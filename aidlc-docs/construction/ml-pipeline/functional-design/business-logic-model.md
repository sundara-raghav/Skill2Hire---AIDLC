# Business Logic Model: ML Pipeline Unit

## Overview

This document defines the detailed business logic and algorithms for the ML Pipeline unit, covering dataset generation, preprocessing, feature engineering, model training, evaluation, and versioning.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## 1. Dataset Generation Logic

### 1.1 Synthetic Data Generation Algorithm

**Purpose**: Generate realistic synthetic dataset with 1000+ student records for training placement prediction models.

**Algorithm**: Hybrid approach combining rule-based correlations with realistic distributions

**Process Flow**:
```
1. Initialize empty dataset
2. Define target size (1000+ records)
3. Define branch distribution (realistic)
4. For each record:
   a. Generate base features from distributions
   b. Apply moderate correlations
   c. Calculate placement probability using weighted formula
   d. Determine placement status
   e. Validate record uniqueness
   f. Add to dataset
5. Validate dataset quality
6. Save dataset to file
```

### 1.2 Feature Generation Rules

#### 1.2.1 CGPA Generation
- **Distribution**: Normal distribution
- **Mean**: 7.0
- **Standard Deviation**: 1.2
- **Range**: [0.0, 10.0]
- **Constraint**: Clip values to valid range

```python
cgpa = np.clip(np.random.normal(7.0, 1.2), 0.0, 10.0)
```

#### 1.2.2 Aptitude Score Generation
- **Distribution**: Normal distribution
- **Mean**: 70
- **Standard Deviation**: 15
- **Range**: [0, 100]
- **Constraint**: Clip values to valid range

```python
aptitude_score = np.clip(np.random.normal(70, 15), 0, 100)
```

#### 1.2.3 Programming Skills Generation
- **Distribution**: Discrete uniform with moderate correlation to CGPA
- **Range**: [1, 10]
- **Correlation**: Moderate positive correlation with CGPA
- **Logic**:
  - Base value: Random integer [1, 10]
  - Adjustment: +1 if CGPA > 8.0, -1 if CGPA < 5.0
  - Clip to valid range

```python
base_prog_skills = np.random.randint(1, 11)
if cgpa > 8.0:
    prog_skills = min(base_prog_skills + 1, 10)
elif cgpa < 5.0:
    prog_skills = max(base_prog_skills - 1, 1)
else:
    prog_skills = base_prog_skills
```

#### 1.2.4 Communication Skills Generation
- **Distribution**: Discrete uniform with weak correlation to CGPA
- **Range**: [1, 10]
- **Correlation**: Weak positive correlation with CGPA
- **Logic**:
  - Base value: Random integer [1, 10]
  - Adjustment: +1 if CGPA > 8.5 (20% probability)
  - Clip to valid range

```python
base_comm_skills = np.random.randint(1, 11)
if cgpa > 8.5 and np.random.random() < 0.2:
    comm_skills = min(base_comm_skills + 1, 10)
else:
    comm_skills = base_comm_skills
```

#### 1.2.5 Number of Projects Generation
- **Distribution**: Poisson distribution with moderate correlation to programming skills
- **Lambda**: 2.5
- **Range**: [0, 10]
- **Correlation**: Moderate positive correlation with programming skills
- **Logic**:
  - Base value: Poisson(lambda=2.5)
  - Adjustment: +1 if prog_skills >= 8
  - Clip to valid range

```python
base_projects = np.random.poisson(2.5)
if prog_skills >= 8:
    num_projects = min(base_projects + 1, 10)
else:
    num_projects = min(base_projects, 10)
```

#### 1.2.6 Internship Experience Generation
- **Distribution**: Bernoulli with moderate correlation to CGPA and projects
- **Probability**: Base 0.4, adjusted by CGPA and projects
- **Logic**:
  - Base probability: 0.4
  - +0.2 if CGPA > 7.5
  - +0.1 if num_projects >= 3
  - Clip probability to [0, 1]
  - Sample from Bernoulli

```python
prob = 0.4
if cgpa > 7.5:
    prob += 0.2
if num_projects >= 3:
    prob += 0.1
prob = min(prob, 1.0)
internship_experience = np.random.random() < prob
```

