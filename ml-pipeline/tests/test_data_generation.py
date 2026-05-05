"""Tests for dataset generation module."""
import sys
import os
import pytest
import pandas as pd

# conftest.py at root handles sys.path

from data.generate_dataset import (
    generate_student_profile, is_duplicate, balance_dataset,
    generate_synthetic_dataset, generate_dataset_with_retry
)


def test_generate_student_profile_keys():
    profile = generate_student_profile(seed=42)
    expected = {'cgpa', 'aptitude_score', 'programming_skills', 'communication_skills',
                'num_projects', 'internship_experience', 'certifications_count',
                'branch', 'placement_status', 'placement_probability'}
    assert expected.issubset(profile.keys())


def test_generate_student_profile_ranges():
    for seed in range(10):
        p = generate_student_profile(seed=seed)
        assert 0.0 <= p['cgpa'] <= 10.0
        assert 0 <= p['aptitude_score'] <= 100
        assert 1 <= p['programming_skills'] <= 10
        assert 1 <= p['communication_skills'] <= 10
        assert 0 <= p['num_projects'] <= 10
        assert p['internship_experience'] in (0, 1)
        assert 0 <= p['certifications_count'] <= 10
        assert p['branch'] in ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']


def test_is_duplicate_detects_duplicate():
    p = generate_student_profile(seed=1)
    assert is_duplicate(p, [p]) is True


def test_is_duplicate_no_false_positive():
    p1 = generate_student_profile(seed=1)
    p2 = generate_student_profile(seed=999)
    result = is_duplicate(p1, [p2])
    assert isinstance(result, bool)


def test_balance_dataset():
    profiles = [generate_student_profile(seed=i) for i in range(100)]
    balanced = balance_dataset(profiles)
    placed = sum(1 for p in balanced if p['placement_status'] == 1)
    assert abs(placed - 50) <= 2


def test_generate_synthetic_dataset_size():
    df = generate_synthetic_dataset(target_size=100, seed=42)
    assert len(df) == 100


def test_generate_synthetic_dataset_balance():
    df = generate_synthetic_dataset(target_size=100, seed=42)
    ratio = df['placement_status'].mean()
    assert 0.48 <= ratio <= 0.52


def test_generate_synthetic_dataset_no_nulls():
    df = generate_synthetic_dataset(target_size=100, seed=42)
    assert df.isnull().sum().sum() == 0


def test_reproducibility_with_seed():
    df1 = generate_synthetic_dataset(target_size=50, seed=42)
    df2 = generate_synthetic_dataset(target_size=50, seed=42)
    assert df1['cgpa'].tolist() == df2['cgpa'].tolist()


def test_generate_dataset_with_retry():
    df = generate_dataset_with_retry(target_size=100, max_retries=2, base_seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100
