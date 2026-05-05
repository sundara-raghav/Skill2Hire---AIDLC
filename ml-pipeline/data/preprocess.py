"""
Data Preprocessing Module

Handles train-test split, feature scaling, and categorical encoding.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

logger = setup_logger()


def preprocess_data(df: pd.DataFrame):
    """
    Preprocess dataset: train-test split, scaling, encoding.
    
    Args:
        df (pd.DataFrame): Raw dataset
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler, encoder)
    """
    logger.info("Starting data preprocessing")
    
    # Separate features and target
    X = df.drop(['placement_status', 'placement_probability'], axis=1)
    y = df['placement_status']
    
    logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
    
    # Train-test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=1 - Config.TRAIN_TEST_SPLIT,
        random_state=Config.RANDOM_SEED,
        stratify=y
    )
    
    logger.info(f"Train set: {len(X_train)} records ({y_train.sum()} placed)")
    logger.info(f"Test set: {len(X_test)} records ({y_test.sum()} placed)")
    
    # Identify numeric and categorical columns
    numeric_features = ['cgpa', 'aptitude_score', 'programming_skills',
                        'communication_skills', 'num_projects', 'certifications_count']
    categorical_features = ['branch']
    
    # Feature scaling (MinMaxScaler)
    logger.info("Applying MinMaxScaler to numeric features")
    scaler = MinMaxScaler()
    X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
    X_test[numeric_features] = scaler.transform(X_test[numeric_features])
    
    # Categorical encoding (OneHotEncoder)
    logger.info("Applying OneHotEncoder to categorical features")
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    
    branch_encoded_train = encoder.fit_transform(X_train[categorical_features])
    branch_encoded_test = encoder.transform(X_test[categorical_features])
    
    # Create column names for encoded features
    branch_columns = [f'branch_{cat}' for cat in encoder.categories_[0]]
    
    # Add encoded columns to datasets
    X_train_encoded = pd.concat([
        X_train.drop(categorical_features, axis=1).reset_index(drop=True),
        pd.DataFrame(branch_encoded_train, columns=branch_columns)
    ], axis=1)
    
    X_test_encoded = pd.concat([
        X_test.drop(categorical_features, axis=1).reset_index(drop=True),
        pd.DataFrame(branch_encoded_test, columns=branch_columns)
    ], axis=1)
    
    logger.info(f"Preprocessed features shape: {X_train_encoded.shape}")
    logger.info(f"Feature columns: {list(X_train_encoded.columns)}")
    
    return (
        X_train_encoded, X_test_encoded,
        y_train.reset_index(drop=True), y_test.reset_index(drop=True),
        scaler, encoder
    )


def save_preprocessing_artifacts(scaler, encoder, version, model_dir):
    """
    Save scaler and encoder for use in Backend inference.
    
    Args:
        scaler: Fitted MinMaxScaler
        encoder: Fitted OneHotEncoder
        version (str): Version identifier
        model_dir (str): Directory to save artifacts
    """
    os.makedirs(model_dir, exist_ok=True)
    
    scaler_path = os.path.join(model_dir, f'scaler_{version}.pkl')
    encoder_path = os.path.join(model_dir, f'encoder_{version}.pkl')
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    logger.info(f"Saved scaler to {scaler_path}")
    
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoder, f)
    logger.info(f"Saved encoder to {encoder_path}")