#### 1.2.7 Certifications Count Generation
- **Distribution**: Poisson distribution with moderate correlation to programming skills
- **Lambda**: 1.5
- **Range**: [0, 10]
- **Correlation**: Moderate positive correlation with programming skills
- **Logic**:
  - Base value: Poisson(lambda=1.5)
  - Adjustment: +1 if prog_skills >= 7
  - Clip to valid range

```python
base_certs = np.random.poisson(1.5)
if prog_skills >= 7:
    certifications_count = min(base_certs + 1, 10)
else:
    certifications_count = min(base_certs, 10)
```

#### 1.2.8 Branch Generation
- **Distribution**: Categorical with realistic distribution
- **Branches**: CS, IT, ECE, EEE, Mechanical, Civil, Chemical, Other
- **Distribution**:
  - CS: 25%
  - IT: 20%
  - ECE: 15%
  - EEE: 12%
  - Mechanical: 10%
  - Civil: 8%
  - Chemical: 5%
  - Other: 5%

```python
branches = ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']
probabilities = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.05]
branch = np.random.choice(branches, p=probabilities)
```

### 1.3 Placement Status Calculation

**Method**: Weighted formula combining all features

**Formula**:
```
placement_score = (
    CGPA * 0.25 +
    (Aptitude_Score / 100) * 0.20 +
    (Programming_Skills / 10) * 0.20 +
    (Communication_Skills / 10) * 0.10 +
    (Num_Projects / 10) * 0.10 +
    (Internship_Experience ? 1 : 0) * 0.10 +
    (Certifications_Count / 10) * 0.05
)

# Normalize to [0, 1]
placement_probability = placement_score / 10.0

# Determine placement status
if placement_probability >= 0.5:
    placement_status = 1  # Placed
else:
    placement_status = 0  # Not Placed
```

**Balancing Strategy**:
- After generating all records, check class balance
- If imbalance > 5%, adjust threshold to achieve 50/50 split
- Recalculate placement status with adjusted threshold

### 1.4 Duplicate Detection Logic

**Method**: Check for duplicate records based on all features

**Logic**:
```python
def is_duplicate(new_record, existing_records):
    for existing in existing_records:
        if all([
            new_record['cgpa'] == existing['cgpa'],
            new_record['aptitude_score'] == existing['aptitude_score'],
            new_record['programming_skills'] == existing['programming_skills'],
            new_record['communication_skills'] == existing['communication_skills'],
            new_record['num_projects'] == existing['num_projects'],
            new_record['internship_experience'] == existing['internship_experience'],
            new_record['certifications_count'] == existing['certifications_count'],
            new_record['branch'] == existing['branch']
        ]):
            return True
    return False
```

**Action**: If duplicate detected, regenerate record with different random seed

### 1.5 Data Quality Validation Rules

**Validation Checks**:
1. **No Null Values**: All fields must have values
2. **Correct Data Types**: Numeric fields are numeric, categorical are strings
3. **Valid Ranges**: All values within specified ranges
4. **Balanced Classes**: 50% placed, 50% not placed (±2% tolerance)
5. **No Duplicates**: All records are unique
6. **Realistic Distributions**: Statistical checks on distributions
7. **Correlation Checks**: Verify moderate correlations exist

**Validation Process**:
```
1. Check for null values → Fail if any found
2. Check data types → Fail if incorrect
3. Check value ranges → Fail if out of range
4. Check class balance → Warn if imbalanced, adjust if needed
5. Check for duplicates → Fail if duplicates found
6. Check distributions → Warn if unrealistic
7. Check correlations → Warn if correlations too weak/strong
```

---

## 2. Data Preprocessing Logic

### 2.1 Missing Value Handling

**Strategy**: No missing values (synthetic dataset guaranteed complete)

**Validation**:
```python
assert dataset.isnull().sum().sum() == 0, "Dataset contains missing values"
```

**Rationale**: Since we control synthetic data generation, we ensure no missing values are created.

### 2.2 Train-Test Split Logic

**Method**: Stratified split to preserve class balance

**Split Ratio**: 80% train, 20% test

**Implementation**:
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y  # Preserve class balance
)
```

**Validation**:
- Verify train set has ~50% placed, ~50% not placed
- Verify test set has ~50% placed, ~50% not placed

### 2.3 Feature Scaling Logic

**Method**: MinMaxScaler (scale to [0, 1] range)

**Features to Scale**:
- CGPA (already [0, 10])
- Aptitude Score ([0, 100])
- Programming Skills ([1, 10])
- Communication Skills ([1, 10])
- Number of Projects ([0, 10])
- Certifications Count ([0, 10])

**Features NOT Scaled**:
- Internship Experience (already binary 0/1)
- Branch (categorical, will be one-hot encoded)

**Implementation**:
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
numeric_features = ['cgpa', 'aptitude_score', 'programming_skills', 
                   'communication_skills', 'num_projects', 'certifications_count']

X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
X_test[numeric_features] = scaler.transform(X_test[numeric_features])
```

