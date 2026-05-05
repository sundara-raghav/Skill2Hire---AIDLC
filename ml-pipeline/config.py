"""
Configuration module for ML Pipeline.

This module defines all configuration parameters for dataset generation,
preprocessing, model training, and evaluation.
"""

import os

_ML_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_ML_PIPELINE_DIR)


class Config:
    """ML Pipeline configuration parameters."""
    
    # Dataset Configuration
    DATASET_SIZE = int(os.getenv('DATASET_SIZE', 1000))
    RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
    TRAIN_TEST_SPLIT = float(os.getenv('TRAIN_TEST_SPLIT', 0.80))
    
    # Data Generation Parameters
    CGPA_MEAN = 7.0
    CGPA_STD = 1.2
    APTITUDE_MEAN = 70
    APTITUDE_STD = 15
    PROJECTS_LAMBDA = 2.5
    CERTIFICATIONS_LAMBDA = 1.5
    INTERNSHIP_BASE_PROB = 0.4
    
    # Branch Distribution
    BRANCH_DISTRIBUTION = {
        'CS': 0.25,
        'IT': 0.20,
        'ECE': 0.15,
        'EEE': 0.12,
        'Mechanical': 0.10,
        'Civil': 0.08,
        'Chemical': 0.05,
        'Other': 0.05
    }
    
    # Placement Probability Weights
    PLACEMENT_WEIGHTS = {
        'cgpa': 0.25,
        'aptitude': 0.20,
        'programming': 0.20,
        'communication': 0.10,
        'projects': 0.10,
        'internship': 0.10,
        'certifications': 0.05
    }
    
    # Cross-Validation Configuration
    CV_FOLDS = int(os.getenv('CV_FOLDS', 5))
    
    # Model Hyperparameters
    # Random Forest
    RF_N_ESTIMATORS = int(os.getenv('RF_N_ESTIMATORS', 100))
    RF_MAX_DEPTH = int(os.getenv('RF_MAX_DEPTH', 10))
    RF_MIN_SAMPLES_SPLIT = int(os.getenv('RF_MIN_SAMPLES_SPLIT', 5))
    RF_MIN_SAMPLES_LEAF = int(os.getenv('RF_MIN_SAMPLES_LEAF', 2))
    RF_MAX_FEATURES = os.getenv('RF_MAX_FEATURES', 'sqrt')
    
    # Gradient Boosting
    GB_N_ESTIMATORS = int(os.getenv('GB_N_ESTIMATORS', 100))
    GB_LEARNING_RATE = float(os.getenv('GB_LEARNING_RATE', 0.1))
    GB_MAX_DEPTH = int(os.getenv('GB_MAX_DEPTH', 5))
    GB_MIN_SAMPLES_SPLIT = int(os.getenv('GB_MIN_SAMPLES_SPLIT', 5))
    GB_MIN_SAMPLES_LEAF = int(os.getenv('GB_MIN_SAMPLES_LEAF', 2))
    GB_SUBSAMPLE = float(os.getenv('GB_SUBSAMPLE', 0.8))
    
    # Logistic Regression
    LR_C = float(os.getenv('LR_C', 1.0))
    LR_PENALTY = os.getenv('LR_PENALTY', 'l2')
    LR_SOLVER = os.getenv('LR_SOLVER', 'lbfgs')
    LR_MAX_ITER = int(os.getenv('LR_MAX_ITER', 1000))
    
    # Performance Thresholds
    ACCURACY_THRESHOLD = float(os.getenv('ACCURACY_THRESHOLD', 0.80))
    
    # Paths (absolute, relative to ml-pipeline/ directory)
    DATA_DIR = os.path.join(_ML_PIPELINE_DIR, 'data')
    MODEL_DIR = os.path.join(_ML_PIPELINE_DIR, 'models', 'trained')
    LOG_DIR = os.path.join(_ML_PIPELINE_DIR, 'logs')
    REPORT_DIR = os.path.join(_ML_PIPELINE_DIR, 'reports')
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    @classmethod
    def get_rf_params(cls):
        """Get Random Forest hyperparameters."""
        return {
            'n_estimators': cls.RF_N_ESTIMATORS,
            'max_depth': cls.RF_MAX_DEPTH,
            'min_samples_split': cls.RF_MIN_SAMPLES_SPLIT,
            'min_samples_leaf': cls.RF_MIN_SAMPLES_LEAF,
            'max_features': cls.RF_MAX_FEATURES,
            'random_state': cls.RANDOM_SEED,
            'n_jobs': -1
        }
    
    @classmethod
    def get_gb_params(cls):
        """Get Gradient Boosting hyperparameters."""
        return {
            'n_estimators': cls.GB_N_ESTIMATORS,
            'learning_rate': cls.GB_LEARNING_RATE,
            'max_depth': cls.GB_MAX_DEPTH,
            'min_samples_split': cls.GB_MIN_SAMPLES_SPLIT,
            'min_samples_leaf': cls.GB_MIN_SAMPLES_LEAF,
            'subsample': cls.GB_SUBSAMPLE,
            'random_state': cls.RANDOM_SEED
        }
    
    @classmethod
    def get_lr_params(cls):
        """Get Logistic Regression hyperparameters."""
        return {
            'C': cls.LR_C,
            'penalty': cls.LR_PENALTY,
            'solver': cls.LR_SOLVER,
            'max_iter': cls.LR_MAX_ITER,
            'random_state': cls.RANDOM_SEED
        }
