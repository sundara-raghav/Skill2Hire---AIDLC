# NFR Design Patterns: ML Pipeline Unit

## Overview

This document defines all non-functional design patterns for the ML Pipeline unit, incorporating NFR requirements into concrete design decisions.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## 1. Resilience Patterns

### 1.1 Fail-Fast Pattern (Critical Operations)

**Pattern**: Fail immediately on critical errors without retry

**Applicability**: Data generation failures, preprocessing failures

**Implementation**:
```python
def generate_and_preprocess_data():
    try:
        # Critical operation - fail fast
        dataset = generate_dataset(target_size=1000)
        validate_dataset(dataset)
        X_train, X_test, y_train, y_test = preprocess_data(dataset)
        return X_train, X_test, y_train, y_test
    except Exception as e:
        logger.critical(f"Critical pipeline failure: {e}", exc_info=True)
        sys.exit(1)  # Fail fast, no retry
```

**Rationale**: Critical errors indicate fundamental issues (invalid data, missing dependencies) that require immediate attention. Retrying would waste time and resources.

**Benefits**:
- Fast failure detection
- Clear error signals
- No wasted resources on doomed operations

---

### 1.2 Retry with Seed Increment Pattern

**Pattern**: Retry failed operations with incremented random seed

**Applicability**: Dataset generation failures due to randomness (duplicate detection, validation)

**Implementation**:
```python
def generate_dataset_with_retry(target_size, max_retries=3, base_seed=42):
    for attempt in range(max_retries):
        try:
            seed = base_seed + attempt
            logger.info(f"Dataset generation attempt {attempt + 1} with seed {seed}")
            dataset = generate_synthetic_dataset(target_size, seed=seed)
            validate_dataset(dataset)
            logger.info(f"Dataset generation successful on attempt {attempt + 1}")
            return dataset
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.critical(f"Dataset generation failed after {max_retries} attempts")
                raise Exception(f"Dataset generation failed after {max_retries} attempts")
    return None
```

**Rationale**: Random seed changes can resolve transient issues (duplicate generation, edge case distributions) without changing core logic.

**Benefits**:
- Handles transient randomness issues
- Simple implementation
- Preserves reproducibility (seed documented)

---

### 1.3 Continue-on-Error Pattern (Model Training)

**Pattern**: Continue training remaining models if one model fails

**Applicability**: Individual model training failures

**Implementation**:
```python
def train_all_models(X_train, y_train, X_test, y_test):
    models = {}
    errors = {}
    
    model_configs = [
        ('random_forest', RandomForestClassifier, rf_params),
        ('gradient_boosting', GradientBoostingClassifier, gb_params),
        ('logistic_regression', LogisticRegression, lr_params)
    ]
    
    for model_name, model_class, params in model_configs:
        try:
            logger.info(f"Training {model_name}")
            model = model_class(**params)
            model.fit(X_train, y_train)
            models[model_name] = model
            logger.info(f"{model_name} training successful")
        except Exception as e:
            logger.error(f"{model_name} training failed: {e}", exc_info=True)
            errors[model_name] = str(e)
            continue  # Continue with next model
    
    if len(models) == 0:
        logger.critical("All models failed to train")
        sys.exit(1)
    
    logger.info(f"Successfully trained {len(models)}/{len(model_configs)} models")
    return models, errors
```

**Rationale**: Partial success is better than complete failure. Some models may fail due to hyperparameter issues or data characteristics, but other models can still succeed.

**Benefits**:
- Maximizes successful outputs
- Provides partial functionality
- Enables debugging of specific model failures

---

### 1.4 Partial Result Persistence Pattern

**Pattern**: Save all successfully trained models, even if some fail

**Applicability**: Model saving after training

**Implementation**:
```python
def save_trained_models(models, version, model_dir):
    saved_models = []
    save_errors = {}
    
    for model_name, model in models.items():
        try:
            filepath = save_model(model, model_name, version, model_dir)
            saved_models.append(model_name)
            logger.info(f"Saved {model_name} to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save {model_name}: {e}", exc_info=True)
            save_errors[model_name] = str(e)
    
    if len(saved_models) == 0:
        logger.critical("Failed to save any models")
        sys.exit(1)
    
    logger.info(f"Successfully saved {len(saved_models)} models")
    return saved_models, save_errors
```

**Rationale**: Successfully trained models should be preserved even if other models fail. This enables partial deployment and debugging.

**Benefits**:
- Preserves successful work
- Enables partial functionality
- Facilitates debugging

---

### 1.5 Warn-and-Continue Pattern (Quality Gates)