**Persistence**: Save scaler object for use in Backend inference

### 2.4 Categorical Encoding Logic

**Method**: One-Hot Encoding for Branch feature

**Implementation**:
```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
branch_encoded_train = encoder.fit_transform(X_train[['branch']])
branch_encoded_test = encoder.transform(X_test[['branch']])

# Create column names
branch_columns = [f'branch_{cat}' for cat in encoder.categories_[0]]

# Add encoded columns to dataset
X_train = pd.concat([
    X_train.drop('branch', axis=1),
    pd.DataFrame(branch_encoded_train, columns=branch_columns, index=X_train.index)
], axis=1)

X_test = pd.concat([
    X_test.drop('branch', axis=1),
    pd.DataFrame(branch_encoded_test, columns=branch_columns, index=X_test.index)
], axis=1)
```

**Persistence**: Save encoder object for use in Backend inference

---

## 3. Feature Engineering Logic

### 3.1 Derived Features

**Strategy**: Create 3 minimal derived features to enhance model performance

#### 3.1.1 Total_Skills_Score
**Purpose**: Aggregate measure of technical and soft skills

**Calculation**:
```python
Total_Skills_Score = Programming_Skills + Communication_Skills
# Range: [2, 20]
```

**Rationale**: Combined skills may be more predictive than individual skills

#### 3.1.2 Experience_Score
**Purpose**: Weighted combination of practical experience indicators

**Calculation**:
```python
Experience_Score = (Num_Projects * 0.4) + (Internship_Experience * 0.6)
# Range: [0, 4.6] (0 projects + no internship = 0, 10 projects + internship = 4.6)
```

**Rationale**: Internship experience weighted higher than project count

#### 3.1.3 CGPA_Project_Score
**Purpose**: Interaction term between academic performance and practical work

**Calculation**:
```python
CGPA_Project_Score = CGPA * Num_Projects
# Range: [0, 100] (0 CGPA * 0 projects = 0, 10 CGPA * 10 projects = 100)
```

**Rationale**: High CGPA combined with many projects is strong placement indicator

### 3.2 Feature Engineering Process

**Workflow**:
```
1. Apply feature scaling to raw features
2. Apply categorical encoding to Branch
3. Calculate derived features from scaled values
4. Concatenate all features (raw scaled + encoded + derived)
5. Final feature vector ready for model training
```

**Final Feature Set** (after engineering):
- cgpa (scaled)
- aptitude_score (scaled)
- programming_skills (scaled)
- communication_skills (scaled)
- num_projects (scaled)
- internship_experience (binary)
- certifications_count (scaled)
- branch_CS, branch_IT, branch_ECE, ... (one-hot encoded)
- Total_Skills_Score (derived)
- Experience_Score (derived)
- CGPA_Project_Score (derived)

**Total Features**: ~18 features (7 numeric + 8 branch + 3 derived)

---

## 4. Model Training Logic

### 4.1 Hyperparameter Configuration

**Strategy**: Manual tuning with predefined "good" hyperparameters

#### 4.1.1 Random Forest Hyperparameters
```python
rf_params = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': 42,
    'n_jobs': -1
}
```

#### 4.1.2 Gradient Boosting Hyperparameters
```python
gb_params = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 5,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'subsample': 0.8,
    'random_state': 42
}
```

#### 4.1.3 Logistic Regression Hyperparameters
```python
lr_params = {
    'C': 1.0,
    'penalty': 'l2',
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42
}
```

### 4.2 Cross-Validation Strategy

**Method**: Stratified K-Fold Cross-Validation

**Configuration**:
- **K**: 5 folds
- **Stratification**: Preserve class balance in each fold
- **Shuffle**: True
- **Random State**: 42

**Implementation**:
```python
from sklearn.model_selection import StratifiedKFold, cross_val_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# For each model
cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1')
mean_cv_score = cv_scores.mean()
std_cv_score = cv_scores.std()
```

