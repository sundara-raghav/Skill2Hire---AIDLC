# Business Rules: ML Pipeline Unit

## Overview

This document defines all business rules, validation logic, and constraints for the ML Pipeline unit.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## Rule Categories

1. Data Generation Rules
2. Data Quality Rules
3. Data Preprocessing Rules
4. Feature Engineering Rules
5. Model Training Rules
6. Model Evaluation Rules
7. Model Versioning Rules
8. Error Handling Rules

---

## 1. Data Generation Rules

### RULE-DG-001: Minimum Dataset Size
**Priority**: CRITICAL  
**Category**: Data Generation

**Rule**: The synthetic dataset MUST contain at least 1000 student records.

**Rationale**: Minimum sample size required for reliable model training and evaluation.

**Validation**:
```python
assert len(dataset) >= 1000, "Dataset must contain at least 1000 records"
```

**Action on Violation**: Fail dataset generation, log error

---

### RULE-DG-002: Balanced Dataset
**Priority**: CRITICAL  
**Category**: Data Generation

**Rule**: The dataset MUST be balanced with 50% placed and 50% not placed students (±2% tolerance).

**Rationale**: Prevent model bias toward majority class.

**Validation**:
```python
placed_ratio = placed_count / total_records
assert 0.48 <= placed_ratio <= 0.52, f"Dataset imbalanced: {placed_ratio:.2%}"
```

**Action on Violation**: Adjust placement threshold to rebalance, regenerate if needed

---

### RULE-DG-003: No Duplicate Records
**Priority**: CRITICAL  
**Category**: Data Generation

**Rule**: All student records MUST be unique (no duplicate feature combinations).

**Rationale**: Duplicates inflate dataset size artificially and skew model training.

**Validation**:
```python
unique_records = dataset.drop_duplicates()
assert len(unique_records) == len(dataset), "Duplicate records found"
```

**Action on Violation**: Remove duplicates, regenerate to reach target size

---

### RULE-DG-004: CGPA Range
**Priority**: HIGH  
**Category**: Data Generation

**Rule**: CGPA values MUST be between 0.0 and 10.0 (inclusive).

**Rationale**: Standard CGPA scale in Indian education system.

**Validation**:
```python
assert dataset['cgpa'].between(0.0, 10.0).all(), "CGPA out of range"
```

**Action on Violation**: Clip values to valid range

---

### RULE-DG-005: Aptitude Score Range
**Priority**: HIGH  
**Category**: Data Generation

**Rule**: Aptitude scores MUST be between 0 and 100 (inclusive).

**Rationale**: Standard percentage-based scoring.

**Validation**:
```python
assert dataset['aptitude_score'].between(0, 100).all(), "Aptitude score out of range"
```

**Action on Violation**: Clip values to valid range

---

### RULE-DG-006: Skills Rating Range
**Priority**: HIGH  
**Category**: Data Generation

**Rule**: Programming and communication skills MUST be rated between 1 and 10 (inclusive).

**Rationale**: Standard 1-10 rating scale.

**Validation**:
```python
assert dataset['programming_skills'].between(1, 10).all(), "Programming skills out of range"
assert dataset['communication_skills'].between(1, 10).all(), "Communication skills out of range"
```

**Action on Violation**: Clip values to valid range

---

### RULE-DG-007: Projects Count Range
**Priority**: MEDIUM  
**Category**: Data Generation

**Rule**: Number of projects MUST be between 0 and 10 (inclusive).

**Rationale**: Realistic upper bound for student projects.

**Validation**:
```python
assert dataset['num_projects'].between(0, 10).all(), "Projects count out of range"
```

**Action on Violation**: Clip values to valid range

---

### RULE-DG-008: Certifications Count Range
**Priority**: MEDIUM  
**Category**: Data Generation

**Rule**: Certifications count MUST be between 0 and 10 (inclusive).

**Rationale**: Realistic upper bound for student certifications.

**Validation**:
```python
assert dataset['certifications_count'].between(0, 10).all(), "Certifications count out of range"
```

