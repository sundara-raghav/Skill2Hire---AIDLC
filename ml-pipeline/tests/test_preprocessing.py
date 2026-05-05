"""Tests for data preprocessing module."""
import sys
import os
import pickle
import tempfile
import pytest

# conftest.py at root handles sys.path

from data.generate_dataset import generate_synthetic_dataset
from data.preprocess import preprocess_data, save_preprocessing_artifacts


@pytest.fixture(scope='module')
def dataset():
    return generate_synthetic_dataset(target_size=200, seed=42)


@pytest.fixture(scope='module')
def preprocessed(dataset):
    return preprocess_data(dataset)


def test_split_ratio(preprocessed):
    X_train, X_test, y_train, y_test, _, _ = preprocessed
    total = len(X_train) + len(X_test)
    assert abs(len(X_train) / total - 0.80) < 0.02


def test_stratification(preprocessed):
    _, _, y_train, y_test, _, _ = preprocessed
    train_ratio = y_train.mean()
    test_ratio = y_test.mean()
    assert abs(train_ratio - test_ratio) < 0.05


def test_minmax_scaling(preprocessed):
    X_train, _, _, _, scaler, _ = preprocessed
    numeric = ['cgpa', 'aptitude_score', 'programming_skills',
               'communication_skills', 'num_projects', 'certifications_count']
    for col in numeric:
        assert X_train[col].min() >= -0.01
        assert X_train[col].max() <= 1.01


def test_onehot_encoding(preprocessed):
    X_train, _, _, _, _, _ = preprocessed
    branch_cols = [c for c in X_train.columns if c.startswith('branch_')]
    assert len(branch_cols) > 0
    assert 'branch' not in X_train.columns


def test_no_data_leakage(preprocessed):
    _, _, _, _, scaler, _ = preprocessed
    assert hasattr(scaler, 'data_min_')


def test_save_load_artifacts(preprocessed):
    _, _, _, _, scaler, encoder = preprocessed
    with tempfile.TemporaryDirectory() as tmpdir:
        save_preprocessing_artifacts(scaler, encoder, 'vtest', tmpdir)
        scaler_path = os.path.join(tmpdir, 'scaler_vtest.pkl')
        encoder_path = os.path.join(tmpdir, 'encoder_vtest.pkl')
        assert os.path.exists(scaler_path)
        assert os.path.exists(encoder_path)
        with open(scaler_path, 'rb') as f:
            loaded_scaler = pickle.load(f)
        assert hasattr(loaded_scaler, 'transform')
