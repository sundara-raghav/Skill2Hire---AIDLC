"""
Model Persistence Module

Sequential versioning (RULE-MV-001): v1, v2, v3, ...
Metadata required (RULE-MV-002, RULE-MV-003): version, date, metrics, hyperparameters,
dataset_info, feature_names, feature_count, file_size_bytes, scikit-learn version.
Partial Result Persistence (NFR pattern 1.4): save successful models even if some fail.
"""

import sys
import os
import pickle
import json
from datetime import datetime

import sklearn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

logger = setup_logger()


def get_next_version(model_dir):
    """
    Determine next sequential version (v1, v2, ...) — RULE-MV-001.

    Args:
        model_dir (str): Directory containing model files

    Returns:
        str: Next version string (e.g. 'v1')
    """
    os.makedirs(model_dir, exist_ok=True)
    existing = [
        f for f in os.listdir(model_dir)
        if f.startswith('random_forest_v') and f.endswith('.pkl')
    ]
    if not existing:
        return 'v1'
    versions = []
    for f in existing:
        try:
            num = int(f.replace('random_forest_v', '').replace('.pkl', ''))
            versions.append(num)
        except ValueError:
            pass
    return f'v{max(versions) + 1}' if versions else 'v1'


def save_model(model, model_name, version, model_dir):
    """
    Save a single model as .pkl file.

    Args:
        model: Trained sklearn model
        model_name (str): Model identifier
        version (str): Version string
        model_dir (str): Output directory

    Returns:
        str: Path to saved file
    """
    os.makedirs(model_dir, exist_ok=True)
    path = os.path.join(model_dir, f'{model_name}_{version}.pkl')
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Saved {model_name} to {path} ({os.path.getsize(path)} bytes)")
    return path


def save_model_metrics(model_name, version, metrics, model_dir):
    """Save metrics as JSON file (NFR: JSON Metrics Persistence pattern)."""
    path = os.path.join(model_dir, f'{model_name}_{version}_metrics.json')
    with open(path, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved metrics for {model_name} to {path}")


def _build_metadata(model_name, version, metrics, model_path,
                    dataset_info=None, training_duration=None):
    """Build complete metadata dict (RULE-MV-003)."""
    return {
        'model_name': model_name,
        'version': version,
        'training_date': datetime.utcnow().isoformat() + 'Z',
        'training_duration_seconds': round(training_duration, 2) if training_duration else None,
        'dataset_info': dataset_info or {},
        'hyperparameters': _get_hyperparams(model_name),
        'feature_names': dataset_info.get('feature_names', []) if dataset_info else [],
        'feature_count': dataset_info.get('features_count', 0) if dataset_info else 0,
        'scikit_learn_version': sklearn.__version__,
        'python_version': sys.version,
        'file_path': model_path,
        'file_size_bytes': os.path.getsize(model_path) if os.path.exists(model_path) else 0,
        'metrics': metrics,
        'performance_threshold_met': metrics.get('performance_threshold_met', False),
    }


def _get_hyperparams(model_name):
    """Return hyperparameters for a given model name."""
    mapping = {
        'random_forest': Config.get_rf_params(),
        'gradient_boosting': Config.get_gb_params(),
        'logistic_regression': Config.get_lr_params(),
        'voting_classifier': {
            'voting': 'soft',
            'estimators': ['random_forest', 'gradient_boosting', 'logistic_regression']
        },
    }
    return mapping.get(model_name, {})


def save_all_models(models, metrics, version, model_dir,
                    dataset_info=None, training_duration=None):
    """
    Save all models, metrics, and metadata.
    Implements Partial Result Persistence: saves successful models even if some fail.

    Args:
        models (dict): Trained models
        metrics (dict): Evaluation metrics per model
        version (str): Version string
        model_dir (str): Output directory
        dataset_info (dict, optional): Dataset statistics
        training_duration (float, optional): Total training duration in seconds

    Returns:
        dict: Paths to saved model files
    """
    os.makedirs(model_dir, exist_ok=True)
    saved_paths = {}

    for name, model in models.items():
        try:
            # Save model .pkl
            path = save_model(model, name, version, model_dir)
            saved_paths[name] = path

            model_metrics = metrics.get(name, {})

            # Save metrics JSON
            save_model_metrics(name, version, model_metrics, model_dir)

            # Save metadata JSON (RULE-MV-002, RULE-MV-003)
            meta = _build_metadata(
                model_name=name,
                version=version,
                metrics=model_metrics,
                model_path=path,
                dataset_info=dataset_info,
                training_duration=training_duration
            )
            meta_path = os.path.join(model_dir, f'{name}_{version}_metadata.json')
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save {name}: {e}", exc_info=True)

    logger.info(f"Saved {len(saved_paths)}/{len(models)} models as {version}")
    return saved_paths
