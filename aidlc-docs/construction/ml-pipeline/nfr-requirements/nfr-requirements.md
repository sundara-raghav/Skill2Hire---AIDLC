# Non-Functional Requirements: ML Pipeline Unit

## Overview

This document defines all non-functional requirements (NFRs) for the ML Pipeline unit, covering scalability, performance, availability, security, reliability, and maintainability.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## 1. Scalability Requirements

### 1.1 Dataset Scalability

**Requirement**: The ML Pipeline SHALL support a fixed dataset size of approximately 1000 records with no growth expected.

**Rationale**: The synthetic dataset is designed for training purposes only and does not need to scale beyond the initial size. This simplifies storage and processing requirements.

**Acceptance Criteria**:
- Dataset generation produces 1000-1200 records
- No dynamic scaling mechanisms required
- Memory footprint remains constant (~1-2 MB for dataset)

**Impact**: Low complexity, predictable resource usage

---

### 1.2 Model Training Scalability

**Requirement**: The ML Pipeline SHALL support parallel training of multiple models simultaneously.

**Rationale**: Training 4 models sequentially would take longer than necessary. Parallel training reduces total training time and enables frequent retraining.

**Acceptance Criteria**:
- All 4 models (RF, GB, LR, Voting) can train in parallel
- CPU cores are utilized efficiently (n_jobs=-1)
- No resource contention between parallel training jobs

**Implementation**:
```python
# Use joblib parallel backend
from joblib import Parallel, delayed

models = Parallel(n_jobs=-1)(
    delayed(train_model)(model_config) 
    for model_config in model_configs
)
```

**Impact**: Reduces training time by ~3-4x compared to sequential training

---

### 1.3 Storage Scalability

**Requirement**: The ML Pipeline SHALL store all models and datasets on local filesystem with no cloud storage integration.

**Rationale**: Simple deployment model, no external dependencies, sufficient for project scope.

**Acceptance Criteria**:
- All models stored in `ml-pipeline/models/trained/` directory
- All datasets stored in `ml-pipeline/data/processed/` directory
- Total storage footprint < 50 MB (models + datasets)

**Storage Structure**:
```
ml-pipeline/
├── data/
│   ├── raw/
│   └── processed/
│       └── training_dataset_v1.csv (~1 MB)
├── models/
│   └── trained/
│       ├── random_forest_v1.pkl (~10 MB)
│       ├── gradient_boosting_v1.pkl (~8 MB)
│       ├── logistic_regression_v1.pkl (~1 MB)
│       ├── voting_classifier_v1.pkl (~20 MB)
│       ├── scaler_v1.pkl (~1 KB)
│       └── encoder_v1.pkl (~1 KB)
```

**Impact**: No cloud costs, simple deployment, fast local access

---

## 2. Performance Requirements

### 2.1 Training Duration

**Requirement**: The ML Pipeline SHALL complete training of all 4 models in under 1 minute on standard CPU hardware.

**Rationale**: Frequent retraining (daily or on every push) requires fast training cycles to avoid blocking CI/CD pipeline.

**Acceptance Criteria**:
- Total training time (all 4 models) < 60 seconds
- Individual model training times:
  - Random Forest: < 20 seconds
  - Gradient Boosting: < 25 seconds
  - Logistic Regression: < 5 seconds
  - Voting Classifier: < 10 seconds
- Measured on: 4-core CPU, 8 GB RAM

**Performance Targets**:
| Model | Target Time | Max Time |
|-------|-------------|----------|
| Random Forest | 15s | 20s |
| Gradient Boosting | 20s | 25s |
| Logistic Regression | 3s | 5s |
| Voting Classifier | 8s | 10s |
| **Total** | **46s** | **60s** |

**Impact**: Enables frequent retraining without CI/CD bottleneck

---

### 2.2 Dataset Generation Performance

**Requirement**: The ML Pipeline SHALL generate 1000+ synthetic records in under 10 seconds.

