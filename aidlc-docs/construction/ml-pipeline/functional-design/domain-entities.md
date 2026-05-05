# Domain Entities: ML Pipeline Unit

## Overview

This document defines all domain entities, their attributes, relationships, and constraints for the ML Pipeline unit.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## Entity Catalog

### 1. StudentProfile

**Purpose**: Represents a student's academic and skill profile for placement prediction

**Attributes**:

| Attribute | Type | Range/Format | Required | Description |
|-----------|------|--------------|----------|-------------|
| student_id | Integer | Auto-increment | Yes | Unique identifier |
| name | String | Max 100 chars | No | Student name (optional) |
| cgpa | Float | [0.0, 10.0] | Yes | Cumulative Grade Point Average |
| aptitude_score | Float | [0, 100] | Yes | Aptitude test score |
| programming_skills | Integer | [1, 10] | Yes | Self-rated programming ability |
| communication_skills | Integer | [1, 10] | Yes | Self-rated communication ability |
| num_projects | Integer | [0, 10] | Yes | Number of completed projects |
| internship_experience | Boolean | True/False | Yes | Has internship experience |
| certifications_count | Integer | [0, 10] | Yes | Number of certifications |
| branch | String | Enum | Yes | Academic branch/department |
| placement_status | Integer | 0 or 1 | Yes | 0=Not Placed, 1=Placed |

**Constraints**:
- `cgpa` must be between 0.0 and 10.0 (inclusive)
- `aptitude_score` must be between 0 and 100 (inclusive)
- `programming_skills` must be between 1 and 10 (inclusive)
- `communication_skills` must be between 1 and 10 (inclusive)
- `num_projects` must be non-negative and ≤ 10
- `certifications_count` must be non-negative and ≤ 10
- `branch` must be one of: CS, IT, ECE, EEE, Mechanical, Civil, Chemical, Other
- `placement_status` must be 0 or 1

**Business Rules**:
- All fields except `name` are required
- No duplicate records (all feature combinations must be unique)
- Record must pass validation before being added to dataset

**Example**:
```json
{
    "student_id": 1,
    "name": "John Doe",
    "cgpa": 8.5,
    "aptitude_score": 85.0,
    "programming_skills": 8,
    "communication_skills": 7,
    "num_projects": 5,
    "internship_experience": true,
    "certifications_count": 3,
    "branch": "CS",
    "placement_status": 1
}
```

---

### 2. TrainingDataset

**Purpose**: Collection of StudentProfile records used for model training

**Attributes**:

| Attribute | Type | Range/Format | Required | Description |
|-----------|------|--------------|----------|-------------|
| dataset_id | String | UUID | Yes | Unique dataset identifier |
| version | String | Sequential | Yes | Dataset version (v1, v2, ...) |
| creation_date | DateTime | ISO 8601 | Yes | When dataset was generated |
| total_records | Integer | ≥ 1000 | Yes | Total number of records |
| placed_count | Integer | ~50% of total | Yes | Number of placed students |
| not_placed_count | Integer | ~50% of total | Yes | Number of not placed students |
| branch_distribution | Dict | JSON | Yes | Count per branch |
| records | List[StudentProfile] | Array | Yes | All student records |

**Constraints**:
- `total_records` must be ≥ 1000
- `placed_count` + `not_placed_count` must equal `total_records`
- Class balance: `placed_count` / `total_records` must be between 0.48 and 0.52 (50% ± 2%)
- All records must be valid StudentProfile entities
- No duplicate records

**Business Rules**:
- Dataset must be balanced (50/50 placed vs not placed)
- Dataset must contain at least 1000 records
- All records must pass validation
- Branch distribution should be realistic (more CS/IT than niche branches)

**Example**:
```json
{
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "v1",
    "creation_date": "2026-05-05T12:00:00Z",
    "total_records": 1000,
    "placed_count": 500,
    "not_placed_count": 500,
    "branch_distribution": {
        "CS": 250,
        "IT": 200,
        "ECE": 150,
        "EEE": 120,
        "Mechanical": 100,
        "Civil": 80,
        "Chemical": 50,
        "Other": 50
    },
    "records": [...]
}
```

---

### 3. ModelMetadata

**Purpose**: Metadata about a trained machine learning model

**Attributes**:

