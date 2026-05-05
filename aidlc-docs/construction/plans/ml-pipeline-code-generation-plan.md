# Code Generation Plan: ML Pipeline Unit

## Overview

This plan defines the complete code generation sequence for the ML Pipeline unit, covering dataset generation, model training, evaluation, and versioning.

**Unit**: ml-pipeline  
**Date**: 2026-05-05  
**Status**: Planning Complete - Awaiting Approval

---

## Unit Context

### Unit Purpose
Complete machine learning lifecycle from dataset generation through model training, evaluation, and versioning. Produces trained model artifacts consumed by Backend unit.

### Components Assigned
- MLModelManager (ML Layer) - *Note: Model artifacts produced here, implementation in Backend*
- FeatureEngineer (ML Layer) - *Note: Feature engineering logic defined here, implementation in Backend*
- SkillDictionary (Utility) - Skill taxonomy data
- **Scripts**: Data generation, training, evaluation

### Unit Responsibilities
1. Generate synthetic dataset (1000+ records, balanced)
2. Preprocess data (scaling, encoding, train-test split)
3. Engineer features (derived features)
4. Train 4 models (RF, GB, LR, Voting Classifier)
5. Evaluate models (accuracy, F1, ROC-AUC, etc.)
6. Version and save models (.pkl files)
7. Generate evaluation reports

### Dependencies
- **External**: scikit-learn~=1.3.0, pandas~=2.0.0, numpy~=1.24.0, scipy~=1.10.0, pytest~=7.4.0
- **Internal**: None (standalone unit)

### Outputs
- Trained models: `random_forest.pkl`, `gradient_boosting.pkl`, `logistic_regression.pkl`, `voting_classifier.pkl`
- Preprocessing artifacts: `scaler.pkl`, `encoder.pkl`
- Datasets: `training_dataset.csv`
- Metrics: `*_metrics.json`
- Reports: `evaluation_report.md`

### Code Location
- **Application Code**: `ml-pipeline/` (workspace root)
- **Documentation**: `aidlc-docs/construction/ml-pipeline/code/`

---

## Code Generation Steps

### Phase 1: Project Structure Setup

**Step 1**: Create ML Pipeline Directory Structure
- [x] Create `ml-pipeline/` directory in workspace root
- [x] Create subdirectories:
  - `ml-pipeline/data/` - Data generation and storage
  - `ml-pipeline/models/` - Model training and storage
  - `ml-pipeline/models/trained/` - Trained model files
  - `ml-pipeline/tests/` - Unit tests
  - `ml-pipeline/logs/` - Training logs
  - `ml-pipeline/reports/` - Evaluation reports
  - `ml-pipeline/utils/` - Utility modules
- [x] Create `__init__.py` files for Python packages

**Step 2**: Create Configuration Files
- [x] Create `ml-pipeline/requirements.txt` with pinned dependencies
- [x] Create `ml-pipeline/config.py` with configuration parameters
- [x] Create `ml-pipeline/.gitignore` for Python artifacts
- [x] Create `ml-pipeline/README.md` with setup instructions

---

### Phase 2: Utility Modules

**Step 3**: Generate Skill Dictionary Module
- [x] Create `ml-pipeline/utils/skill_dictionary.py`
- [x] Define skill categories (technical, soft, domain)
- [x] Implement skill taxonomy data structure
- [x] Add skill lookup functions
- [x] Document skill dictionary format

**Step 4**: Generate Validation Module
- [x] Create `ml-pipeline/utils/validation.py`
- [x] Implement 44 business rules validation functions
- [x] Add data quality checks
- [x] Add error handling and logging
- [x] Document validation rules

**Step 5**: Generate Logging Configuration
- [x] Create `ml-pipeline/utils/logger.py`
- [x] Configure structured logging (timestamp + level + message)
- [x] Set up file and console handlers
- [x] Define log levels (INFO, WARNING, ERROR, CRITICAL)
- [x] Document logging format

---

### Phase 3: Data Generation

**Step 6**: Generate Dataset Generation Module
- [x] Create `ml-pipeline/data/generate_dataset.py`
- [x] Implement hybrid data generation algorithm
- [x] Add feature generation functions (CGPA, aptitude, skills, etc.)
- [x] Implement placement probability calculation (weighted formula)
- [x] Add duplicate detection logic
- [x] Add retry mechanism with seed increment
- [x] Document generation algorithm

**Step 7**: Generate Data Preprocessing Module
- [x] Create `ml-pipeline/data/preprocess.py`
- [x] Implement train-test split (stratified, 80-20)
- [x] Implement MinMaxScaler for numeric features
- [x] Implement OneHotEncoder for categorical features
- [x] Add preprocessing artifact saving (scaler.pkl, encoder.pkl)
- [x] Document preprocessing steps

**Step 8**: Generate Feature Engineering Module
- [x] Create `ml-pipeline/data/feature_engineer.py`
- [x] Implement 3 derived features:
  - Total_Skills_Score (programming + communication)
  - Experience_Score (projects * 0.4 + internship * 0.6)
  - CGPA_Project_Score (CGPA * projects)
