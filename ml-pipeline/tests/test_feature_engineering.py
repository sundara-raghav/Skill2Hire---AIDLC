"""Tests for feature engineering module."""
import sys
import os
import pytest

# conftest.py at root handles sys.path

from data.generate_dataset import generate_synthetic_dataset
from data.preprocess import preprocess_data
from data.feature_engineer import engineer_features


@pytest.fixture(scope='module')
def engineered():
    df = generate_synthetic_dataset(target_size=200, seed=42)
    X_train, X_test, _, _, _, _ = preprocess_data(df)
    return engineer_features(X_train, X_test)


def test_feature_count(engineered):
    X_train_eng, _ = engineered
    assert 'Total_Skills_Score' in X_train_eng.columns
    assert 'Experience_Score' in X_train_eng.columns
    assert 'CGPA_Project_Score' in X_train_eng.columns


def test_total_skills_score(engineered):
    X_train_eng, _ = engineered
    expected = X_train_eng['programming_skills'] + X_train_eng['communication_skills']
    assert (X_train_eng['Total_Skills_Score'] - expected).abs().max() < 1e-9


def test_experience_score(engineered):
    X_train_eng, _ = engineered
    expected = X_train_eng['num_projects'] * 0.4 + X_train_eng['internship_experience'] * 0.6
    assert (X_train_eng['Experience_Score'] - expected).abs().max() < 1e-9


def test_cgpa_project_score(engineered):
    X_train_eng, _ = engineered
    expected = X_train_eng['cgpa'] * X_train_eng['num_projects']
    assert (X_train_eng['CGPA_Project_Score'] - expected).abs().max() < 1e-9


def test_applied_to_both_sets(engineered):
    X_train_eng, X_test_eng = engineered
    for col in ['Total_Skills_Score', 'Experience_Score', 'CGPA_Project_Score']:
        assert col in X_train_eng.columns
        assert col in X_test_eng.columns