**Rationale**: Dataset generation is a prerequisite for training. Fast generation enables rapid iteration during development.

**Acceptance Criteria**:
- Generate 1000 records in < 10 seconds
- Duplicate detection overhead < 2 seconds
- Validation overhead < 1 second

**Performance Breakdown**:
- Record generation: ~5 seconds (1000 records)
- Duplicate detection: ~2 seconds
- Validation: ~1 second
- File I/O: ~1 second
- **Total**: ~9 seconds

**Impact**: Fast iteration during development and testing

---

### 2.3 GPU Acceleration

**Requirement**: The ML Pipeline SHALL NOT require GPU acceleration and SHALL run on CPU-only hardware.

**Rationale**: Dataset size (1000 records) and model complexity (tree-based + logistic regression) do not benefit significantly from GPU acceleration. CPU training is sufficient and simplifies deployment.

**Acceptance Criteria**:
- All models train successfully on CPU-only hardware
- No CUDA or GPU dependencies required
- Training time targets met on CPU

**Impact**: Simplified deployment, no GPU costs, broader hardware compatibility

---

## 3. Availability Requirements

### 3.1 Training Frequency

**Requirement**: The ML Pipeline SHALL support frequent retraining (daily or on every code push) without manual intervention.

**Rationale**: Continuous integration workflow requires automated, frequent retraining to validate model changes.

**Acceptance Criteria**:
- Training can be triggered automatically via CI/CD
- No manual steps required for retraining
- Training completes within CI/CD timeout (< 5 minutes)

**Trigger Mechanisms**:
- GitHub Actions workflow on push to main branch
- Scheduled daily training (cron job)
- Manual trigger via workflow_dispatch

**Impact**: Enables continuous model improvement and validation

---

### 3.2 Model Versioning

**Requirement**: The ML Pipeline SHALL version all trained models using Git-based versioning with sequential version numbers.

**Rationale**: Simple versioning scheme, no external dependencies, sufficient for project scope.

**Acceptance Criteria**:
- Each model version has unique identifier (v1, v2, v3, ...)
- Model files committed to Git repository
- Metadata files track version history

**Versioning Strategy**:
- Sequential versioning: v1, v2, v3, ...
- Git commits track model changes
- Metadata JSON files document each version

**Impact**: Simple rollback, clear version history, no external tools required

---

### 3.3 Failure Handling

**Requirement**: The ML Pipeline SHALL implement hybrid error handling: fail fast on critical errors (data generation, preprocessing), continue on model-specific errors.

**Rationale**: Critical errors (data generation, preprocessing) indicate fundamental issues that must be fixed immediately. Model-specific errors (one model fails to train) should not block other models from training.

**Acceptance Criteria**:
- Data generation errors: Fail entire pipeline, log error, exit with non-zero code
- Preprocessing errors: Fail entire pipeline, log error, exit with non-zero code
- Model training errors: Log error, skip failed model, continue with remaining models
- At least 1 model must train successfully for pipeline to succeed

**Error Handling Logic**:
```python
# Critical errors - fail fast
try:
    dataset = generate_dataset()
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
except Exception as e:
    logger.critical(f"Critical error: {e}")
    sys.exit(1)

# Model-specific errors - continue
trained_models = []
for model_config in model_configs:
    try:
        model = train_model(model_config, X_train, y_train)
        trained_models.append(model)
    except Exception as e:
        logger.error(f"Model {model_config['name']} failed: {e}")
        continue

if len(trained_models) == 0:
    logger.critical("All models failed to train")
    sys.exit(1)
```

**Impact**: Balances robustness (partial success) with correctness (fail on critical errors)

---

## 4. Security Requirements

### 4.1 Data Encryption

**Requirement**: The ML Pipeline SHALL NOT encrypt synthetic datasets or trained models at rest.

**Rationale**: Synthetic data contains no sensitive information. Models are trained on synthetic data and do not contain PII or confidential information.

