"""Tests for model training module."""
import sys
import os
import pytest

# conftest.py at root handles sys.path

from data.generate_dataset import generate_synthetic_dataset
from data.preprocess import preprocess_data
from data.feature_engineer import engineer_features
from models.train_models import train_all_models


@pytest.fixture(scope='module')
def training_data():
    df = generate_synthetic_dataset(target_size=300, seed=42)
    X_train, X_test, y_train, y_test, _, _ = preprocess_data(df)
    X_train_eng, X_test_eng = engineer_features(X_train, X_test)
    return X_train_eng, X_test_eng, y_train, y_test


def test_all_models_trained(training_data):
    X_train, _, y_train, _ = training_data
    models, cv_scores, errors = train_all_models(X_train, y_train)
    assert len(models) >= 3


def test_voting_classifier_trained(training_data):
    X_train, _, y_train, _ = training_data
    models, _, _ = train_all_models(X_train, y_train)
    assert 'voting_classifier' in models


def test_cv_scores_present(training_data):
    X_train, _, y_train, _ = training_data
    _, cv_scores, _ = train_all_models(X_train, y_train)
    for name, scores in cv_scores.items():
        assert len(scores) == 5
        assert all(0 <= s <= 1 for s in scores)


def test_models_can_predict(training_data):
    X_train, X_test, y_train, _ = training_data
    models, _, _ = train_all_models(X_train, y_train)
    for name, model in models.items():
        preds = model.predict(X_test)
        assert len(preds) == len(X_test)
        assert set(preds).issubset({0, 1})
