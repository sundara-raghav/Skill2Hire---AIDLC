# Logical Components: ML Pipeline Unit

## Overview

This document defines all logical components for the ML Pipeline unit, including infrastructure components, orchestration components, and monitoring components.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## Component Architecture

### Architecture Decision

**Decision**: No additional infrastructure components required

**Rationale**: The ML Pipeline is a simple script-based pipeline with no need for queues, caches, circuit breakers, or other infrastructure components. The pipeline runs sequentially with parallel model training handled by joblib.

**Architecture Style**: Simple Script-Based Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Pipeline (train.py)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Environment Validation                               │ │
│  │    - Check dependencies installed                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 2. Dataset Generation (with retry)                      │ │
│  │    - Generate 1000 synthetic records                    │ │
│  │    - Validate dataset quality                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 3. Data Preprocessing                                   │ │
│  │    - Train-test split (stratified)                      │ │
│  │    - Feature scaling (MinMaxScaler)                     │ │
│  │    - Categorical encoding (OneHotEncoder)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 4. Feature Engineering                                  │ │
│  │    - Create derived features                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 5. Model Training (PARALLEL)                            │ │
│  │    ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│ │
│  │    │ Random Forest│  │ Gradient     │  │ Logistic    ││ │
│  │    │              │  │ Boosting     │  │ Regression  ││ │
│  │    └──────────────┘  └──────────────┘  └─────────────┘│ │
│  │              ↓                ↓                ↓        │ │
│  │    ┌──────────────────────────────────────────────────┐│ │
│  │    │         Voting Classifier (ensemble)             ││ │
│  │    └──────────────────────────────────────────────────┘│ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 6. Model Evaluation                                     │ │
│  │    - Calculate metrics (accuracy, F1, etc.)             │ │
│  │    - Validate quality gates                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 7. Model Persistence                                    │ │
│  │    - Save models as .pkl files                          │ │
│  │    - Save metrics as JSON files                         │ │
│  │    - Save metadata                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 8. Report Generation                                    │ │
│  │    - Generate evaluation report (Markdown)              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
                  ┌─────────────────┐
                  │ Filesystem      │
                  │ - Models (.pkl) │
                  │ - Metrics (JSON)│
                  │ - Logs (.log)   │
                  │ - Reports (.md) │
                  └─────────────────┘
```

---

## 1. Core Components

### 1.1 Training Script (train.py)

**Type**: Orchestration Component

**Responsibility**: Coordinate all pipeline steps sequentially

**Implementation**:
```python
# ml-pipeline/train.py
import logging
import sys
from pathlib import Path

