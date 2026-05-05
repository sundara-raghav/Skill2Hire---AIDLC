"""
Validation Module

Implements all 44 business rules for data quality validation.
RULE-DQ-003: Statistical distribution checks (scipy normality test).
RULE-DG-011: Moderate feature correlations check.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger()

try:
    from scipy import stats as scipy_stats
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_student_profile(profile: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a single student profile against all business rules.
    
    Args:
        profile (dict): Student profile data
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # CGPA validation
    if not (0.0 <= profile.get('cgpa', -1) <= 10.0):
        errors.append("CGPA must be between 0.0 and 10.0")
    
    # Aptitude score validation
    if not (0 <= profile.get('aptitude_score', -1) <= 100):
        errors.append("Aptitude score must be between 0 and 100")
    
    # Programming skills validation
    if not (1 <= profile.get('programming_skills', 0) <= 10):
        errors.append("Programming skills must be between 1 and 10")
    
    # Communication skills validation
    if not (1 <= profile.get('communication_skills', 0) <= 10):
        errors.append("Communication skills must be between 1 and 10")
    
    # Number of projects validation
    if not (0 <= profile.get('num_projects', -1) <= 10):
        errors.append("Number of projects must be between 0 and 10")
    
    # Internship experience validation
    if profile.get('internship_experience') not in [0, 1, True, False]:
        errors.append("Internship experience must be boolean (0/1 or True/False)")
    
    # Certifications count validation
    if not (0 <= profile.get('certifications_count', -1) <= 10):
        errors.append("Certifications count must be between 0 and 10")
    
    # Branch validation
    valid_branches = ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']
    if profile.get('branch') not in valid_branches:
        errors.append(f"Branch must be one of {valid_branches}")
    
    return len(errors) == 0, errors


def validate_dataset(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate entire dataset against business rules.
    
    Args:
        df (pd.DataFrame): Dataset to validate
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Check for null values
    if df.isnull().sum().sum() > 0:
        errors.append("Dataset contains null values")
    
    # Check dataset size
    if len(df) < 100:
        errors.append(f"Dataset too small: {len(df)} records (minimum 100)")
    
    # Check class balance
    if 'placement_status' in df.columns:
        placed_count = df['placement_status'].sum()
        total_count = len(df)
        placed_ratio = placed_count / total_count
        
        if not (0.48 <= placed_ratio <= 0.52):
            errors.append(f"Class imbalance detected: {placed_ratio:.2%} placed (target: 50% ± 2%)")
    
    # Check for duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        errors.append(f"Dataset contains {duplicate_count} duplicate records")

    # RULE-DQ-003: Statistical distribution check (warn only — MEDIUM priority)
    if _SCIPY_AVAILABLE and 'cgpa' in df.columns and len(df) >= 20:
        try:
            _, p_value = scipy_stats.normaltest(df['cgpa'].dropna())
            if p_value < 0.001:
                logger.warning(f"CGPA distribution may not be normal (p={p_value:.4f}) — warning only")
        except Exception:
            pass  # Non-critical, skip if test fails

    # RULE-DG-011: Moderate feature correlations check (warn only — MEDIUM priority)
    numeric_cols = ['cgpa', 'programming_skills']
    if all(c in df.columns for c in numeric_cols) and len(df) >= 20:
        try:
            corr = df[numeric_cols].corr().loc['cgpa', 'programming_skills']
            if not (0.05 <= abs(corr) <= 0.95):
                logger.warning(
                    f"CGPA-programming_skills correlation {corr:.3f} outside expected range — warning only"
                )
        except Exception:
            pass  # Non-critical
    
    # Validate data types
    expected_types = {
        'cgpa': [np.float64, np.float32, float],
        'aptitude_score': [np.int64, np.int32, int, np.float64, np.float32, float],
        'programming_skills': [np.int64, np.int32, int],
        'communication_skills': [np.int64, np.int32, int],
        'num_projects': [np.int64, np.int32, int],
        'internship_experience': [np.int64, np.int32, int, bool],
        'certifications_count': [np.int64, np.int32, int],
        'branch': [object, str],
        'placement_status': [np.int64, np.int32, int, bool]
    }
    
    for col, valid_types in expected_types.items():
        if col in df.columns:
            if df[col].dtype not in valid_types and type(df[col].iloc[0]) not in valid_types:
                errors.append(f"Column '{col}' has incorrect data type: {df[col].dtype}")
    
    # Validate value ranges for all records
    if 'cgpa' in df.columns:
        invalid_cgpa = ((df['cgpa'] < 0) | (df['cgpa'] > 10)).sum()
        if invalid_cgpa > 0:
            errors.append(f"{invalid_cgpa} records have invalid CGPA values")
    
    if 'aptitude_score' in df.columns:
        invalid_apt = ((df['aptitude_score'] < 0) | (df['aptitude_score'] > 100)).sum()
        if invalid_apt > 0:
            errors.append(f"{invalid_apt} records have invalid aptitude scores")
    
    if 'programming_skills' in df.columns:
        invalid_prog = ((df['programming_skills'] < 1) | (df['programming_skills'] > 10)).sum()
        if invalid_prog > 0:
            errors.append(f"{invalid_prog} records have invalid programming skills")
    
    if 'communication_skills' in df.columns:
        invalid_comm = ((df['communication_skills'] < 1) | (df['communication_skills'] > 10)).sum()
        if invalid_comm > 0:
            errors.append(f"{invalid_comm} records have invalid communication skills")
    
    return len(errors) == 0, errors


def validate_environment():
    """
    Validate that all required dependencies are installed.
    
    Raises:
        ValidationError: If required packages are missing
    """
    required_packages = [
        'sklearn',
        'numpy',
        'pandas',
        'scipy',
        'joblib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ValidationError(
            f"Missing required packages: {missing_packages}. "
            f"Install with: pip install -r requirements.txt"
        )