**Action on Violation**: Clip values to valid range

---

### RULE-DG-009: Valid Branch Values
**Priority**: HIGH  
**Category**: Data Generation

**Rule**: Branch MUST be one of: CS, IT, ECE, EEE, Mechanical, Civil, Chemical, Other.

**Rationale**: Predefined set of academic branches.

**Validation**:
```python
valid_branches = ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']
assert dataset['branch'].isin(valid_branches).all(), "Invalid branch value"
```

**Action on Violation**: Fail validation, log error

---

### RULE-DG-010: Realistic Branch Distribution
**Priority**: MEDIUM  
**Category**: Data Generation

**Rule**: Branch distribution SHOULD follow realistic proportions (CS: 25%, IT: 20%, ECE: 15%, EEE: 12%, Mechanical: 10%, Civil: 8%, Chemical: 5%, Other: 5%).

**Rationale**: Reflect real-world enrollment patterns.

**Validation**:
```python
actual_dist = dataset['branch'].value_counts(normalize=True)
expected_dist = {'CS': 0.25, 'IT': 0.20, 'ECE': 0.15, ...}
# Allow ±5% deviation
for branch, expected in expected_dist.items():
    actual = actual_dist.get(branch, 0)
    assert abs(actual - expected) <= 0.05, f"Branch {branch} distribution off: {actual:.2%}"
```

**Action on Violation**: Warn, continue (not critical)

---

### RULE-DG-011: Moderate Feature Correlations
**Priority**: MEDIUM  
**Category**: Data Generation

**Rule**: Features SHOULD exhibit moderate correlations (e.g., CGPA and skills, projects and internships).

**Rationale**: Realistic data patterns improve model generalization.

**Validation**:
```python
corr_matrix = dataset.corr()
# Check key correlations exist
assert 0.2 <= corr_matrix.loc['cgpa', 'programming_skills'] <= 0.6, "CGPA-skills correlation weak"
```

**Action on Violation**: Warn, continue (not critical)

---

## 2. Data Quality Rules

### RULE-DQ-001: No Missing Values
**Priority**: CRITICAL  
**Category**: Data Quality

**Rule**: The dataset MUST NOT contain any missing (null/NaN) values.

**Rationale**: Synthetic dataset is fully controlled, no missing values should exist.

**Validation**:
```python
assert dataset.isnull().sum().sum() == 0, "Dataset contains missing values"
```

**Action on Violation**: Fail validation, regenerate dataset

---

### RULE-DQ-002: Correct Data Types
**Priority**: CRITICAL  
**Category**: Data Quality

**Rule**: All fields MUST have correct data types (float for CGPA/aptitude, int for skills/projects/certs, bool for internship, str for branch).

**Rationale**: Type safety for downstream processing.

**Validation**:
```python
assert dataset['cgpa'].dtype == float, "CGPA must be float"
assert dataset['programming_skills'].dtype == int, "Programming skills must be int"
assert dataset['internship_experience'].dtype == bool, "Internship must be bool"
assert dataset['branch'].dtype == object, "Branch must be string"
```

**Action on Violation**: Convert to correct type, warn if conversion fails

---

### RULE-DQ-003: Statistical Distribution Checks
**Priority**: MEDIUM  
**Category**: Data Quality

**Rule**: Numeric features SHOULD follow expected distributions (CGPA: normal, skills: uniform-ish).

**Rationale**: Detect anomalies in data generation.

**Validation**:
```python
from scipy import stats
# Test CGPA normality
_, p_value = stats.normaltest(dataset['cgpa'])
assert p_value > 0.01, "CGPA distribution not normal"
```

**Action on Violation**: Warn, continue (not critical)

---

### RULE-DQ-004: Outlier Detection
**Priority**: LOW  
**Category**: Data Quality

**Rule**: Extreme outliers SHOULD be investigated (values beyond 3 standard deviations).

**Rationale**: Detect potential data generation bugs.