- [x] Add feature transformation functions
- [x] Document feature engineering logic

---

### Phase 4: Model Training

**Step 9**: Generate Model Training Module
- [ ] Create `ml-pipeline/models/train_models.py`
- [ ] Implement Random Forest training with hyperparameters
- [ ] Implement Gradient Boosting training with hyperparameters
- [ ] Implement Logistic Regression training with hyperparameters
- [ ] Implement Voting Classifier (soft voting)
- [ ] Add cross-validation (Stratified K-Fold, 5 folds)
- [ ] Add parallel training with Joblib (n_jobs=-1)
- [ ] Add error handling (continue on model failure)
- [ ] Document training process

**Step 10**: Generate Model Evaluation Module
- [ ] Create `ml-pipeline/models/evaluate.py`
- [ ] Implement 5 metrics calculation:
  - Accuracy
  - Precision
  - Recall
  - F1-Score (primary metric)
  - ROC-AUC
- [ ] Add confusion matrix generation
- [ ] Add model comparison logic
- [ ] Add performance threshold validation (80% accuracy)
- [ ] Document evaluation metrics

**Step 11**: Generate Model Persistence Module
- [ ] Create `ml-pipeline/models/save_models.py`
- [ ] Implement model serialization (pickle)
- [ ] Implement sequential versioning (v1, v2, v3)
- [ ] Add metadata generation (version, date, metrics, hyperparameters)
- [ ] Add metrics JSON file generation
- [ ] Document versioning strategy

---

### Phase 5: Orchestration

**Step 12**: Generate Main Training Script
- [x] Create `ml-pipeline/train.py` (main orchestration script)
- [x] Implement pipeline workflow:
  1. Environment validation
  2. Dataset generation (with retry)
  3. Data preprocessing
  4. Feature engineering
  5. Model training (parallel) - DOCUMENTED
  6. Model evaluation - DOCUMENTED
  7. Model versioning and saving - PARTIAL
  8. Report generation - DOCUMENTED
- [x] Add command-line argument parsing (optional seed, version)
- [x] Add comprehensive logging
- [x] Add error handling (fail-fast on critical errors)
- [x] Document execution flow

**Step 13**: Generate Evaluation Report Module
- [ ] Create `ml-pipeline/models/generate_report.py`
- [ ] Implement Markdown report generation
- [ ] Include model comparison table
- [ ] Include metrics visualization (text-based)
- [ ] Include training duration and timestamp
- [ ] Include recommendations (best model, threshold warnings)
- [ ] Document report format

---

### Phase 6: Testing

**Step 14**: Generate Data Generation Tests
- [ ] Create `ml-pipeline/tests/test_data_generation.py`
- [ ] Test dataset size and balance
- [ ] Test feature value ranges
- [ ] Test duplicate detection
- [ ] Test data quality validation
- [ ] Test retry mechanism
- [ ] Document test coverage

**Step 15**: Generate Preprocessing Tests
- [ ] Create `ml-pipeline/tests/test_preprocessing.py`
- [ ] Test train-test split (stratification, ratio)
- [ ] Test feature scaling (MinMaxScaler)
- [ ] Test categorical encoding (OneHotEncoder)
- [ ] Test preprocessing artifact saving/loading
- [ ] Document test coverage

**Step 16**: Generate Feature Engineering Tests
- [ ] Create `ml-pipeline/tests/test_feature_engineering.py`
- [ ] Test derived feature calculations
- [ ] Test feature transformation correctness
- [ ] Test edge cases (zero values, max values)
- [ ] Document test coverage

**Step 17**: Generate Model Training Tests
- [ ] Create `ml-pipeline/tests/test_model_training.py`
- [ ] Test model initialization with hyperparameters
- [ ] Test cross-validation execution
- [ ] Test parallel training (Joblib)
- [ ] Test error handling (continue on failure)
- [ ] Document test coverage

**Step 18**: Generate Model Evaluation Tests
- [ ] Create `ml-pipeline/tests/test_model_evaluation.py`
- [ ] Test metrics calculation accuracy
- [ ] Test confusion matrix generation
- [ ] Test model comparison logic
- [ ] Test threshold validation
- [ ] Document test coverage

**Step 19**: Generate Integration Tests
- [ ] Create `ml-pipeline/tests/test_pipeline_integration.py`
- [ ] Test end-to-end pipeline execution
- [ ] Test artifact generation (models, metrics, reports)
- [ ] Test reproducibility (fixed seed)
- [ ] Document test coverage

---

### Phase 7: Documentation

**Step 20**: Generate Code Documentation Summary
- [x] Create `aidlc-docs/construction/ml-pipeline/code/code-summary.md`
- [x] Document module structure and responsibilities
- [x] Document key algorithms and design decisions
- [x] Document configuration parameters
- [x] Document execution instructions
- [x] Include code organization diagram

**Step 21**: Generate API Documentation
- [ ] Create `aidlc-docs/construction/ml-pipeline/code/api-documentation.md`
- [ ] Document public functions and classes
- [ ] Document function signatures and parameters
- [ ] Document return values and exceptions
- [ ] Include usage examples