**Acceptance Criteria**:
- Datasets stored as plain CSV files
- Models stored as plain pickle files
- No encryption overhead

**Security Posture**:
- Data is synthetic (no real student data)
- Models trained on synthetic data only
- No PII or confidential information in models
- Access control via filesystem permissions

**Impact**: Simplified storage, no encryption overhead, acceptable risk for synthetic data

---

### 4.2 Dependency Security

**Requirement**: The ML Pipeline SHALL use minor version pinning for all dependencies to balance reproducibility with security updates.

**Rationale**: Exact pinning (scikit-learn==1.3.0) blocks security patches. No pinning breaks reproducibility. Minor version pinning (scikit-learn~=1.3.0) allows patches while blocking breaking changes.

**Acceptance Criteria**:
- All dependencies use minor version pinning (~=)
- Patch updates allowed (1.3.0 → 1.3.1)
- Minor updates blocked (1.3.0 → 1.4.0)
- Major updates blocked (1.3.0 → 2.0.0)

**Dependency Pinning Strategy**:
```
scikit-learn~=1.3.0    # Allows 1.3.x, blocks 1.4.0+
pandas~=2.0.0          # Allows 2.0.x, blocks 2.1.0+
numpy~=1.24.0          # Allows 1.24.x, blocks 1.25.0+
```

**Impact**: Balances reproducibility with security, allows critical patches

---

### 4.3 Model Integrity

**Requirement**: The ML Pipeline SHALL NOT implement model signature verification or integrity checks.

**Rationale**: Models are trained internally in trusted CI/CD environment. No external model sources. Pickle security concerns mitigated by controlled training environment.

**Acceptance Criteria**:
- Models trained in CI/CD pipeline only
- No external model loading
- Git commit history provides audit trail

**Security Posture**:
- Models trained in trusted environment (GitHub Actions)
- No untrusted model sources
- Git provides version control and audit trail
- Pickle acceptable for internal use

**Impact**: Simplified implementation, acceptable risk for internal models

---

## 5. Reliability Requirements

### 5.1 Model Performance Monitoring

**Requirement**: The ML Pipeline SHALL implement basic model performance monitoring with manual review of metrics.

**Rationale**: Comprehensive monitoring (drift detection, alerting) is overkill for project scope. Basic logging of metrics with manual review is sufficient.

**Acceptance Criteria**:
- All 5 metrics logged for each model (accuracy, precision, recall, F1, ROC-AUC)
- Metrics saved to JSON files alongside models
- Cross-validation scores logged
- Performance threshold (80% accuracy) validated and logged

**Monitoring Artifacts**:
- `random_forest_v1_metrics.json` - All metrics
- `training_log.txt` - Training progress and errors
- `evaluation_report.md` - Human-readable report

**Manual Review Process**:
1. Developer reviews metrics after training
2. Compare new model metrics to previous version
3. Decide whether to deploy new model
4. Document decision in Git commit message

**Impact**: Lightweight monitoring, sufficient for project scope, no alerting overhead

---

### 5.2 Data Quality Validation

**Requirement**: The ML Pipeline SHALL enforce all 44 business rules defined in business-rules.md during dataset generation and preprocessing.

**Rationale**: Data quality is critical for model performance. Comprehensive validation prevents training on invalid data.

**Acceptance Criteria**:
- All 6 CRITICAL rules enforced (fail on violation)
- All 21 HIGH rules enforced (fail or correct on violation)
- All 14 MEDIUM rules enforced (warn on violation)
- All 3 LOW rules enforced (log on violation)

**Validation Categories**:
- Data Generation: 11 rules (3 critical, 5 high, 3 medium)
- Data Quality: 4 rules (2 critical, 1 medium, 1 low)
- Data Preprocessing: 6 rules (6 high)
- Feature Engineering: 4 rules (4 medium)
- Model Training: 5 rules (1 critical, 2 high, 2 medium)
- Model Evaluation: 5 rules (3 high, 1 medium, 1 low)
- Model Versioning: 5 rules (2 high, 2 medium, 1 low)
- Error Handling: 4 rules (3 high, 1 medium)