**Validation**:
```python
for col in ['cgpa', 'aptitude_score']:
    mean = dataset[col].mean()
    std = dataset[col].std()
    outliers = dataset[(dataset[col] < mean - 3*std) | (dataset[col] > mean + 3*std)]
    if len(outliers) > 0:
        print(f"Warning: {len(outliers)} outliers in {col}")
```

**Action on Violation**: Warn, continue

---

## 3. Data Preprocessing Rules

### RULE-DP-001: Train-Test Split Ratio
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: Dataset MUST be split into 80% training and 20% testing.

**Rationale**: Standard split ratio for adequate training and evaluation.

**Validation**:
```python
assert len(X_train) / len(X) == 0.80, "Train set must be 80%"
assert len(X_test) / len(X) == 0.20, "Test set must be 20%"
```

**Action on Violation**: Fail preprocessing, log error

---

### RULE-DP-002: Stratified Split
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: Train-test split MUST be stratified to preserve class balance in both sets.

**Rationale**: Ensure both sets are representative of overall distribution.

**Validation**:
```python
train_placed_ratio = y_train.sum() / len(y_train)
test_placed_ratio = y_test.sum() / len(y_test)
assert abs(train_placed_ratio - 0.50) <= 0.05, "Train set imbalanced"
assert abs(test_placed_ratio - 0.50) <= 0.05, "Test set imbalanced"
```

**Action on Violation**: Fail preprocessing, resplit with stratification

---

### RULE-DP-003: Feature Scaling Required
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: All numeric features MUST be scaled using MinMaxScaler before training.

**Rationale**: Normalize feature ranges for model convergence.

**Validation**:
```python
# After scaling
for col in numeric_features:
    assert X_train[col].min() >= 0.0, f"{col} min < 0 after scaling"
    assert X_train[col].max() <= 1.0, f"{col} max > 1 after scaling"
```

**Action on Violation**: Fail preprocessing, apply scaling

---

### RULE-DP-004: Categorical Encoding Required
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: Branch feature MUST be one-hot encoded before training.

**Rationale**: Convert categorical to numeric for model input.

**Validation**:
```python
# After encoding
branch_cols = [col for col in X_train.columns if col.startswith('branch_')]
assert len(branch_cols) == 8, "Must have 8 branch columns after encoding"
assert X_train[branch_cols].sum(axis=1).eq(1).all(), "Each row must have exactly one branch"
```

**Action on Violation**: Fail preprocessing, apply encoding

---

### RULE-DP-005: Scaler Persistence
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: MinMaxScaler object MUST be saved for use in Backend inference.

**Rationale**: Ensure consistent scaling in production.

**Validation**:
```python
assert os.path.exists('ml-pipeline/models/trained/scaler_v1.pkl'), "Scaler not saved"
```

**Action on Violation**: Fail preprocessing, save scaler

---

### RULE-DP-006: Encoder Persistence
**Priority**: HIGH  
**Category**: Data Preprocessing

**Rule**: OneHotEncoder object MUST be saved for use in Backend inference.

**Rationale**: Ensure consistent encoding in production.

**Validation**:
```python
assert os.path.exists('ml-pipeline/models/trained/encoder_v1.pkl'), "Encoder not saved"
```

**Action on Violation**: Fail preprocessing, save encoder

---

## 4. Feature Engineering Rules

### RULE-FE-001: Derived Features Required
**Priority**: MEDIUM  
**Category**: Feature Engineering

**Rule**: Three derived features MUST be created: Total_Skills_Score, Experience_Score, CGPA_Project_Score.

**Rationale**: Enhance model performance with engineered features.

**Validation**:
```python
required_features = ['Total_Skills_Score', 'Experience_Score', 'CGPA_Project_Score']
for feature in required_features:
    assert feature in X_train.columns, f"Missing derived feature: {feature}"
```

**Action on Violation**: Fail feature engineering, create features

---

### RULE-FE-002: Total_Skills_Score Calculation
**Priority**: MEDIUM  
**Category**: Feature Engineering

**Rule**: Total_Skills_Score MUST equal Programming_Skills + Communication_Skills.

