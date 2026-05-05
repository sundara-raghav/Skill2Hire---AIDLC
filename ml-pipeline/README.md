# ML Pipeline - Skill2Hire Placement Prediction

## Overview

Complete machine learning pipeline for generating synthetic student data, training ensemble models, and predicting placement probability.

## Features

- **Synthetic Dataset Generation**: Generate 1000+ balanced student records
- **Data Preprocessing**: Scaling, encoding, train-test split
- **Feature Engineering**: 3 derived features for enhanced predictions
- **Ensemble Learning**: Random Forest, Gradient Boosting, Logistic Regression, Voting Classifier
- **Model Evaluation**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Model Versioning**: Sequential versioning with Git LFS
- **Parallel Training**: Joblib multiprocessing for faster training

## Requirements

- Python 3.9+
- See `requirements.txt` for dependencies

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Train Models

```bash
python train.py
```

This will:
1. Generate synthetic dataset (1000 records)
2. Preprocess data (scaling, encoding)
3. Engineer features (derived features)
4. Train 4 models in parallel
5. Evaluate models
6. Save models to `models/trained/`
7. Generate evaluation report

### Configuration

Edit `config.py` or set environment variables:

```bash
export DATASET_SIZE=1000
export RANDOM_SEED=42
export ACCURACY_THRESHOLD=0.80
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_data_generation.py
```

## Directory Structure

```
ml-pipeline/
├── data/                   # Data generation and preprocessing
│   ├── generate_dataset.py
│   ├── preprocess.py
│   └── feature_engineer.py
├── models/                 # Model training and evaluation
│   ├── train_models.py
│   ├── evaluate.py
│   ├── save_models.py
│   ├── generate_report.py
│   └── trained/            # Saved models (.pkl)
├── utils/                  # Utilities
│   ├── skill_dictionary.py
│   ├── validation.py
│   └── logger.py
├── tests/                  # Unit and integration tests
├── logs/                   # Training logs
├── reports/                # Evaluation reports
├── config.py               # Configuration
├── train.py                # Main training script
└── requirements.txt        # Dependencies
```

## Model Outputs

### Trained Models
- `random_forest_v1.pkl`
- `gradient_boosting_v1.pkl`
- `logistic_regression_v1.pkl`
- `voting_classifier_v1.pkl`

### Preprocessing Artifacts
- `scaler_v1.pkl` (MinMaxScaler)
- `encoder_v1.pkl` (OneHotEncoder)

### Metrics
- `*_v1_metrics.json` (JSON format)

### Reports
- `evaluation_report_v1.md` (Markdown format)

## Performance

- **Training Time**: < 1 minute (all 4 models)
- **Dataset Size**: 1000 records
- **Accuracy Target**: ≥ 80%
- **Parallelization**: Joblib (n_jobs=-1)

## CI/CD

Training is automated via GitHub Actions:
- **Trigger**: Push to main, daily schedule, manual
- **Workflow**: `.github/workflows/ml-pipeline.yml`
- **Artifacts**: Logs and reports (90-day retention)

## Versioning

Models are versioned sequentially (v1, v2, v3, ...) and tracked with Git LFS.

## License

MIT License

## Contact

Skill2Hire Team