| Attribute | Type | Range/Format | Required | Description |
|-----------|------|--------------|----------|-------------|
| model_id | String | UUID | Yes | Unique model identifier |
| model_name | String | Enum | Yes | Model type (random_forest, gradient_boosting, logistic_regression, voting_classifier) |
| version | String | Sequential | Yes | Model version (v1, v2, ...) |
| training_date | DateTime | ISO 8601 | Yes | When model was trained |
| training_duration_seconds | Float | > 0 | Yes | Training time in seconds |
| dataset_version | String | Sequential | Yes | Version of dataset used |
| dataset_info | Dict | JSON | Yes | Dataset statistics |
| hyperparameters | Dict | JSON | Yes | Model hyperparameters |
| feature_names | List[String] | Array | Yes | Names of all features |
| feature_count | Integer | > 0 | Yes | Total number of features |
| scikit_learn_version | String | Semver | Yes | scikit-learn version used |
| python_version | String | Semver | Yes | Python version used |
| file_path | String | Path | Yes | Path to .pkl file |
| file_size_bytes | Integer | > 0 | Yes | Size of .pkl file |

**Constraints**:
- `model_name` must be one of: random_forest, gradient_boosting, logistic_regression, voting_classifier
- `version` must follow sequential format (v1, v2, v3, ...)
- `training_duration_seconds` must be positive
- `feature_count` must match length of `feature_names`
- `file_path` must point to existing .pkl file

**Business Rules**:
- Each model version must have unique metadata
- Metadata must be saved alongside model .pkl file
- Metadata must include all hyperparameters used
- Metadata must reference dataset version used for training

**Example**:
```json
{
    "model_id": "660e8400-e29b-41d4-a716-446655440001",
    "model_name": "random_forest",
    "version": "v1",
    "training_date": "2026-05-05T12:30:00Z",
    "training_duration_seconds": 45.3,
    "dataset_version": "v1",
    "dataset_info": {
        "total_records": 1000,
        "train_records": 800,
        "test_records": 200,
        "features_count": 18
    },
    "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "random_state": 42
    },
    "feature_names": [
        "cgpa", "aptitude_score", "programming_skills", "communication_skills",
        "num_projects", "internship_experience", "certifications_count",
        "branch_CS", "branch_IT", "branch_ECE", "branch_EEE", "branch_Mechanical",
        "branch_Civil", "branch_Chemical", "branch_Other",
        "Total_Skills_Score", "Experience_Score", "CGPA_Project_Score"
    ],
    "feature_count": 18,
    "scikit_learn_version": "1.3.0",
    "python_version": "3.9.0",
    "file_path": "ml-pipeline/models/trained/random_forest_v1.pkl",
    "file_size_bytes": 5242880
}
```

---

### 4. EvaluationMetrics

**Purpose**: Performance metrics for a trained model

**Attributes**:

| Attribute | Type | Range/Format | Required | Description |
|-----------|------|--------------|----------|-------------|
| evaluation_id | String | UUID | Yes | Unique evaluation identifier |
| model_id | String | UUID | Yes | Reference to ModelMetadata |
| model_name | String | Enum | Yes | Model type |
| model_version | String | Sequential | Yes | Model version |
| evaluation_date | DateTime | ISO 8601 | Yes | When evaluation was performed |
| cv_f1_mean | Float | [0, 1] | Yes | Cross-validation F1 mean |
| cv_f1_std | Float | [0, 1] | Yes | Cross-validation F1 std dev |
| test_accuracy | Float | [0, 1] | Yes | Test set accuracy |
| test_precision | Float | [0, 1] | Yes | Test set precision |
| test_recall | Float | [0, 1] | Yes | Test set recall |
| test_f1_score | Float | [0, 1] | Yes | Test set F1-score |
| test_roc_auc | Float | [0, 1] | Yes | Test set ROC-AUC |
| confusion_matrix | List[List[Int]] | 2x2 matrix | Yes | Confusion matrix |
| performance_threshold_met | Boolean | True/False | Yes | Meets 80% accuracy threshold |
| feature_importance | Dict | JSON | No | Feature importance scores (tree models only) |

**Constraints**:
- All metric values must be between 0 and 1 (inclusive)
- `confusion_matrix` must be 2x2 array
- `model_id` must reference existing ModelMetadata
- `performance_threshold_met` = True if `test_accuracy` ≥ 0.80

**Business Rules**:
- Evaluation must be performed on test set (not training set)
- All 5 metrics (accuracy, precision, recall, F1, ROC-AUC) must be calculated
- Cross-validation scores must be from stratified K-fold
- Feature importance only applicable to tree-based models (RF, GB)