**Rationale**: Aggregate skills measure.

**Validation**:
```python
expected = X_train['programming_skills'] + X_train['communication_skills']
assert (X_train['Total_Skills_Score'] == expected).all(), "Total_Skills_Score incorrect"
```

**Action on Violation**: Recalculate feature

---

### RULE-FE-003: Experience_Score Calculation
**Priority**: MEDIUM  
**Category**: Feature Engineering

**Rule**: Experience_Score MUST equal (Num_Projects * 0.4) + (Internship_Experience * 0.6).

**Rationale**: Weighted experience measure.

**Validation**:
```python
expected = (X_train['num_projects'] * 0.4) + (X_train['internship_experience'] * 0.6)
assert np.allclose(X_train['Experience_Score'], expected), "Experience_Score incorrect"
```

**Action on Violation**: Recalculate feature

---

### RULE-FE-004: CGPA_Project_Score Calculation
**Priority**: MEDIUM  
**Category**: Feature Engineering

**Rule**: CGPA_Project_Score MUST equal CGPA * Num_Projects.

**Rationale**: Interaction term between academics and projects.

**Validation**:
```python
expected = X_train['cgpa'] * X_train['num_projects']
assert np.allclose(X_train['CGPA_Project_Score'], expected), "CGPA_Project_Score incorrect"
```

**Action on Violation**: Recalculate feature

---

## 5. Model Training Rules

### RULE-MT-001: Minimum Training Set Size
**Priority**: CRITICAL  
**Category**: Model Training

**Rule**: Training set MUST contain at least 800 records (80% of 1000).

**Rationale**: Sufficient data for model learning.

**Validation**:
```python
assert len(X_train) >= 800, "Training set too small"
```

**Action on Violation**: Fail training, increase dataset size

---

### RULE-MT-002: Cross-Validation Required
**Priority**: HIGH  
**Category**: Model Training

**Rule**: All models MUST be validated using 5-fold stratified cross-validation.

**Rationale**: Detect overfitting and validate generalization.

**Validation**:
```python
assert cv.get_n_splits() == 5, "Must use 5-fold CV"
assert isinstance(cv, StratifiedKFold), "Must use stratified CV"
```

**Action on Violation**: Fail training, apply CV

---

### RULE-MT-003: Manual Hyperparameters
**Priority**: MEDIUM  
**Category**: Model Training

**Rule**: Models MUST use predefined hyperparameters (no tuning required).

**Rationale**: Simplify training process, use known good parameters.

**Validation**:
```python
# Verify hyperparameters match predefined values
assert rf_model.n_estimators == 100, "RF n_estimators incorrect"
assert gb_model.learning_rate == 0.1, "GB learning_rate incorrect"
```

**Action on Violation**: Warn, continue

---

### RULE-MT-004: Soft Voting Ensemble
**Priority**: HIGH  
**Category**: Model Training

**Rule**: Voting Classifier MUST use soft voting (average probabilities).

**Rationale**: Leverage probability estimates for better ensemble.

**Validation**:
```python
assert voting_clf.voting == 'soft', "Voting Classifier must use soft voting"
```

**Action on Violation**: Fail training, set voting='soft'

---

### RULE-MT-005: Random State Consistency
**Priority**: MEDIUM  
**Category**: Model Training

**Rule**: All models SHOULD use random_state=42 for reproducibility.

**Rationale**: Enable reproducible results.

**Validation**:
```python
assert rf_model.random_state == 42, "RF random_state not set"
assert gb_model.random_state == 42, "GB random_state not set"
```

**Action on Violation**: Warn, continue

---

## 6. Model Evaluation Rules

### RULE-ME-001: All Metrics Required
**Priority**: HIGH  
**Category**: Model Evaluation

**Rule**: All 5 metrics MUST be calculated: accuracy, precision, recall, F1-score, ROC-AUC.

**Rationale**: Comprehensive performance assessment.

**Validation**:
```python
required_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
for metric in required_metrics:
    assert metric in evaluation_metrics, f"Missing metric: {metric}"
```