**Purpose**: Validate model performance and detect overfitting

### 4.3 Model Training Process

**Workflow**:
```
1. Initialize model with hyperparameters
2. Perform cross-validation on training set
3. Log cross-validation scores
4. Train model on full training set
5. Evaluate on test set
6. Check performance threshold (≥80% accuracy)
7. If threshold met, save model
8. If threshold not met, log warning and save anyway
```

**Training Code**:
```python
# Train Random Forest
rf_model = RandomForestClassifier(**rf_params)
rf_cv_scores = cross_val_score(rf_model, X_train, y_train, cv=cv, scoring='f1')
rf_model.fit(X_train, y_train)

# Train Gradient Boosting
gb_model = GradientBoostingClassifier(**gb_params)
gb_cv_scores = cross_val_score(gb_model, X_train, y_train, cv=cv, scoring='f1')
gb_model.fit(X_train, y_train)

# Train Logistic Regression
lr_model = LogisticRegression(**lr_params)
lr_cv_scores = cross_val_score(lr_model, X_train, y_train, cv=cv, scoring='f1')
lr_model.fit(X_train, y_train)
```

### 4.4 Ensemble Voting Classifier

**Method**: Soft Voting (average predicted probabilities)

**Configuration**:
```python
from sklearn.ensemble import VotingClassifier

voting_clf = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('gb', gb_model),
        ('lr', lr_model)
    ],
    voting='soft',  # Average probabilities
    n_jobs=-1
)

voting_clf.fit(X_train, y_train)
```

**Rationale**: Soft voting leverages probability estimates for better ensemble performance

---

## 5. Model Evaluation Logic

### 5.1 Evaluation Metrics

**Primary Metric**: F1-Score (balance between precision and recall)

**All Metrics Calculated**:
1. **Accuracy**: Overall correctness
2. **Precision**: Minimize false positives
3. **Recall**: Minimize false negatives
4. **F1-Score**: Harmonic mean of precision and recall
5. **ROC-AUC**: Discriminative ability

**Implementation**:
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'f1_score': f1_score(y_test, y_pred),
    'roc_auc': roc_auc_score(y_test, y_pred_proba)
}
```

### 5.2 Model Comparison Logic

**Comparison Criteria**:
1. **Primary**: F1-Score (highest wins)
2. **Secondary**: Accuracy (if F1 tied)
3. **Tertiary**: ROC-AUC (if accuracy tied)

**Comparison Process**:
```python
def compare_models(models_metrics):
    # Sort by F1-Score (descending), then Accuracy, then ROC-AUC
    sorted_models = sorted(
        models_metrics.items(),
        key=lambda x: (x[1]['f1_score'], x[1]['accuracy'], x[1]['roc_auc']),
        reverse=True
    )
    return sorted_models[0][0]  # Return best model name
```

### 5.3 Performance Threshold Validation

**Threshold**: Minimum 80% accuracy on test set

**Validation Logic**:
```python
def validate_performance(metrics):
    if metrics['accuracy'] >= 0.80:
        return True, "Model meets performance threshold"
    else:
        return False, f"Model accuracy {metrics['accuracy']:.2%} below 80% threshold"
```

**Action**:
- If threshold met: Save model, log success
- If threshold not met: Log warning, save model anyway (for debugging)

### 5.4 Evaluation Report Generation

**Report Contents**:
1. Model name and version
2. Training date and duration
3. Cross-validation scores (mean ± std)
4. Test set metrics (all 5 metrics)
5. Confusion matrix
6. Feature importance (for tree-based models)
7. Performance threshold validation result

**Report Format**: Markdown file + JSON metrics file

---

## 6. Model Versioning Logic

### 6.1 Version Numbering Scheme

**Method**: Sequential versioning (v1, v2, v3, ...)

**Logic**:
```python
def get_next_version(model_dir):
    existing_versions = [
        int(f.replace('v', '').replace('.pkl', ''))
        for f in os.listdir(model_dir)
        if f.startswith('v') and f.endswith('.pkl')
    ]
    if not existing_versions:
        return 'v1'
    return f'v{max(existing_versions) + 1}'
```

### 6.2 Model Serialization

**Format**: Pickle (.pkl) files

**Serialization Process**:
```python
import pickle

