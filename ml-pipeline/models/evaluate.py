"""
Model Evaluation Module

Computes all 5 required metrics (RULE-ME-001): Accuracy, Precision, Recall, F1-Score, ROC-AUC.
F1-Score is the primary metric for model selection (RULE-ME-002).
Feature importance calculated for tree-based models (RULE-ME-005).
Performance threshold (80% accuracy) validated with warn-and-continue (RULE-ME-003).
"""

import sys
import os
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

logger = setup_logger()

TREE_MODELS = {'random_forest', 'gradient_boosting'}


def calculate_metrics(model, model_name, X_test, y_test, feature_names=None):
    """
    Calculate all evaluation metrics for a model.

    Args:
        model: Trained sklearn model
        model_name (str): Model identifier
        X_test: Test features
        y_test: True labels
        feature_names (list, optional): Feature names for importance

    Returns:
        dict: All metrics including confusion matrix and feature importance
    """
    y_pred = model.predict(X_test)
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, 'predict_proba')
        else y_pred.astype(float)
    )

    metrics = {
        'accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
        'precision': round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        'f1_score': round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob)), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),  # RULE-ME-004
    }

    # Feature importance for tree-based models (RULE-ME-005)
    if model_name in TREE_MODELS and hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        if feature_names and len(feature_names) == len(importances):
            fi = dict(zip(feature_names, [round(float(v), 6) for v in importances]))
            # Sort by importance descending
            metrics['feature_importance'] = dict(
                sorted(fi.items(), key=lambda x: x[1], reverse=True)
            )
        else:
            metrics['feature_importance'] = {
                f'feature_{i}': round(float(v), 6)
                for i, v in enumerate(importances)
            }

    return metrics


def evaluate_all_models(models, X_test, y_test, cv_scores, feature_names=None):
    """
    Evaluate all trained models and log results.

    Args:
        models (dict): Trained models
        X_test: Test features
        y_test: True labels
        cv_scores (dict): Cross-validation scores from training
        feature_names (list, optional): Feature names for importance

    Returns:
        dict: Metrics for each model
    """
    all_metrics = {}

    for name, model in models.items():
        try:
            metrics = calculate_metrics(model, name, X_test, y_test, feature_names)

            # Attach CV scores
            if name in cv_scores and cv_scores[name] is not None:
                metrics['cv_f1_mean'] = round(float(np.mean(cv_scores[name])), 4)
                metrics['cv_f1_std'] = round(float(np.std(cv_scores[name])), 4)

            # Performance threshold validation — warn-and-continue (RULE-ME-003, NFR pattern 1.5)
            if metrics['accuracy'] < Config.ACCURACY_THRESHOLD:
                logger.warning(
                    f"{name} accuracy {metrics['accuracy']:.4f} below "
                    f"{Config.ACCURACY_THRESHOLD} threshold. Saving anyway."
                )
                metrics['performance_threshold_met'] = False
            else:
                metrics['performance_threshold_met'] = True

            all_metrics[name] = metrics
            logger.info(
                f"{name}: acc={metrics['accuracy']:.4f}, "
                f"f1={metrics['f1_score']:.4f}, "
                f"roc_auc={metrics['roc_auc']:.4f}, "
                f"threshold={'PASS' if metrics['performance_threshold_met'] else 'FAIL'}"
            )

        except Exception as e:
            logger.error(f"Evaluation failed for {name}: {e}", exc_info=True)

    return all_metrics


def get_best_model(metrics_dict):
    """
    Return name of best model by F1-Score (primary), then Accuracy, then ROC-AUC (RULE-ME-002).

    Args:
        metrics_dict (dict): Model metrics

    Returns:
        str: Name of best model
    """
    return max(
        metrics_dict,
        key=lambda k: (
            metrics_dict[k].get('f1_score', 0),
            metrics_dict[k].get('accuracy', 0),
            metrics_dict[k].get('roc_auc', 0)
        )
    )
