"""Integration tests for the full ML pipeline."""
import sys
import os
import tempfile
import pytest

# conftest.py at root handles sys.path

from data.generate_dataset import generate_dataset_with_retry
from data.preprocess import preprocess_data, save_preprocessing_artifacts
from data.feature_engineer import engineer_features
from models.train_models import train_all_models
from models.evaluate import evaluate_all_models, get_best_model
from models.save_models import get_next_version, save_all_models
from models.generate_report import generate_evaluation_report


def test_end_to_end_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        model_dir = os.path.join(tmpdir, 'models')
        report_dir = os.path.join(tmpdir, 'reports')

        df = generate_dataset_with_retry(target_size=200, max_retries=2, base_seed=42)
        assert len(df) >= 200

        X_train, X_test, y_train, y_test, scaler, encoder = preprocess_data(df)
        X_train_eng, X_test_eng = engineer_features(X_train, X_test)

        models, cv_scores, errors = train_all_models(X_train_eng, y_train)
        assert len(models) >= 3

        metrics = evaluate_all_models(models, X_test_eng, y_test, cv_scores,
                                      feature_names=list(X_train_eng.columns))
        best = get_best_model(metrics)
        assert best in metrics

        version = get_next_version(model_dir)
        assert version == 'v1'
        save_preprocessing_artifacts(scaler, encoder, version, model_dir)
        dataset_info = {
            'total_records': len(df),
            'train_records': len(X_train_eng),
            'test_records': len(X_test_eng),
            'features_count': X_train_eng.shape[1],
            'feature_names': list(X_train_eng.columns)
        }
        saved = save_all_models(models, metrics, version, model_dir,
                                dataset_info=dataset_info, training_duration=5.0)
        assert len(saved) == len(models)

        for name in models:
            assert os.path.exists(os.path.join(model_dir, f'{name}_{version}.pkl'))

        report_path = generate_evaluation_report(
            metrics=metrics, version=version,
            dataset_size=len(df), duration=10.0,
            report_dir=report_dir
        )
        assert os.path.exists(report_path)
        with open(report_path) as f:
            content = f.read()
        assert 'Model Comparison' in content


def test_reproducibility():
    df1 = generate_dataset_with_retry(target_size=100, max_retries=1, base_seed=42)
    df2 = generate_dataset_with_retry(target_size=100, max_retries=1, base_seed=42)
    assert df1['cgpa'].tolist() == df2['cgpa'].tolist()