**Action on Violation**: Fail evaluation, calculate all metrics

---

### RULE-ME-002: F1-Score Priority
**Priority**: HIGH  
**Category**: Model Evaluation

**Rule**: F1-Score MUST be used as primary metric for model selection.

**Rationale**: Balance between precision and recall.

**Validation**:
```python
# Model comparison should sort by F1-score first
best_model = max(models, key=lambda m: m.metrics['f1_score'])
```

**Action on Violation**: Adjust model selection logic

---

### RULE-ME-003: Performance Threshold
**Priority**: HIGH  
**Category**: Model Evaluation

**Rule**: Models SHOULD achieve at least 80% accuracy on test set.

**Rationale**: Minimum acceptable performance level.

**Validation**:
```python
if metrics['accuracy'] < 0.80:
    logger.warning(f"Model accuracy {metrics['accuracy']:.2%} below 80% threshold")
```

**Action on Violation**: Warn, save model anyway (for debugging)

---

### RULE-ME-004: Confusion Matrix Required
**Priority**: MEDIUM  
**Category**: Model Evaluation

**Rule**: Confusion matrix MUST be generated for each model.

**Rationale**: Understand error patterns (false positives vs false negatives).

**Validation**:
```python
assert 'confusion_matrix' in evaluation_metrics, "Confusion matrix missing"
assert len(evaluation_metrics['confusion_matrix']) == 2, "Confusion matrix must be 2x2"
```

**Action on Violation**: Fail evaluation, generate confusion matrix

---

### RULE-ME-005: Feature Importance for Tree Models
**Priority**: LOW  
**Category**: Model Evaluation

**Rule**: Feature importance SHOULD be calculated for Random Forest and Gradient Boosting.

**Rationale**: Understand which features drive predictions.

**Validation**:
```python
if model_name in ['random_forest', 'gradient_boosting']:
    assert 'feature_importance' in evaluation_metrics, "Feature importance missing"
```

**Action on Violation**: Warn, continue

---

## 7. Model Versioning Rules

### RULE-MV-001: Sequential Versioning
**Priority**: HIGH  
**Category**: Model Versioning

**Rule**: Model versions MUST follow sequential format: v1, v2, v3, ...

**Rationale**: Simple, predictable versioning scheme.

**Validation**:
```python
assert re.match(r'^v\d+$', version), "Version must be v1, v2, v3, etc."
```

**Action on Violation**: Fail versioning, correct format

---

### RULE-MV-002: Metadata Required
**Priority**: HIGH  
**Category**: Model Versioning

**Rule**: Model metadata MUST be saved alongside .pkl file.

**Rationale**: Track model provenance and performance.

**Validation**:
```python
pkl_file = 'random_forest_v1.pkl'
metadata_file = 'random_forest_v1_metadata.json'
assert os.path.exists(metadata_file), "Metadata file missing"
```

**Action on Violation**: Fail versioning, save metadata

---

### RULE-MV-003: Metadata Content
**Priority**: MEDIUM  
**Category**: Model Versioning

**Rule**: Metadata MUST include: version, date, metrics, hyperparameters, dataset info, scikit-learn version.

**Rationale**: Complete model documentation.

**Validation**:
```python
required_fields = ['version', 'training_date', 'metrics', 'hyperparameters', 
                   'dataset_info', 'scikit_learn_version']
for field in required_fields:
    assert field in metadata, f"Missing metadata field: {field}"
```

**Action on Violation**: Fail versioning, add missing fields

---

### RULE-MV-004: Model Replacement Criteria
**Priority**: MEDIUM  
**Category**: Model Versioning

**Rule**: New model SHOULD replace existing model only if accuracy improves.

**Rationale**: Prevent regression in model performance.

**Validation**:
```python
if existing_model_metadata:
    if new_metrics['accuracy'] <= existing_metrics['accuracy']:
        logger.warning("New model does not improve accuracy, not replacing")
```

**Action on Violation**: Warn, keep existing model

---

