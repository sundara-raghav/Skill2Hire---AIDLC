"""Tests for model evaluation module."""
import sys
import os
import pytest

# conftest.py at root handles sys.path

from data.generate_dataset import generate_synthetic_dataset
from data.preprocess import preprocess_data
from data.feature_engineer import engineer_features
from models.train_models import train_all_models
from models.evaluate import calculate_metrics, evaluate_all_models, get_best_model


@pytest.fixture(scope='module')
def trained():
    df = generate_synthetic_dataset(target_size=300, seed=42)
    X_train, X_test, y_train, y_test, _, _ = preprocess_data(df)
    X_train_eng, X_test_eng = engineer_features(X_train, X_test)
    models, cv_scores, _ = train_all_models(X_train_eng, y_train)
    return models, cv_scores, X_test_eng, y_test


def test_calculate_metrics_keys(trained):
    models, _, X_test, y_test = trained
    model = next(iter(models.values()))
    model_name = next(iter(models.keys()))
    metrics = calculate_metrics(model, model_name, X_test, y_test)
    for key in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']:
        assert key in metrics
        assert 0.0 <= metrics[key] <= 1.0


def test_evaluate_all_models(trained):
    models, cv_scores, X_test, y_test = trained
    all_metrics = evaluate_all_models(models, X_test, y_test, cv_scores,
                                      feature_names=list(X_test.columns))
    assert len(all_metrics) == len(models)


def test_get_best_model(trained):
    models, cv_scores, X_test, y_test = trained
    all_metrics = evaluate_all_models(models, X_test, y_test, cv_scores,
                                      feature_names=list(X_test.columns))
    best = get_best_model(all_metrics)
    assert best in all_metrics


def test_accuracy_above_threshold(trained):
    models, cv_scores, X_test, y_test = trained
    all_metrics = evaluate_all_models(models, X_test, y_test, cv_scores,
                                      feature_names=list(X_test.columns))
    assert any(m['accuracy'] >= 0.75 for m in all_metrics.values())