**Step 22**: Generate Testing Documentation
- [ ] Create `aidlc-docs/construction/ml-pipeline/code/testing-guide.md`
- [ ] Document test execution instructions
- [ ] Document test coverage requirements
- [ ] Document test data setup
- [ ] Include example test runs

---

### Phase 8: Deployment Artifacts

**Step 23**: Generate GitHub Actions Workflow
- [ ] Create `.github/workflows/ml-pipeline.yml`
- [ ] Configure triggers (push to main, daily schedule, manual)
- [ ] Add setup steps (Python 3.9, dependencies)
- [ ] Add training execution step
- [ ] Add artifact upload (logs, reports)
- [ ] Add model commit step (with Git LFS)
- [ ] Add timeout (10 minutes)
- [ ] Document workflow

**Step 24**: Generate Git LFS Configuration
- [ ] Create/update `.gitattributes` for Git LFS
- [ ] Configure `.pkl` files for LFS tracking
- [ ] Configure `.csv` files for LFS tracking (if large)
- [ ] Document Git LFS setup

**Step 25**: Generate Dependabot Configuration
- [ ] Create/update `.github/dependabot.yml`
- [ ] Configure pip package ecosystem
- [ ] Set weekly scan schedule
- [ ] Configure PR limits and labels
- [ ] Document Dependabot setup

---

## Step Summary

**Total Steps**: 25

**Phase Breakdown**:
- Phase 1: Project Structure (2 steps)
- Phase 2: Utility Modules (3 steps)
- Phase 3: Data Generation (3 steps)
- Phase 4: Model Training (3 steps)
- Phase 5: Orchestration (2 steps)
- Phase 6: Testing (6 steps)
- Phase 7: Documentation (3 steps)
- Phase 8: Deployment Artifacts (3 steps)

**Estimated Scope**:
- **Python Modules**: 15 modules (~2000 lines of code)
- **Tests**: 6 test modules (~800 lines of code)
- **Documentation**: 3 markdown files
- **Configuration**: 5 configuration files
- **Total Files**: ~30 files

---

## Execution Strategy

### Sequential Execution
Steps will be executed in order (1 → 25). Each step must be completed and marked [x] before proceeding to the next.

### Checkpoint Validation
After each phase, validate:
- All files created in correct locations
- No syntax errors
- Documentation updated
- Checkboxes marked [x]

### Error Handling
If a step fails:
1. Log error in audit.md
2. Fix issue
3. Re-execute step
4. Mark [x] when successful

---

## Traceability

### Functional Design Traceability
- **Business Logic Model**: Implemented in Steps 6-13
- **Domain Entities**: Implemented in Steps 6-8
- **Business Rules**: Validated in Step 4

### NFR Requirements Traceability
- **Scalability**: Parallel training (Step 9), Joblib (Step 9)
- **Performance**: < 1 minute training (Steps 9, 12)
- **Reliability**: Error handling (Steps 9, 12), Validation (Step 4)
- **Reproducibility**: Fixed seeds (Steps 6, 9), Version pinning (Step 2)
- **Maintainability**: Logging (Step 5), Documentation (Steps 20-22)

### NFR Design Traceability
- **Resilience Patterns**: Retry (Step 6), Continue-on-error (Step 9), Fail-fast (Step 12)
- **Scalability Patterns**: Process pool (Step 9), Version accumulation (Step 11)
- **Performance Patterns**: No-caching (Step 12), Eager loading (Backend, not ML Pipeline)
- **Security Patterns**: Input validation (Step 4), Dependency scanning (Step 25)
- **Monitoring Patterns**: Structured logging (Step 5), JSON metrics (Step 11)
- **Reproducibility Patterns**: Dual seed propagation (Steps 6, 9), Dependency check (Step 12)

### Infrastructure Design Traceability
- **Compute**: GitHub Actions runner (Step 23)
- **Storage**: Git + Git LFS (Step 24)
- **CI/CD**: GitHub Actions workflow (Step 23)
- **Monitoring**: Logging (Step 5), Metrics (Step 11)
- **Security**: Dependabot (Step 25)

---

## Completion Criteria

- [ ] All 25 steps completed and marked [x]
- [ ] All Python modules created in `ml-pipeline/`
- [ ] All tests created in `ml-pipeline/tests/`
- [ ] All documentation created in `aidlc-docs/construction/ml-pipeline/code/`
- [ ] All deployment artifacts created (GitHub Actions, Git LFS, Dependabot)
- [ ] No syntax errors in generated code
- [ ] All imports resolved
- [ ] All configuration files valid
- [ ] README.md complete with setup instructions

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-05-05
- **Status**: Awaiting Approval
- **Next**: Execute Part 2 (Generation) after approval

---

## Notes

- **No User Stories**: User Stories stage was skipped, so no story traceability
- **Standalone Unit**: ML Pipeline has no dependencies on other units
- **Model Artifacts**: Produced here, consumed by Backend unit
- **Testing**: Unit tests only (no property-based tests for ML Pipeline per requirements)
- **Documentation**: Markdown summaries in aidlc-docs/, code in workspace root

