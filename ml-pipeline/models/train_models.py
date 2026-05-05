"""
Model Training Module

Trains RF, GB, LR in parallel using Joblib process pool (NFR: Process Pool Parallelization).
Implements Continue-on-Error pattern: failed models are logged and skipped.
Voting Classifier requires at least 2 successful base models (RULE-EH-003).
"""

import sys
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from joblib import Parallel, delayed

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

logger = setup_logger()


def _train_model_wrapper(model_name, model_class, params, X_train, y_train):
    """
    Train a single model with cross-validation.
    Returns (model_name, model, cv_scores, error).
    Designed for joblib parallel execution.
    """
    try:
        logger.info(f"Training {model_name}...")
        model = model_class(**params)

        # Stratified K-Fold cross-validation (RULE-MT-002)
        cv = StratifiedKFold(
            n_splits=Config.CV_FOLDS,
            shuffle=True,
            random_state=Config.RANDOM_SEED
        )
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1', n_jobs=-1)

        # Train on full training set
        model.fit(X_train, y_train)

        logger.info(
            f"{model_name} trained. CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
        )
        return model_name, model, cv_scores, None

    except Exception as e:
        logger.error(f"{model_name} training failed: {e}", exc_info=True)
        return model_name, None, None, str(e)


def train_all_models(X_train, y_train):
    """
    Train all base models in parallel, then build Voting Classifier.

    Implements:
    - Process Pool Parallelization (NFR pattern 2.1)
    - Continue-on-Error (NFR pattern 1.3)
    - Partial Result Persistence (NFR pattern 1.4)

    Args:
        X_train: Training features (engineered)
        y_train: Training labels

    Returns:
        tuple: (models_dict, cv_scores_dict, errors_dict)
    """
    base_configs = [
        ('random_forest', RandomForestClassifier, Config.get_rf_params()),
        ('gradient_boosting', GradientBoostingClassifier, Config.get_gb_params()),
        ('logistic_regression', LogisticRegression, Config.get_lr_params()),
    ]

    # Parallel training with process pool backend (NFR: Process Pool Parallelization)
    results = Parallel(n_jobs=-1, backend='multiprocessing')(
        delayed(_train_model_wrapper)(name, cls, params, X_train, y_train)
        for name, cls, params in base_configs
    )

    models, cv_scores, errors = {}, {}, {}
    for name, model, scores, error in results:
        if model is not None:
            models[name] = model
            cv_scores[name] = scores
        else:
            errors[name] = error

    # Voting Classifier requires at least 2 base models (RULE-EH-003)
    if len(models) >= 2:
        try:
            estimators = [(name, m) for name, m in models.items()]
            # Soft voting — average probabilities (RULE-MT-004)
            voting_clf = VotingClassifier(estimators=estimators, voting='soft', n_jobs=-1)

            cv = StratifiedKFold(
                n_splits=Config.CV_FOLDS,
                shuffle=True,
                random_state=Config.RANDOM_SEED
            )
            vc_scores = cross_val_score(voting_clf, X_train, y_train, cv=cv, scoring='f1', n_jobs=-1)
            voting_clf.fit(X_train, y_train)

            models['voting_classifier'] = voting_clf
            cv_scores['voting_classifier'] = vc_scores
            logger.info(
                f"voting_classifier trained. CV F1: {vc_scores.mean():.4f} ± {vc_scores.std():.4f}"
            )
        except Exception as e:
            errors['voting_classifier'] = str(e)
            logger.error(f"Voting Classifier training failed: {e}", exc_info=True)
    else:
        msg = f"Insufficient base models ({len(models)}) for Voting Classifier, skipping"
        errors['voting_classifier'] = msg
        logger.warning(msg)

    # Fail fast if ALL models failed (NFR: Fail-Fast on critical failure)
    if not models:
        logger.critical("All models failed to train")
        raise RuntimeError("All models failed to train")

    logger.info(f"Training complete. Trained: {list(models.keys())}. Errors: {list(errors.keys())}")
    return models, cv_scores, errors