# Import pipeline modules
from data.generate_dataset import generate_dataset_with_retry
from data.preprocess import preprocess_data
from features.engineer import engineer_features
from models.train import train_all_models_parallel
from models.evaluate import evaluate_all_models
from models.save import save_all_models, save_all_metrics
from utils.validation import validate_environment
from utils.reporting import generate_evaluation_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('ml-pipeline/logs/training.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("=== ML Pipeline Training Started ===")
        
        # Step 1: Validate environment
        logger.info("Step 1: Validating environment")
        validate_environment()
        
        # Step 2: Generate dataset
        logger.info("Step 2: Generating dataset")
        dataset = generate_dataset_with_retry(target_size=1000, max_retries=3, base_seed=42)
        
        # Step 3: Preprocess data
        logger.info("Step 3: Preprocessing data")
        X_train, X_test, y_train, y_test, scaler, encoder = preprocess_data(dataset)
        
        # Step 4: Engineer features
        logger.info("Step 4: Engineering features")
        X_train_eng, X_test_eng = engineer_features(X_train, X_test)
        
        # Step 5: Train models (parallel)
        logger.info("Step 5: Training models in parallel")
        models, metrics, errors = train_all_models_parallel(
            X_train_eng, y_train, X_test_eng, y_test
        )
        
        if len(models) == 0:
            logger.critical("All models failed to train")
            sys.exit(1)
        
        # Step 6: Determine version
        logger.info("Step 6: Determining model version")
        version = get_next_version('ml-pipeline/models/trained')
        
        # Step 7: Save models and artifacts
        logger.info("Step 7: Saving models and artifacts")
        save_all_models(models, version, 'ml-pipeline/models/trained')
        save_all_metrics(metrics, version, 'ml-pipeline/models/trained')
        save_preprocessing_artifacts(scaler, encoder, version, 'ml-pipeline/models/trained')
        
        # Step 8: Generate evaluation report
        logger.info("Step 8: Generating evaluation report")
        generate_evaluation_report(models, metrics, version, 'ml-pipeline/reports')
        
        logger.info(f"=== ML Pipeline Training Completed Successfully ({len(models)} models) ===")
        
        if errors:
            logger.warning(f"Some models failed: {list(errors.keys())}")
            sys.exit(0)  # Exit successfully despite partial failures
        
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Dependencies**:
- Python standard library (logging, sys, pathlib)
- Pipeline modules (data, features, models, utils)

**Interactions**:
- Calls all pipeline modules sequentially
- Writes to filesystem (logs, models, metrics, reports)
- Exits with status code (0 = success, 1 = failure)

---

### 1.2 Python Logging Module

**Type**: Monitoring Component

**Responsibility**: Capture and persist all pipeline events

**Configuration**:
```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('ml-pipeline/logs/training.log', mode='a'),
        logging.StreamHandler()
    ]
)
```

**Log Levels Used**:
- **INFO**: Normal operations (dataset generation, model training, saving)
- **WARNING**: Non-critical issues (quality gate failures, partial model failures)
- **ERROR**: Model-specific failures (continue execution)
- **CRITICAL**: Pipeline failures (exit execution)

**Log Output Destinations**:
- File: `ml-pipeline/logs/training.log` (append mode)
- Console: stdout (for CI/CD visibility)

**Log Retention**: Indefinite (Git handles storage)

---

### 1.3 Joblib Process Pool

**Type**: Parallelization Component

**Responsibility**: Coordinate parallel model training

**Implementation**:
```python
from joblib import Parallel, delayed

def train_all_models_parallel(X_train, y_train, X_test, y_test):
    model_configs = [
        ('random_forest', RandomForestClassifier, rf_params),
        ('gradient_boosting', GradientBoostingClassifier, gb_params),
        ('logistic_regression', LogisticRegression, lr_params)
    ]
    
    # Parallel training with n_jobs=-1 (use all CPU cores)
    results = Parallel(n_jobs=-1, backend='multiprocessing')(
        delayed(train_model_wrapper)(name, cls, params, X_train, y_train, X_test, y_test)
        for name, cls, params in model_configs
    )
    
    # Process results
    models = {}
    metrics_dict = {}
    errors = {}
    
    for model_name, model, metrics, error in results:
        if error is None:
            models[model_name] = model
            metrics_dict[model_name] = metrics
        else:
            errors[model_name] = error
    
    return models, metrics_dict, errors
```

**Configuration**:
- **n_jobs**: -1 (use all available CPU cores)
- **backend**: multiprocessing (process-based parallelism)
- **verbose**: 0 (no progress output)

**Resource Usage**:
- CPU: 100% utilization during training (desired)
- Memory: ~500 MB peak (dataset + models in memory)

**Benefits**:
- 3-4x faster training compared to sequential
- Automatic process management
- Built into scikit-learn ecosystem

---

### 1.4 Filesystem Storage

**Type**: Persistence Component

**Responsibility**: Store all pipeline artifacts

**Directory Structure**:
```
ml-pipeline/
├── data/
│   ├── raw/                          # Raw data (if any)
│   └── processed/
│       └── training_dataset_v1.csv   # Generated datasets
├── models/
│   └── trained/
│       ├── random_forest_v1.pkl      # Model files
│       ├── gradient_boosting_v1.pkl
│       ├── logistic_regression_v1.pkl
│       ├── voting_classifier_v1.pkl
│       ├── scaler_v1.pkl             # Preprocessing artifacts
│       ├── encoder_v1.pkl
│       ├── random_forest_v1_metrics.json      # Metrics files
│       ├── gradient_boosting_v1_metrics.json
│       ├── logistic_regression_v1_metrics.json
│       └── voting_classifier_v1_metrics.json
├── logs/
│   └── training.log                  # Training logs (append mode)
└── reports/
    └── evaluation_report_v1.md       # Evaluation reports
```

**File Formats**:
- Models: `.pkl` (pickle)
- Metrics: `.json` (JSON)
- Datasets: `.csv` (CSV)
- Logs: `.log` (plain text)
- Reports: `.md` (Markdown)

**Storage Management**:
- No automatic cleanup (keep all versions)
- Git LFS for large files (models)
- Total storage: ~50 MB per version

---

## 2. External Components

### 2.1 GitHub Actions (CI/CD)

**Type**: Orchestration Component (External)

**Responsibility**: Trigger and monitor training pipeline

**Workflow Configuration**:
```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline Training
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:      # Manual trigger

jobs:
  train:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          lfs: true  # Pull Git LFS files (models)
      
      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r ml-pipeline/requirements.txt
      
      - name: Run ML Pipeline
        run: python ml-pipeline/train.py
      
      - name: Commit trained models
        if: success()
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add ml-pipeline/models/trained/
          git add ml-pipeline/logs/
          git add ml-pipeline/reports/
          git commit -m "Update trained models [skip ci]" || echo "No changes"
          git push
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: training-artifacts
          path: |
            ml-pipeline/logs/
            ml-pipeline/reports/
```

**Triggers**:
- Push to main branch
- Daily schedule (midnight UTC)
- Manual dispatch

**Notifications**:
- Email on failure (GitHub default)
- UI status badge
- Commit status checks

**Timeout**: 10 minutes (pipeline should complete in < 1 minute)

---

### 2.2 GitHub Dependabot

**Type**: Security Component (External)

**Responsibility**: Automated dependency vulnerability scanning

**Configuration**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/ml-pipeline"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"
    reviewers:
      - "team-ml"
```

**Behavior**:
- Scans `ml-pipeline/requirements.txt` weekly
- Creates PRs for vulnerable dependencies
- Respects minor version pinning (~=)
- Limits to 5 open PRs at a time

**Notifications**:
- PR creation
- Security alerts

---

### 2.3 Git / Git LFS

**Type**: Version Control Component (External)

**Responsibility**: Version control for code and models

**Configuration**:
```
# .gitattributes
*.pkl filter=lfs diff=lfs merge=lfs -text
*.csv filter=lfs diff=lfs merge=lfs -text
```

**Usage**:
- Code versioning: Standard Git
- Model versioning: Git LFS (large files)
- Commit history: Audit trail for all changes

**Benefits**:
- Complete version history
- Easy rollback
- Audit trail

---

## 3. Component Interactions

### 3.1 Training Pipeline Flow

```
┌─────────────────┐
│ GitHub Actions  │ (Trigger)
└────────┬────────┘
         │ Executes
         ↓
┌─────────────────┐
│   train.py      │ (Orchestration)
└────────┬────────┘
         │ Calls
         ↓
┌─────────────────┐
│ Pipeline Modules│ (Data, Features, Models, Utils)
└────────┬────────┘
         │ Uses
         ↓
┌─────────────────┐
│ Joblib Pool     │ (Parallelization)
└────────┬────────┘
         │ Trains
         ↓
┌─────────────────┐
│ scikit-learn    │ (ML Models)
└────────┬────────┘
         │ Saves to
         ↓
┌─────────────────┐
│ Filesystem      │ (Persistence)
└────────┬────────┘
         │ Commits to
         ↓
┌─────────────────┐
│ Git / Git LFS   │ (Version Control)
└─────────────────┘
```

### 3.2 Logging Flow

```
┌─────────────────┐
│ Pipeline Modules│
└────────┬────────┘
         │ Log events
         ↓
┌─────────────────┐
│ Python Logging  │
└────────┬────────┘
         │ Writes to
         ├─────────────────┐
         ↓                 ↓
┌─────────────────┐  ┌─────────────────┐
│ training.log    │  │ Console (stdout)│
│ (File)          │  │ (CI/CD visible) │
└─────────────────┘  └─────────────────┘
```

### 3.3 Alerting Flow

```
┌─────────────────┐
│   train.py      │
└────────┬────────┘
         │ Exits with status code
         ↓
┌─────────────────┐
│ GitHub Actions  │
└────────┬────────┘
         │ Detects failure
         ↓
┌─────────────────┐
│ GitHub          │
│ Notifications   │
│ - Email         │
│ - UI Badge      │
└─────────────────┘
```

---

## 4. Component Lifecycle

### 4.1 Training Pipeline Lifecycle

**Startup**:
1. GitHub Actions triggers workflow
2. Checkout code and setup Python environment
3. Install dependencies
4. Execute `train.py`

**Execution**:
1. Validate environment
2. Generate dataset (with retry)
3. Preprocess data
4. Engineer features
5. Train models (parallel)
6. Evaluate models
7. Save models and metrics
8. Generate report

**Shutdown**:
1. Log completion status
2. Exit with status code (0 or 1)
3. GitHub Actions commits artifacts (if successful)
4. GitHub Actions sends notifications (if failed)

**Duration**: < 1 minute (target), < 10 minutes (timeout)

---

### 4.2 Joblib Process Pool Lifecycle

**Startup**:
1. `Parallel(n_jobs=-1)` creates process pool
2. Determine number of CPU cores
3. Spawn worker processes

**Execution**:
1. Distribute model training tasks to workers
2. Each worker trains one model independently
3. Workers return results to main process

**Shutdown**:
1. Collect all results
2. Terminate worker processes
3. Return aggregated results

**Duration**: ~30-45 seconds (parallel training)

---

## 5. Component Dependencies

### 5.1 Dependency Graph

```
train.py
├── Python Standard Library
│   ├── logging
│   ├── sys
│   ├── pathlib
│   └── json
├── scikit-learn~=1.3.0
│   ├── RandomForestClassifier
│   ├── GradientBoostingClassifier
│   ├── LogisticRegression
│   ├── VotingClassifier
│   ├── train_test_split
│   ├── StratifiedKFold
│   ├── cross_val_score
│   ├── MinMaxScaler
│   └── OneHotEncoder
├── numpy~=1.24.0
│   ├── np.random
│   ├── np.array
│   └── np.clip
├── pandas~=2.0.0
│   ├── pd.DataFrame
│   ├── pd.read_csv
│   └── pd.to_csv
├── scipy~=1.10.0
│   └── scipy.stats
└── joblib (transitive from scikit-learn)
    └── Parallel, delayed
```

### 5.2 External Dependencies

```
GitHub Actions
├── ubuntu-latest (runner)
├── actions/checkout@v3
├── actions/setup-python@v4
└── actions/upload-artifact@v3

GitHub Dependabot
└── GitHub Security Advisories

Git / Git LFS
├── Git 2.x
└── Git LFS 3.x
```

---

## 6. Component Configuration

### 6.1 Training Script Configuration

**Configuration File**: `ml-pipeline/config.py`

```python
# ml-pipeline/config.py
import os

class Config:
    # Dataset configuration
    DATASET_SIZE = int(os.getenv('DATASET_SIZE', 1000))
    RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
    
    # Training configuration
    TRAIN_TEST_SPLIT = float(os.getenv('TRAIN_TEST_SPLIT', 0.80))
    CV_FOLDS = int(os.getenv('CV_FOLDS', 5))
    
    # Model hyperparameters
    RF_N_ESTIMATORS = int(os.getenv('RF_N_ESTIMATORS', 100))
    RF_MAX_DEPTH = int(os.getenv('RF_MAX_DEPTH', 10))
    
    GB_N_ESTIMATORS = int(os.getenv('GB_N_ESTIMATORS', 100))
    GB_LEARNING_RATE = float(os.getenv('GB_LEARNING_RATE', 0.1))
    
    LR_C = float(os.getenv('LR_C', 1.0))
    LR_MAX_ITER = int(os.getenv('LR_MAX_ITER', 1000))
    
    # Paths
    DATA_DIR = 'ml-pipeline/data/processed'
    MODEL_DIR = 'ml-pipeline/models/trained'
    LOG_DIR = 'ml-pipeline/logs'
    REPORT_DIR = 'ml-pipeline/reports'
    
    # Performance thresholds
    ACCURACY_THRESHOLD = float(os.getenv('ACCURACY_THRESHOLD', 0.80))
```

**Configuration Precedence**:
1. Environment variables (highest priority)
2. Configuration file defaults
3. Code defaults (lowest priority)

---

### 6.2 Logging Configuration

**Configuration**: Inline in `train.py`

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('ml-pipeline/logs/training.log', mode='a'),
        logging.StreamHandler()
    ]
)
```

**Configurable Parameters**:
- Log level: INFO (can be changed to DEBUG via environment variable)
- Log format: Simple timestamp + level + message
- Log file: `ml-pipeline/logs/training.log`
- Log mode: Append (never overwrite)

---

## 7. Component Monitoring

### 7.1 Training Pipeline Monitoring

**Metrics Collected**:
- Training duration (total and per model)
- Dataset size and class balance
- Model performance metrics (accuracy, F1, etc.)
- Cross-validation scores
- Error counts and types

**Monitoring Method**: Log analysis (manual review)

**Monitoring Frequency**: After each training run

---

### 7.2 CI/CD Monitoring

**Metrics Collected**:
- Workflow execution time
- Success/failure rate
- Artifact sizes

**Monitoring Method**: GitHub Actions UI

**Monitoring Frequency**: Real-time

---

## 8. Component Scalability

### 8.1 Current Scalability Limits

| Component | Current Limit | Bottleneck |
|-----------|---------------|------------|
| Dataset Generation | 1000 records | Fixed size (by design) |
| Model Training | 4 models | CPU cores (parallelization) |
| Storage | ~50 MB/version | Git LFS (acceptable) |
| Training Duration | < 1 minute | CPU speed |

### 8.2 Future Scalability Considerations

**If dataset grows to 10K+ records**:
- Consider distributed training (Dask, Ray)
- Consider cloud storage (S3, GCS)
- Consider GPU acceleration

**If model count grows to 10+ models**:
- Consider task queue (Celery, RQ)
- Consider model registry (MLflow)
- Consider distributed training

**Current Design**: Sufficient for project scope (1000 records, 4 models)

---

## Component Summary

| Component | Type | Responsibility | Technology |
|-----------|------|----------------|------------|
| **train.py** | Orchestration | Coordinate pipeline steps | Python script |
| **Python Logging** | Monitoring | Capture pipeline events | Python logging module |
| **Joblib Pool** | Parallelization | Parallel model training | joblib (scikit-learn) |
| **Filesystem** | Persistence | Store artifacts | Local filesystem |
| **GitHub Actions** | CI/CD | Trigger and monitor | GitHub Actions |
| **Dependabot** | Security | Vulnerability scanning | GitHub Dependabot |
| **Git / Git LFS** | Version Control | Version code and models | Git, Git LFS |

**Total Components**: 7 (4 internal, 3 external)

**Infrastructure Complexity**: Low (no queues, caches, or additional services)

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC NFR Design

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial logical components document |