**Impact**: High data quality, comprehensive validation, clear error messages

---

### 5.3 Reproducibility

**Requirement**: The ML Pipeline SHALL ensure critical reproducibility with fixed random seeds and minor version pinning.

**Rationale**: Reproducibility is essential for debugging, validation, and scientific rigor. Fixed random seeds and version pinning enable exact reproduction of results.

**Acceptance Criteria**:
- All random operations use fixed seed (random_state=42)
- Train-test split uses fixed seed (random_state=42)
- Cross-validation uses fixed seed (random_state=42)
- Dependencies use minor version pinning (~=)
- Python version documented in metadata

**Reproducibility Guarantees**:
- **Exact reproduction**: Same code + same dependencies + same seed = identical results
- **Approximate reproduction**: Same code + patch updates + same seed = similar results (±1% metrics)
- **No reproduction**: Different minor versions = potentially different results

**Implementation**:
```python
# Set global random seed
np.random.seed(42)
random.seed(42)

# Use random_state in all operations
train_test_split(..., random_state=42)
StratifiedKFold(..., random_state=42)
RandomForestClassifier(..., random_state=42)
```

**Impact**: Enables debugging, validation, and scientific reproducibility

---

## 6. Maintainability Requirements

### 6.1 Code Quality

**Requirement**: The ML Pipeline SHALL follow PEP 8 coding standards with basic unit testing.

**Rationale**: Code quality standards improve readability and maintainability. Basic testing validates core functionality.

**Acceptance Criteria**:
- All Python code follows PEP 8 (enforced by flake8)
- Unit tests for core functions (data generation, preprocessing, feature engineering)
- Test coverage > 60% for core modules
- No property-based tests (partial enforcement per requirements)

**Testing Scope**:
- Unit tests: Data generation, preprocessing, feature engineering, validation
- No integration tests (tested via full pipeline run)
- No property-based tests (partial enforcement - only for Backend pure functions)

**Code Quality Tools**:
- flake8: PEP 8 linting
- pytest: Unit testing framework
- coverage: Test coverage reporting

**Impact**: Maintainable codebase, basic quality assurance

---

### 6.2 Logging

**Requirement**: The ML Pipeline SHALL implement INFO-level logging for all key operations and milestones.

**Rationale**: INFO-level logging provides sufficient detail for monitoring and debugging without excessive verbosity.

**Acceptance Criteria**:
- All key operations logged at INFO level
- Errors logged at ERROR level with stack traces
- Warnings logged at WARNING level
- Log output to console and file

**Logging Events**:
- Dataset generation start/complete
- Preprocessing start/complete
- Model training start/complete (per model)
- Model evaluation start/complete (per model)
- Model saving start/complete (per model)
- Errors and warnings

**Log Format**:
```
2026-05-05 12:00:00 INFO: Starting dataset generation (target: 1000 records)
2026-05-05 12:00:09 INFO: Dataset generation complete (1000 records, 500 placed, 500 not placed)
2026-05-05 12:00:10 INFO: Starting preprocessing (train-test split, scaling, encoding)
2026-05-05 12:00:12 INFO: Preprocessing complete (800 train, 200 test, 18 features)
2026-05-05 12:00:12 INFO: Starting Random Forest training
2026-05-05 12:00:27 INFO: Random Forest training complete (CV F1: 0.85 ± 0.03)
...
```

**Impact**: Sufficient observability, manageable log volume

---

### 6.3 Documentation

**Requirement**: The ML Pipeline SHALL include comprehensive documentation covering architecture, algorithms, and usage.

**Rationale**: Documentation enables onboarding, maintenance, and knowledge transfer.