**Pattern**: Log warning but continue execution when quality gates fail

**Applicability**: Model performance threshold validation (80% accuracy)

**Implementation**:
```python
def validate_and_save_model(model, model_name, metrics, version, model_dir):
    # Check quality gate
    if metrics['accuracy'] < 0.80:
        logger.warning(
            f"{model_name} accuracy {metrics['accuracy']:.2%} below 80% threshold. "
            f"Saving anyway for debugging."
        )
        # Mark in metadata
        metadata = create_model_metadata(model, model_name, metrics, version)
        metadata['performance_threshold_met'] = False
        metadata['quality_gate_warning'] = f"Accuracy {metrics['accuracy']:.2%} below 80%"
    else:
        logger.info(f"{model_name} meets 80% accuracy threshold")
        metadata = create_model_metadata(model, model_name, metrics, version)
        metadata['performance_threshold_met'] = True
    
    # Save model regardless of threshold
    save_model(model, model_name, version, model_dir)
    save_metadata(metadata, model_name, version, model_dir)
    
    return metadata
```

**Rationale**: Models below threshold are still useful for debugging and analysis. Blocking saves would prevent investigation of poor performance.

**Benefits**:
- Enables debugging of underperforming models
- Preserves all training results
- Clear documentation of quality issues

---

## 2. Scalability Patterns

### 2.1 Process Pool Parallelization Pattern

**Pattern**: Use multiprocessing with joblib for parallel model training

**Applicability**: Training multiple models simultaneously

**Implementation**:
```python
from joblib import Parallel, delayed

def train_model_wrapper(model_name, model_class, params, X_train, y_train, X_test, y_test):
    try:
        logger.info(f"Training {model_name} in parallel")
        model = model_class(**params)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1')
        
        # Train on full training set
        model.fit(X_train, y_train)
        
        # Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        metrics['cv_f1_mean'] = cv_scores.mean()
        metrics['cv_f1_std'] = cv_scores.std()
        
        return model_name, model, metrics, None
    except Exception as e:
        logger.error(f"{model_name} training failed: {e}")
        return model_name, None, None, str(e)

def train_all_models_parallel(X_train, y_train, X_test, y_test):
    model_configs = [
        ('random_forest', RandomForestClassifier, rf_params),
        ('gradient_boosting', GradientBoostingClassifier, gb_params),
        ('logistic_regression', LogisticRegression, lr_params)
    ]
    
    # Parallel training with n_jobs=-1 (use all cores)
    results = Parallel(n_jobs=-1)(
        delayed(train_model_wrapper)(name, cls, params, X_train, y_train, X_test, y_test)
        for name, cls, params in model_configs
    )
    
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

**Rationale**: Parallel training reduces total training time by ~3-4x. Joblib handles process management and is scikit-learn's recommended parallelization library.

**Benefits**:
- Faster training (< 1 minute for all models)
- Efficient CPU utilization
- Simple implementation (joblib handles complexity)

---

### 2.2 Automatic Memory Management Pattern

**Pattern**: Rely on Python's garbage collection for memory management

**Applicability**: All memory-intensive operations

**Implementation**:
```python
def train_pipeline():
    # Load data
    dataset = load_dataset()
    
    # Preprocess (Python will GC dataset after this if not referenced)
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
    
    # Train models (Python will GC preprocessed data after this)
    models = train_all_models(X_train, y_train, X_test, y_test)
    
    # Save models (Python will GC models after this)
    save_all_models(models)
    
    # No explicit cleanup needed - Python GC handles it