**Example**:
```json
{
    "evaluation_id": "770e8400-e29b-41d4-a716-446655440002",
    "model_id": "660e8400-e29b-41d4-a716-446655440001",
    "model_name": "random_forest",
    "model_version": "v1",
    "evaluation_date": "2026-05-05T12:35:00Z",
    "cv_f1_mean": 0.85,
    "cv_f1_std": 0.03,
    "test_accuracy": 0.87,
    "test_precision": 0.86,
    "test_recall": 0.88,
    "test_f1_score": 0.87,
    "test_roc_auc": 0.92,
    "confusion_matrix": [
        [85, 15],
        [11, 89]
    ],
    "performance_threshold_met": true,
    "feature_importance": {
        "cgpa": 0.18,
        "aptitude_score": 0.15,
        "programming_skills": 0.12,
        "Total_Skills_Score": 0.10,
        ...
    }
}
```

---

### 5. SkillDictionary

**Purpose**: Categorized taxonomy of skills for NLP matching

**Attributes**:

| Attribute | Type | Range/Format | Required | Description |
|-----------|------|--------------|----------|-------------|
| dictionary_id | String | UUID | Yes | Unique dictionary identifier |
| version | String | Sequential | Yes | Dictionary version |
| last_updated | DateTime | ISO 8601 | Yes | Last update timestamp |
| categories | Dict | JSON | Yes | Skills grouped by category |

**Categories Structure**:
```json
{
    "programming_languages": ["Python", "Java", "JavaScript", "C++", "C#", ...],
    "frameworks": ["Flask", "Django", "React", "Angular", "Spring", ...],
    "databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis", ...],
    "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "AWS", ...],
    "soft_skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", ...],
    "domains": ["Machine Learning", "Web Development", "Data Science", "DevOps", ...]
}
```

**Constraints**:
- All skill names must be unique across categories
- Skill names must be title case
- Each category must have at least 5 skills
- Categories must include: programming_languages, frameworks, databases, tools, soft_skills, domains

**Business Rules**:
- Dictionary should be comprehensive but not exhaustive
- Skills should be commonly used in industry
- Dictionary can be updated independently of models
- New skills can be added without retraining models

**Example**:
```json
{
    "dictionary_id": "880e8400-e29b-41d4-a716-446655440003",
    "version": "v1",
    "last_updated": "2026-05-05T10:00:00Z",
    "categories": {
        "programming_languages": [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift"
        ],
        "frameworks": [
            "Flask", "Django", "FastAPI", "React", "Angular", "Vue", "Spring Boot", "Express"
        ],
        "databases": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra", "Oracle", "SQL Server"
        ],
        "tools": [
            "Git", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "Terraform"
        ],
        "soft_skills": [
            "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management"
        ],
        "domains": [
            "Machine Learning", "Web Development", "Data Science", "DevOps", "Cloud Computing"
        ]
    }
}
```

---

## Entity Relationships

### Relationship Diagram

```
TrainingDataset (1) ──contains──> (N) StudentProfile
       │
       │ used_by
       ↓
ModelMetadata (1) ──evaluated_by──> (1) EvaluationMetrics
       │
       │ references
       ↓
SkillDictionary (1) ──used_by──> (N) ModelMetadata
```

### Relationship Descriptions

#### 1. TrainingDataset → StudentProfile
- **Type**: One-to-Many (Composition)
- **Cardinality**: 1 TrainingDataset contains N StudentProfile records (N ≥ 1000)
- **Description**: A training dataset is composed of multiple student profile records
- **Cascade**: Deleting dataset deletes all associated student profiles

#### 2. TrainingDataset → ModelMetadata
- **Type**: One-to-Many (Association)
- **Cardinality**: 1 TrainingDataset used by N ModelMetadata (N ≥ 1)
- **Description**: A dataset can be used to train multiple models
- **Cascade**: Deleting dataset does not delete models (models reference dataset version)

#### 3. ModelMetadata → EvaluationMetrics
- **Type**: One-to-One (Composition)
- **Cardinality**: 1 ModelMetadata has 1 EvaluationMetrics
- **Description**: Each trained model has exactly one evaluation result
- **Cascade**: Deleting model deletes associated evaluation metrics

#### 4. SkillDictionary → ModelMetadata
- **Type**: One-to-Many (Association)
- **Cardinality**: 1 SkillDictionary used by N ModelMetadata
- **Description**: Skill dictionary is referenced by models for feature engineering
- **Cascade**: Deleting dictionary does not delete models (models reference dictionary version)

---

## Entity Validation Rules