def save_model(model, model_name, version, model_dir):
    filename = f'{model_name}_{version}.pkl'
    filepath = os.path.join(model_dir, filename)
    
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    return filepath
```

**Models Saved**:
- `random_forest_v1.pkl`
- `gradient_boosting_v1.pkl`
- `logistic_regression_v1.pkl`
- `voting_classifier_v1.pkl`

**Additional Artifacts Saved**:
- `scaler_v1.pkl` (MinMaxScaler)
- `encoder_v1.pkl` (OneHotEncoder)

### 6.3 Model Metadata

**Content**: Standard metadata (version, date, metrics, hyperparameters)

**Metadata Structure**:
```json
{
    "model_name": "random_forest",
    "version": "v1",
    "training_date": "2026-05-05T12:00:00Z",
    "training_duration_seconds": 45.3,
    "dataset_info": {
        "total_records": 1000,
        "train_records": 800,
        "test_records": 200,
        "features_count": 18
    },
    "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 10,
        ...
    },
    "metrics": {
        "cv_f1_mean": 0.85,
        "cv_f1_std": 0.03,
        "test_accuracy": 0.87,
        "test_precision": 0.86,
        "test_recall": 0.88,
        "test_f1_score": 0.87,
        "test_roc_auc": 0.92
    },
    "performance_threshold_met": true,
    "scikit_learn_version": "1.3.0",
    "python_version": "3.9.0"
}
```

**Storage**: JSON file alongside model pickle file

### 6.4 Model Replacement Logic

**Criteria**: Replace if new model has better accuracy

**Replacement Process**:
```python
def should_replace_model(new_metrics, existing_metrics):
    if existing_metrics is None:
        return True  # No existing model, always replace
    
    if new_metrics['accuracy'] > existing_metrics['accuracy']:
        return True
    else:
        return False
```

**Action**:
- If replacement approved: Update symlink to point to new version
- If not approved: Keep existing model, archive new model

**Symlink Strategy**:
```bash
# Create symlinks for "latest" models
ln -sf random_forest_v2.pkl random_forest.pkl
ln -sf gradient_boosting_v2.pkl gradient_boosting.pkl
ln -sf logistic_regression_v2.pkl logistic_regression.pkl
ln -sf voting_classifier_v2.pkl voting_classifier.pkl
```

---

## 7. Error Handling Logic

### 7.1 Training Error Handling

**Strategy**: Continue on error (log error, skip failed model, continue with others)

**Error Handling Process**:
```python
def train_all_models(X_train, y_train, X_test, y_test):
    models = {}
    errors = {}
    
    # Train Random Forest
    try:
        rf_model = train_random_forest(X_train, y_train)
        models['random_forest'] = rf_model
    except Exception as e:
        logger.error(f"Random Forest training failed: {e}")
        errors['random_forest'] = str(e)
    
    # Train Gradient Boosting
    try:
        gb_model = train_gradient_boosting(X_train, y_train)
        models['gradient_boosting'] = gb_model
    except Exception as e:
        logger.error(f"Gradient Boosting training failed: {e}")
        errors['gradient_boosting'] = str(e)
    
    # Train Logistic Regression
    try:
        lr_model = train_logistic_regression(X_train, y_train)
        models['logistic_regression'] = lr_model
    except Exception as e:
        logger.error(f"Logistic Regression training failed: {e}")
        errors['logistic_regression'] = str(e)
    
    # Train Voting Classifier (only if at least 2 models succeeded)
    if len(models) >= 2:
        try:
            voting_clf = train_voting_classifier(models, X_train, y_train)
            models['voting_classifier'] = voting_clf
        except Exception as e:
            logger.error(f"Voting Classifier training failed: {e}")
            errors['voting_classifier'] = str(e)
    else:
        logger.warning("Insufficient models for ensemble, skipping Voting Classifier")
    
    return models, errors
```

**Rationale**: Partial success is better than complete failure. If some models train successfully, they can still be used.

### 7.2 Data Generation Error Handling

**Strategy**: Retry with different random seed if generation fails

**Error Handling**:
```python
def generate_dataset_with_retry(target_size, max_retries=3):
    for attempt in range(max_retries):
        try:
            dataset = generate_synthetic_dataset(target_size, seed=42 + attempt)
            validate_dataset(dataset)
            return dataset
        except Exception as e:
            logger.warning(f"Dataset generation attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise Exception(f"Dataset generation failed after {max_retries} attempts")
    return None
```

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC Functional Design
- **Next**: domain-entities.md, business-rules.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial business logic model |