**Acceptance Criteria**:
- README.md with overview, setup, and usage instructions
- Inline code comments for complex logic
- Docstrings for all public functions
- Functional design documents (business-logic-model.md, domain-entities.md, business-rules.md)

**Documentation Artifacts**:
- `ml-pipeline/README.md` - Overview and usage
- `aidlc-docs/construction/ml-pipeline/functional-design/` - Detailed design
- Inline comments in code
- Docstrings for functions

**Impact**: Improved maintainability, easier onboarding

---

### 6.4 Configuration Management

**Requirement**: The ML Pipeline SHALL use hybrid configuration (files + environment variables) for flexibility.

**Rationale**: Configuration files for defaults, environment variables for deployment-specific overrides.

**Acceptance Criteria**:
- Default configuration in `config.py` file
- Environment variables override defaults
- No hardcoded values in code

**Configuration Parameters**:
- Dataset size (default: 1000)
- Train-test split ratio (default: 0.80)
- Random seed (default: 42)
- Model hyperparameters (default: predefined values)
- File paths (default: relative paths)

**Configuration Precedence**:
1. Environment variables (highest priority)
2. Configuration file
3. Code defaults (lowest priority)

**Impact**: Flexible configuration, easy deployment customization

---

## 7. Operational Requirements

### 7.1 Deployment Model

**Requirement**: The ML Pipeline SHALL be deployed as part of a single Docker container alongside Backend and Frontend.

**Rationale**: Simplified deployment, no separate ML service, models loaded by Backend at startup.

**Acceptance Criteria**:
- ML Pipeline code included in Docker image
- Models stored in Docker image filesystem
- Backend loads models from filesystem at startup
- No separate ML service or API

**Deployment Architecture**:
```
Docker Container
├── Backend (Flask)
│   ├── Loads models from ml-pipeline/models/trained/
│   └── Serves predictions via REST API
├── ML Pipeline (training scripts)
│   ├── Runs during CI/CD to train models
│   └── Outputs models to ml-pipeline/models/trained/
└── Frontend (static files)
    └── Served by Flask
```

**Impact**: Simple deployment, no microservices complexity

---

### 7.2 CI/CD Integration

**Requirement**: The ML Pipeline SHALL integrate with GitHub Actions CI/CD pipeline for automated training and testing.

**Rationale**: Continuous integration ensures models are retrained and validated on every code change.

**Acceptance Criteria**:
- GitHub Actions workflow triggers on push to main
- Workflow runs dataset generation, training, and evaluation
- Workflow fails if critical errors occur
- Workflow commits trained models to repository

**CI/CD Workflow**:
```yaml
name: ML Pipeline CI/CD
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

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
      - name: Commit models
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add ml-pipeline/models/trained/
          git commit -m "Update trained models [skip ci]"
          git push
```

**Impact**: Automated training, continuous validation, no manual steps

---

### 7.3 Resource Limits

**Requirement**: The ML Pipeline SHALL NOT enforce resource limits (memory, CPU) during training.

**Rationale**: Training workload is predictable and lightweight. Resource limits add complexity without benefit.

**Acceptance Criteria**:
- No memory limits enforced
- No CPU limits enforced
- Training completes successfully on standard hardware (4-core CPU, 8 GB RAM)

**Expected Resource Usage**:
- Memory: ~500 MB peak (dataset + models in memory)
- CPU: 100% utilization during parallel training (desired)
- Disk: ~50 MB (models + datasets)

**Impact**: Simplified implementation, no resource management overhead

---

## 8. Compliance Requirements

### 8.1 Security Baseline Compliance

**Requirement**: The ML Pipeline SHALL comply with all applicable security baseline rules from the Security Extension.

**Rationale**: Security baseline rules are mandatory constraints enforced across all units.