### StudentProfile Validation

```python
def validate_student_profile(profile):
    errors = []
    
    # CGPA validation
    if not (0.0 <= profile.cgpa <= 10.0):
        errors.append("CGPA must be between 0.0 and 10.0")
    
    # Aptitude score validation
    if not (0 <= profile.aptitude_score <= 100):
        errors.append("Aptitude score must be between 0 and 100")
    
    # Skills validation
    if not (1 <= profile.programming_skills <= 10):
        errors.append("Programming skills must be between 1 and 10")
    if not (1 <= profile.communication_skills <= 10):
        errors.append("Communication skills must be between 1 and 10")
    
    # Projects validation
    if not (0 <= profile.num_projects <= 10):
        errors.append("Number of projects must be between 0 and 10")
    
    # Certifications validation
    if not (0 <= profile.certifications_count <= 10):
        errors.append("Certifications count must be between 0 and 10")
    
    # Branch validation
    valid_branches = ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']
    if profile.branch not in valid_branches:
        errors.append(f"Branch must be one of {valid_branches}")
    
    # Placement status validation
    if profile.placement_status not in [0, 1]:
        errors.append("Placement status must be 0 or 1")
    
    return len(errors) == 0, errors
```

### TrainingDataset Validation

```python
def validate_training_dataset(dataset):
    errors = []
    
    # Minimum size validation
    if dataset.total_records < 1000:
        errors.append("Dataset must contain at least 1000 records")
    
    # Class balance validation
    placed_ratio = dataset.placed_count / dataset.total_records
    if not (0.48 <= placed_ratio <= 0.52):
        errors.append(f"Dataset must be balanced (50% ± 2%), current: {placed_ratio:.2%}")
    
    # Record count consistency
    if dataset.placed_count + dataset.not_placed_count != dataset.total_records:
        errors.append("Placed + Not Placed counts must equal total records")
    
    # Validate all records
    for i, record in enumerate(dataset.records):
        is_valid, record_errors = validate_student_profile(record)
        if not is_valid:
            errors.append(f"Record {i} validation failed: {record_errors}")
    
    # Check for duplicates
    unique_records = set()
    for record in dataset.records:
        record_tuple = (
            record.cgpa, record.aptitude_score, record.programming_skills,
            record.communication_skills, record.num_projects,
            record.internship_experience, record.certifications_count, record.branch
        )
        if record_tuple in unique_records:
            errors.append(f"Duplicate record found: {record_tuple}")
        unique_records.add(record_tuple)
    
    return len(errors) == 0, errors
```

### ModelMetadata Validation

```python
def validate_model_metadata(metadata):
    errors = []
    
    # Model name validation
    valid_models = ['random_forest', 'gradient_boosting', 'logistic_regression', 'voting_classifier']
    if metadata.model_name not in valid_models:
        errors.append(f"Model name must be one of {valid_models}")
    
    # Version format validation
    if not metadata.version.startswith('v') or not metadata.version[1:].isdigit():
        errors.append("Version must be in format 'v1', 'v2', etc.")
    
    # Training duration validation
    if metadata.training_duration_seconds <= 0:
        errors.append("Training duration must be positive")
    
    # Feature count consistency
    if metadata.feature_count != len(metadata.feature_names):
        errors.append("Feature count must match length of feature names")
    
    # File existence validation
    if not os.path.exists(metadata.file_path):
        errors.append(f"Model file not found: {metadata.file_path}")
    
    return len(errors) == 0, errors
```

### EvaluationMetrics Validation

```python
def validate_evaluation_metrics(metrics):
    errors = []
    
    # Metric range validation
    metric_fields = ['cv_f1_mean', 'cv_f1_std', 'test_accuracy', 'test_precision', 
                     'test_recall', 'test_f1_score', 'test_roc_auc']
    for field in metric_fields:
        value = getattr(metrics, field)
        if not (0 <= value <= 1):
            errors.append(f"{field} must be between 0 and 1, got {value}")
    
    # Confusion matrix validation
    if len(metrics.confusion_matrix) != 2 or len(metrics.confusion_matrix[0]) != 2:
        errors.append("Confusion matrix must be 2x2")
    
    # Performance threshold consistency
    expected_threshold_met = metrics.test_accuracy >= 0.80
    if metrics.performance_threshold_met != expected_threshold_met:
        errors.append("Performance threshold flag inconsistent with accuracy")
    
    return len(errors) == 0, errors
```

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC Functional Design
- **Next**: business-rules.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial domain entities document |