```

**Rationale**: Dataset size (~1000 records) and model sizes (~50 MB total) are small enough for automatic memory management. Explicit cleanup adds complexity without benefit.

**Benefits**:
- Simple implementation
- No manual memory management overhead
- Sufficient for small dataset

**Limitations**: Not suitable for large datasets (>100K records) or large models (>1 GB)

---

### 2.3 Version Accumulation Pattern

**Pattern**: Keep all model versions indefinitely, rely on Git for storage management

**Applicability**: Model versioning and storage

**Implementation**:
```python
def save_model_version(model, model_name, model_dir):
    # Determine next version
    existing_versions = [
        int(f.replace(f'{model_name}_v', '').replace('.pkl', ''))
        for f in os.listdir(model_dir)
        if f.startswith(f'{model_name}_v') and f.endswith('.pkl')
    ]
    
    if not existing_versions:
        version = 'v1'
    else:
        next_version_num = max(existing_versions) + 1
        version = f'v{next_version_num}'
    
    # Save new version (never delete old versions)
    filepath = os.path.join(model_dir, f'{model_name}_{version}.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Saved {model_name} as {version}")
    return version, filepath
```

**Rationale**: Git LFS handles large file storage efficiently. Keeping all versions enables rollback and historical analysis. Manual cleanup is simpler than automated retention policies.

**Benefits**:
- Complete version history
- Easy rollback
- No complex retention logic

---

## 3. Performance Patterns

### 3.1 No-Caching Pattern

**Pattern**: Regenerate all intermediate results on each training run

**Applicability**: Dataset generation, preprocessing, feature engineering

**Implementation**:
```python
def train_pipeline():
    # Always regenerate from scratch
    dataset = generate_dataset(target_size=1000)
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
    X_train_eng, X_test_eng = engineer_features(X_train, X_test)
    models = train_models(X_train_eng, y_train, X_test_eng, y_test)
    
    # No caching - simple and avoids stale data
```

**Rationale**: Training is fast enough (< 1 minute) that caching adds complexity without significant benefit. No caching eliminates stale data issues.

**Benefits**:
- Simple implementation
- No stale data issues
- No cache invalidation logic needed

**Trade-offs**: Slightly slower than caching, but acceptable for < 1 minute training time

---

### 3.2 Eager Loading Pattern

**Pattern**: Load all models at Backend startup

**Applicability**: Backend model loading for inference

**Implementation**:
```python
# Backend startup (app/__init__.py)
class MLModelManager:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.models = {}
        self.scaler = None
        self.encoder = None
        
        # Eager loading at startup
        self.load_all_models()
    
    def load_all_models(self):
        logger.info("Loading all models at startup")
        
        # Load models
        self.models['random_forest'] = self.load_model('random_forest.pkl')
        self.models['gradient_boosting'] = self.load_model('gradient_boosting.pkl')
        self.models['logistic_regression'] = self.load_model('logistic_regression.pkl')
        self.models['voting_classifier'] = self.load_model('voting_classifier.pkl')
        
        # Load preprocessing artifacts
        self.scaler = self.load_model('scaler.pkl')
        self.encoder = self.load_model('encoder.pkl')
        
        logger.info(f"Loaded {len(self.models)} models successfully")
    
    def load_model(self, filename):
        filepath = os.path.join(self.model_dir, filename)
        with open(filepath, 'rb') as f:
            return pickle.load(f)
```

**Rationale**: Models are small (~50 MB total) and loading is fast (~1 second). Eager loading ensures first request is fast and simplifies code.

**Benefits**:
- Fast inference (no loading delay)
- Simple implementation
- Predictable startup time

**Trade-offs**: Higher startup memory footprint, but acceptable for small models

---

## 4. Security Patterns

### 4.1 Automated Dependency Scanning Pattern

**Pattern**: Use GitHub Dependabot for automated vulnerability scanning

**Applicability**: Dependency security monitoring

**Implementation**:
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
```

**Rationale**: Dependabot is built into GitHub, requires no additional setup, and automatically creates PRs for vulnerable dependencies.

**Benefits**:
- Automated vulnerability detection
- Automatic PR creation
- No additional tooling required

---

### 4.2 Default Permission Pattern

**Pattern**: Use system default file permissions (644 for files, 755 for directories)

**Applicability**: Model files, dataset files, log files

**Implementation**:
```python
def save_model(model, filepath):
    # Save with default permissions (644)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    # No explicit chmod needed - default is acceptable
```

**Rationale**: Synthetic data and models contain no sensitive information. Default permissions are sufficient. Container environment provides isolation.

**Benefits**:
- Simple implementation
- Standard Unix permissions
- Sufficient security for non-sensitive data

---

### 4.3 Input Validation Pattern

**Pattern**: Validate all inputs against business rules before processing

**Applicability**: Dataset generation, preprocessing, model training

**Implementation**:
```python
def validate_student_profile(profile):
    errors = []
    
    # Validate CGPA
    if not (0.0 <= profile['cgpa'] <= 10.0):
        errors.append("CGPA must be between 0.0 and 10.0")
    
    # Validate aptitude score
    if not (0 <= profile['aptitude_score'] <= 100):
        errors.append("Aptitude score must be between 0 and 100")
    
    # ... (all 44 business rules)
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return True

def generate_dataset(target_size):
    dataset = []
    for i in range(target_size):
        profile = generate_student_profile()
        validate_student_profile(profile)  # Validate before adding
        dataset.append(profile)
    return dataset
```

**Rationale**: Input validation prevents invalid data from entering the pipeline. All 44 business rules are enforced.

**Benefits**:
- Data quality assurance
- Early error detection
- Compliance with business rules

---

## 5. Monitoring Patterns

### 5.1 Simple Structured Logging Pattern

**Pattern**: Use simple timestamp + level + message format for all logs

**Applicability**: All logging operations

**Implementation**:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('ml-pipeline/logs/training.log'),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Starting dataset generation (target: 1000 records)")
logger.warning("Model accuracy 78% below 80% threshold")
logger.error("Random Forest training failed", exc_info=True)
logger.critical("All models failed to train")
```

**Rationale**: Simple format is human-readable and sufficient for basic monitoring. No need for structured JSON logging.

**Benefits**:
- Human-readable logs
- Simple implementation
- Sufficient for manual review

---

### 5.2 JSON Metrics Persistence Pattern

**Pattern**: Store evaluation metrics as JSON files alongside model files

**Applicability**: Model evaluation metrics storage

**Implementation**:
```python
def save_model_metrics(model_name, version, metrics, model_dir):
    metrics_data = {
        'model_name': model_name,
        'version': version,
        'training_date': datetime.utcnow().isoformat(),
        'metrics': {
            'cv_f1_mean': float(metrics['cv_f1_mean']),
            'cv_f1_std': float(metrics['cv_f1_std']),
            'test_accuracy': float(metrics['accuracy']),
            'test_precision': float(metrics['precision']),
            'test_recall': float(metrics['recall']),
            'test_f1_score': float(metrics['f1_score']),
            'test_roc_auc': float(metrics['roc_auc'])
        },
        'performance_threshold_met': metrics['accuracy'] >= 0.80
    }
    
    filepath = os.path.join(model_dir, f'{model_name}_{version}_metrics.json')
    with open(filepath, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    logger.info(f"Saved metrics for {model_name} {version}")
    return filepath
```

**Rationale**: JSON is human-readable and machine-parseable. One file per model version enables easy comparison.

**Benefits**:
- Human-readable format
- Machine-parseable for analysis
- Simple file-based storage

---

### 5.3 Log Accumulation Pattern

**Pattern**: Append to log file indefinitely, rely on Git for retention

**Applicability**: Training logs

**Implementation**:
```python
# Configure logging to append (not overwrite)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('ml-pipeline/logs/training.log', mode='a'),  # Append mode
        logging.StreamHandler()
    ]
)
```

**Rationale**: Git handles file storage. Keeping all logs enables historical analysis. No complex retention logic needed.

**Benefits**:
- Complete log history
- Simple implementation
- No retention logic needed

---

### 5.4 CI/CD Alerting Pattern

**Pattern**: Rely on GitHub Actions failure notifications for alerting

**Applicability**: Training failure alerts

**Implementation**:
```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline Training
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r ml-pipeline/requirements.txt
      - name: Run ML Pipeline
        run: python ml-pipeline/train.py
      # GitHub Actions automatically sends failure notifications
