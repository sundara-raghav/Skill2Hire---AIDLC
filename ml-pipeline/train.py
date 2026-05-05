"""
Main Training Script

Orchestrates the complete ML pipeline: dataset generation, preprocessing,
feature engineering, model training, evaluation, versioning, and reporting.
"""

import sys
import os
import random
import argparse
from datetime import datetime

import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.logger import setup_logger, log_section_header
from utils.validation import validate_environment
from data.generate_dataset import generate_dataset_with_retry
from data.preprocess import preprocess_data, save_preprocessing_artifacts
from data.feature_engineer import engineer_features
from models.train_models import train_all_models
from models.evaluate import evaluate_all_models, get_best_model
from models.save_models import get_next_version, save_all_models
from models.generate_report import generate_evaluation_report

logger = setup_logger()


def main():
    """Main training pipeline execution."""
    try:
        log_section_header(logger, "ML PIPELINE TRAINING STARTED")
        start_time = datetime.now()

        # Dual seed propagation (NFR: critical reproducibility)
        random.seed(Config.RANDOM_SEED)
        np.random.seed(Config.RANDOM_SEED)
        logger.info(f"Global random seeds set to {Config.RANDOM_SEED}")

        # Step 1: Validate environment
        log_section_header(logger, "Step 1: Environment Validation")
        validate_environment()
        logger.info("All required dependencies are installed")

        # Step 2: Generate dataset
        log_section_header(logger, "Step 2: Dataset Generation")
        dataset = generate_dataset_with_retry(
            target_size=Config.DATASET_SIZE,
            max_retries=Config.MAX_RETRIES,
            base_seed=Config.RANDOM_SEED
        )
        logger.info(f"Dataset generated: {len(dataset)} records")

        os.makedirs(Config.DATA_DIR, exist_ok=True)
        dataset_path = os.path.join(Config.DATA_DIR, 'training_dataset.csv')
        dataset.to_csv(dataset_path, index=False)
        logger.info(f"Dataset saved to {dataset_path} ({len(dataset)} records)")

        # Step 3: Preprocess data
        log_section_header(logger, "Step 3: Data Preprocessing")
        X_train, X_test, y_train, y_test, scaler, encoder = preprocess_data(dataset)
        logger.info(f"Preprocessing complete. Train: {len(X_train)}, Test: {len(X_test)}")

        # Step 4: Engineer features
        log_section_header(logger, "Step 4: Feature Engineering")
        X_train_eng, X_test_eng = engineer_features(X_train, X_test)
        logger.info(f"Feature engineering complete. Features: {X_train_eng.shape[1]}")

        # Step 5: Train models
        log_section_header(logger, "Step 5: Model Training")
        models, cv_scores, train_errors = train_all_models(X_train_eng, y_train)
        if train_errors:
            logger.warning(f"Some models failed to train: {train_errors}")
        if not models:
            raise RuntimeError("All models failed to train")
        logger.info(f"Trained {len(models)} models: {list(models.keys())}")

        # Step 6: Evaluate models
        log_section_header(logger, "Step 6: Model Evaluation")
        feature_names = list(X_train_eng.columns)
        metrics = evaluate_all_models(models, X_test_eng, y_test, cv_scores,
                                      feature_names=feature_names)
        best_model = get_best_model(metrics)
        logger.info(f"Best model by F1-Score: {best_model}")

        # Step 7: Save models and artifacts
        log_section_header(logger, "Step 7: Model Persistence")
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        version = get_next_version(Config.MODEL_DIR)
        save_preprocessing_artifacts(scaler, encoder, version, Config.MODEL_DIR)
        dataset_info = {
            'total_records': len(dataset),
            'train_records': len(X_train),
            'test_records': len(X_test),
            'features_count': X_train_eng.shape[1],
            'feature_names': list(X_train_eng.columns)
        }
        training_duration = (datetime.now() - start_time).total_seconds()
        save_all_models(models, metrics, version, Config.MODEL_DIR,
                        dataset_info=dataset_info, training_duration=training_duration)
        logger.info(f"All models saved as version {version}")

        # Step 8: Generate report
        log_section_header(logger, "Step 8: Report Generation")
        duration = (datetime.now() - start_time).total_seconds()
        generate_evaluation_report(
            metrics=metrics,
            version=version,
            dataset_size=len(dataset),
            duration=duration,
            report_dir=Config.REPORT_DIR
        )

        log_section_header(logger, "ML PIPELINE TRAINING COMPLETED")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Version: {version} | Best model: {best_model}")
        logger.info(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        logger.critical(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ML Pipeline Training')
    parser.add_argument('--seed', type=int, default=Config.RANDOM_SEED)
    parser.add_argument('--size', type=int, default=Config.DATASET_SIZE)
    args = parser.parse_args()

    Config.RANDOM_SEED = args.seed
    Config.DATASET_SIZE = args.size

    main()