**Applicable Security Rules**:
- **SECURITY-03**: Application-level logging (INFO level, no PII)
- **SECURITY-05**: Input validation (44 business rules enforced)
- **SECURITY-10**: Software supply chain security (minor version pinning, dependency scanning)
- **SECURITY-13**: Software and data integrity (no unsafe deserialization - pickle acceptable for internal use)
- **SECURITY-15**: Exception handling (fail-closed on critical errors, resource cleanup)

**Non-Applicable Security Rules**:
- SECURITY-01: Encryption (N/A - synthetic data, no sensitive info)
- SECURITY-02: Access logging (N/A - no user access, internal training only)
- SECURITY-04: HTTP security headers (N/A - no HTTP interface)
- SECURITY-06: Least-privilege access (N/A - no database access)
- SECURITY-07: Network configuration (N/A - no network access)
- SECURITY-08: Access control (N/A - no user access)
- SECURITY-09: Security hardening (N/A - no credentials, no stack traces in logs)
- SECURITY-11: Secure design (N/A - no rate limiting, no user input)
- SECURITY-12: Authentication (N/A - no authentication required)
- SECURITY-14: Alerting and monitoring (Basic logging only, no alerting)

**Impact**: Compliant with applicable security rules, N/A for non-applicable rules

---

### 8.2 Property-Based Testing Compliance

**Requirement**: The ML Pipeline SHALL NOT implement property-based testing (partial enforcement - Backend only).

**Rationale**: Property-based testing extension is partially enforced (pure functions + serialization only). ML Pipeline has no pure functions suitable for PBT.

**Acceptance Criteria**:
- No property-based tests in ML Pipeline
- Unit tests only (pytest)
- PBT reserved for Backend pure functions

**Impact**: Simplified testing, no PBT overhead for ML Pipeline

---

## NFR Summary Matrix

| Category | Requirement | Priority | Acceptance Criteria |
|----------|-------------|----------|---------------------|
| **Scalability** | Fixed dataset size (~1000 records) | Medium | Dataset generation produces 1000-1200 records |
| **Scalability** | Parallel model training | High | All 4 models train in parallel |
| **Scalability** | Local filesystem storage | High | All models stored in ml-pipeline/models/trained/ |
| **Performance** | Training duration < 1 minute | High | Total training time < 60 seconds |
| **Performance** | Dataset generation < 10 seconds | Medium | Generate 1000 records in < 10 seconds |
| **Performance** | CPU-only training | High | No GPU required, CPU sufficient |
| **Availability** | Frequent retraining (daily/on push) | High | Automated CI/CD triggers |
| **Availability** | Git-based versioning | High | Sequential versions (v1, v2, v3) |
| **Availability** | Hybrid error handling | High | Fail fast on critical, continue on model errors |
| **Security** | No encryption (synthetic data) | Low | Plain CSV and pickle files |
| **Security** | Minor version pinning | High | Dependencies use ~= pinning |
| **Security** | No model integrity checks | Low | Models trained internally only |
| **Reliability** | Basic performance monitoring | Medium | Metrics logged, manual review |
| **Reliability** | 44 business rules enforced | High | All rules validated |
| **Reliability** | Critical reproducibility | High | Fixed seeds, version pinning |
| **Maintainability** | PEP 8 + basic unit tests | Medium | flake8 + pytest, >60% coverage |
| **Maintainability** | INFO-level logging | High | All key operations logged |
| **Maintainability** | Comprehensive documentation | Medium | README + design docs + docstrings |
| **Maintainability** | Hybrid configuration | Medium | Files + env vars |
| **Operational** | Single container deployment | High | ML + Backend + Frontend in one container |
| **Operational** | GitHub Actions CI/CD | High | Automated training on push |
| **Operational** | No resource limits | Low | No memory/CPU limits enforced |
| **Compliance** | Security baseline (applicable rules) | High | 5 applicable rules enforced |
| **Compliance** | No property-based testing | Low | Unit tests only |

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC NFR Requirements
- **Next**: tech-stack-decisions.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial NFR requirements document |