```

**Rationale**: GitHub Actions provides built-in failure notifications via email and UI. No additional alerting infrastructure needed.

**Benefits**:
- Built-in alerting
- No additional infrastructure
- Sufficient for basic monitoring

---

## 6. Reproducibility Patterns

### 6.1 Dual Seed Propagation Pattern

**Pattern**: Set both global seeds and explicit random_state parameters

**Applicability**: All random operations

**Implementation**:
```python
import random
import numpy as np

def set_global_seeds(seed=42):
    """Set global random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    logger.info(f"Set global random seeds to {seed}")

def train_pipeline(seed=42):
    # Set global seeds
    set_global_seeds(seed)
    
    # Also pass explicit random_state to all operations
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=seed,  # Explicit seed
        stratify=y
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)  # Explicit seed
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=seed,  # Explicit seed
        **other_params
    )
    
    # Both global and explicit seeds ensure reproducibility
```

**Rationale**: Global seeds catch operations that don't accept random_state. Explicit seeds ensure reproducibility even if global seeds are not set. Redundancy ensures complete reproducibility.

**Benefits**:
- Complete reproducibility
- Catches all random operations
- Redundant safety

---

### 6.2 Accuracy-Based Version Comparison Pattern

**Pattern**: Compare model versions using test accuracy only

**Applicability**: Model version comparison for deployment decisions

**Implementation**:
```python
def should_deploy_new_model(new_metrics, existing_metrics):
    if existing_metrics is None:
        logger.info("No existing model, deploying new model")
        return True
    
    new_accuracy = new_metrics['accuracy']
    existing_accuracy = existing_metrics['accuracy']
    
    if new_accuracy > existing_accuracy:
        improvement = (new_accuracy - existing_accuracy) * 100
        logger.info(
            f"New model accuracy {new_accuracy:.2%} > "
            f"existing {existing_accuracy:.2%} "
            f"(+{improvement:.2f}pp). Deploying new model."
        )
        return True
    else:
        logger.info(
            f"New model accuracy {new_accuracy:.2%} <= "
            f"existing {existing_accuracy:.2%}. "
            f"Keeping existing model."
        )
        return False
```

**Rationale**: Accuracy is the simplest and most interpretable metric. Single metric comparison avoids complex multi-metric trade-offs.

**Benefits**:
- Simple decision logic
- Clear interpretation
- No metric weighting needed

---

### 6.3 Dependency Check Validation Pattern

**Pattern**: Verify all dependencies are installed before training

**Applicability**: Training script startup

**Implementation**:
```python
def validate_environment():
    required_packages = [
        'sklearn',
        'numpy',
        'pandas',
        'scipy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.critical(f"Missing required packages: {missing_packages}")
        logger.critical("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("All required dependencies are installed")
    return True

def main():
    # Validate environment first
    validate_environment()
    
    # Proceed with training
    train_pipeline()
```

**Rationale**: Dependency check catches missing packages early. Version check is not needed (minor version pinning allows patches).

**Benefits**:
- Early error detection
- Clear error messages
- Simple implementation

---

## 7. Orchestration Patterns

### 7.1 Simple Script Pattern

**Pattern**: Single Python script executes all pipeline steps sequentially

**Applicability**: Training pipeline orchestration

**Implementation**:
```python
# ml-pipeline/train.py
def main():
    logger.info("=== ML Pipeline Training Started ===")
    
    # Step 1: Validate environment
    validate_environment()
    
    # Step 2: Generate dataset
    dataset = generate_dataset_with_retry(target_size=1000)
    
    # Step 3: Preprocess data
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
    
    # Step 4: Engineer features
    X_train_eng, X_test_eng = engineer_features(X_train, X_test)
    
    # Step 5: Train models (parallel)
    models, metrics, errors = train_all_models_parallel(
        X_train_eng, y_train, X_test_eng, y_test
    )
    
    # Step 6: Save models and metrics
    version = get_next_version()
    save_all_models(models, version)
    save_all_metrics(metrics, version)
    
    # Step 7: Generate evaluation report
    generate_evaluation_report(models, metrics, version)
    
    logger.info("=== ML Pipeline Training Completed ===")

if __name__ == '__main__':
    main()
```

**Rationale**: Simple script is sufficient for sequential pipeline. No need for complex orchestration tools (Airflow, Prefect) for simple workflow.

**Benefits**:
- Simple implementation
- Easy to understand and debug
- No additional dependencies

---

## Pattern Summary Matrix

| Category | Pattern | Applicability | Key Benefit |
|----------|---------|---------------|-------------|
| **Resilience** | Fail-Fast | Critical operations | Fast failure detection |
| **Resilience** | Retry with Seed Increment | Dataset generation | Handles transient randomness |
| **Resilience** | Continue-on-Error | Model training | Maximizes successful outputs |
| **Resilience** | Partial Result Persistence | Model saving | Preserves successful work |
| **Resilience** | Warn-and-Continue | Quality gates | Enables debugging |
| **Scalability** | Process Pool Parallelization | Model training | 3-4x faster training |
| **Scalability** | Automatic Memory Management | All operations | Simple implementation |
| **Scalability** | Version Accumulation | Model versioning | Complete history |
| **Performance** | No-Caching | Intermediate results | Simple, no stale data |
| **Performance** | Eager Loading | Backend model loading | Fast inference |
| **Security** | Automated Dependency Scanning | Vulnerability detection | No additional tooling |
| **Security** | Default Permission | File permissions | Simple, sufficient |
| **Security** | Input Validation | Data validation | Data quality assurance |
| **Monitoring** | Simple Structured Logging | All logging | Human-readable |
| **Monitoring** | JSON Metrics Persistence | Metrics storage | Machine-parseable |
| **Monitoring** | Log Accumulation | Log retention | Complete history |
| **Monitoring** | CI/CD Alerting | Failure alerts | Built-in notifications |
| **Reproducibility** | Dual Seed Propagation | Random operations | Complete reproducibility |
| **Reproducibility** | Accuracy-Based Comparison | Version comparison | Simple decision logic |
| **Reproducibility** | Dependency Check Validation | Environment validation | Early error detection |
| **Orchestration** | Simple Script | Pipeline orchestration | Simple, easy to debug |

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC NFR Design
- **Next**: logical-components.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial NFR design patterns document |
