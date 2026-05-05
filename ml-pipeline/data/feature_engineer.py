"""
Feature Engineering Module

Creates derived features to enhance model performance.
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

logger = setup_logger()


def engineer_features(X_train: pd.DataFrame, X_test: pd.DataFrame):
    """
    Create derived features for both train and test sets.
    
    Derived Features:
    1. Total_Skills_Score = Programming_Skills + Communication_Skills
    2. Experience_Score = (Num_Projects * 0.4) + (Internship_Experience * 0.6)
    3. CGPA_Project_Score = CGPA * Num_Projects
    
    Args:
        X_train (pd.DataFrame): Training features
        X_test (pd.DataFrame): Test features
    
    Returns:
        tuple: (X_train_engineered, X_test_engineered)
    """
    logger.info("Engineering derived features")
    
    # Create copies to avoid modifying originals
    X_train_eng = X_train.copy()
    X_test_eng = X_test.copy()
    
    # Feature 1: Total_Skills_Score
    X_train_eng['Total_Skills_Score'] = (
        X_train_eng['programming_skills'] + X_train_eng['communication_skills']
    )
    X_test_eng['Total_Skills_Score'] = (
        X_test_eng['programming_skills'] + X_test_eng['communication_skills']
    )
    
    # Feature 2: Experience_Score
    X_train_eng['Experience_Score'] = (
        X_train_eng['num_projects'] * 0.4 + X_train_eng['internship_experience'] * 0.6
    )
    X_test_eng['Experience_Score'] = (
        X_test_eng['num_projects'] * 0.4 + X_test_eng['internship_experience'] * 0.6
    )
    
    # Feature 3: CGPA_Project_Score
    X_train_eng['CGPA_Project_Score'] = (
        X_train_eng['cgpa'] * X_train_eng['num_projects']
    )
    X_test_eng['CGPA_Project_Score'] = (
        X_test_eng['cgpa'] * X_test_eng['num_projects']
    )
    
    logger.info(f"Added 3 derived features. New shape: {X_train_eng.shape}")
    logger.info(f"Feature columns: {list(X_train_eng.columns)}")
    
    return X_train_eng, X_test_eng