### RULE-MV-005: Backward Compatibility
**Priority**: LOW  
**Category**: Model Versioning

**Rule**: New model versions SHOULD maintain same feature set as previous versions.

**Rationale**: Simplify Backend integration.

**Validation**:
```python
if existing_model_metadata:
    assert new_features == existing_features, "Feature set changed"
```

**Action on Violation**: Warn, document breaking change

---

## 8. Error Handling Rules

### RULE-EH-001: Continue on Model Failure
**Priority**: HIGH  
**Category**: Error Handling

**Rule**: If one model fails to train, continue training other models.

**Rationale**: Partial success better than complete failure.

**Implementation**:
```python
try:
    rf_model = train_random_forest(X_train, y_train)
except Exception as e:
    logger.error(f"RF training failed: {e}")
    rf_model = None
# Continue with other models
```

**Action on Violation**: N/A (rule defines behavior)

---

### RULE-EH-002: Log All Errors
**Priority**: HIGH  
**Category**: Error Handling

**Rule**: All errors MUST be logged with full stack trace.

**Rationale**: Enable debugging and troubleshooting.

**Implementation**:
```python
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
```

**Action on Violation**: N/A (rule defines behavior)

---

### RULE-EH-003: Minimum Models for Ensemble
**Priority**: HIGH  
**Category**: Error Handling

**Rule**: Voting Classifier requires at least 2 successfully trained models.

**Rationale**: Ensemble needs multiple models to be meaningful.

**Validation**:
```python
if len(trained_models) < 2:
    logger.warning("Insufficient models for ensemble, skipping Voting Classifier")
    return None
```

**Action on Violation**: Skip ensemble, log warning

---

### RULE-EH-004: Dataset Generation Retry
**Priority**: MEDIUM  
**Category**: Error Handling

**Rule**: If dataset generation fails, retry up to 3 times with different random seeds.

**Rationale**: Transient failures may resolve with different seed.

**Implementation**:
```python
for attempt in range(3):
    try:
        dataset = generate_dataset(seed=42 + attempt)
        return dataset
    except Exception as e:
        logger.warning(f"Attempt {attempt + 1} failed: {e}")
```

**Action on Violation**: N/A (rule defines behavior)

---

## Rule Priority Levels

### CRITICAL
- **Definition**: Violation prevents system from functioning correctly
- **Action**: Fail operation, log error, do not proceed
- **Examples**: RULE-DG-001, RULE-DG-002, RULE-DQ-001, RULE-DP-001, RULE-MT-001

### HIGH
- **Definition**: Violation significantly impacts quality or correctness
- **Action**: Fail operation or apply correction, log warning
- **Examples**: RULE-DG-004, RULE-DP-002, RULE-ME-001, RULE-MV-001

### MEDIUM
- **Definition**: Violation impacts quality but system can function
- **Action**: Warn, continue with degraded functionality
- **Examples**: RULE-DG-010, RULE-FE-001, RULE-MT-003, RULE-MV-003

### LOW
- **Definition**: Violation is informational, minimal impact
- **Action**: Log info, continue normally
- **Examples**: RULE-DQ-004, RULE-ME-005, RULE-MV-005

---

## Rule Enforcement Matrix

| Rule Category | Total Rules | Critical | High | Medium | Low |
|---------------|-------------|----------|------|--------|-----|
| Data Generation | 11 | 3 | 5 | 3 | 0 |
| Data Quality | 4 | 2 | 0 | 1 | 1 |
| Data Preprocessing | 6 | 0 | 6 | 0 | 0 |
| Feature Engineering | 4 | 0 | 0 | 4 | 0 |
| Model Training | 5 | 1 | 2 | 2 | 0 |
| Model Evaluation | 5 | 0 | 3 | 1 | 1 |
| Model Versioning | 5 | 0 | 2 | 2 | 1 |
| Error Handling | 4 | 0 | 3 | 1 | 0 |
| **TOTAL** | **44** | **6** | **21** | **14** | **3** |

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC Functional Design

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial business rules document |
