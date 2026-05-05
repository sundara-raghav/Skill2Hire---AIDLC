# Functional Design Plan: ML Pipeline Unit

## Purpose
Define detailed business logic, domain models, and business rules for the ML Pipeline unit.

---

## Context

### Unit Overview
**Unit ID**: `ml-pipeline`

**Purpose**: Complete machine learning lifecycle from dataset generation through model training, evaluation, and versioning.

**Responsibilities**:
1. Dataset Generation (synthetic data with 1000+ records)
2. Data Preprocessing (cleaning, validation, feature engineering)
3. Model Training (Random Forest, Gradient Boosting, Logistic Regression, Voting Classifier)
4. Model Evaluation (metrics, comparison, reporting)
5. Model Versioning (save models, Git versioning, metadata)

**Components**:
- MLModelManager (produces model artifacts)
- FeatureEngineer (defines feature engineering logic)
- SkillDictionary (skill taxonomy data)
- Data generation scripts
- Training scripts
- Evaluation scripts

---

## Functional Design Plan

### Phase 1: Understand Business Domain
- [ ] **1.1 Review Requirements**
  - [ ] Read functional requirements (FR-06, FR-07, FR-08)
  - [ ] Read data requirements (dataset specifications)
  - [ ] Read ML requirements (model types, evaluation metrics)
  - [ ] Understand performance constraints (<5 second prediction)

- [ ] **1.2 Identify Domain Entities**
  - [ ] Define Student Profile entity
  - [ ] Define Job Description entity
  - [ ] Define Prediction Result entity
  - [ ] Define Model Metadata entity
  - [ ] Define Training Dataset entity

- [ ] **1.3 Map Business Workflows**
  - [ ] Dataset generation workflow
  - [ ] Data preprocessing workflow
  - [ ] Model training workflow
  - [ ] Model evaluation workflow
  - [ ] Model versioning workflow

### Phase 2: Design Business Logic Models
- [ ] **2.1 Dataset Generation Logic**
  - [ ] Define synthetic data generation algorithm
  - [ ] Define data distribution rules (balanced 50/50)
  - [ ] Define field value ranges and constraints
  - [ ] Define duplicate detection logic
  - [ ] Define data quality validation rules

- [ ] **2.2 Data Preprocessing Logic**
  - [ ] Define missing value handling strategy
  - [ ] Define feature scaling approach
  - [ ] Define categorical encoding strategy
  - [ ] Define train-test split logic (80-20)
  - [ ] Define data validation rules

- [ ] **2.3 Feature Engineering Logic**
  - [ ] Define feature transformation rules
  - [ ] Define derived feature calculations
  - [ ] Define feature selection criteria
  - [ ] Define feature normalization approach

- [ ] **2.4 Model Training Logic**
  - [ ] Define hyperparameter tuning strategy
  - [ ] Define cross-validation approach
  - [ ] Define model selection criteria
  - [ ] Define ensemble voting strategy
  - [ ] Define training convergence criteria

- [ ] **2.5 Model Evaluation Logic**
  - [ ] Define evaluation metrics calculation
  - [ ] Define model comparison criteria
  - [ ] Define performance threshold rules
  - [ ] Define evaluation report generation

- [ ] **2.6 Model Versioning Logic**
  - [ ] Define model serialization format
  - [ ] Define version numbering scheme
  - [ ] Define metadata structure
  - [ ] Define model storage strategy

### Phase 3: Define Domain Entities
- [ ] **3.1 Create Domain Entity Definitions**
  - [ ] StudentProfile entity (attributes, constraints)
  - [ ] JobDescription entity (attributes, constraints)
  - [ ] TrainingDataset entity (attributes, constraints)
  - [ ] ModelMetadata entity (attributes, constraints)
  - [ ] EvaluationMetrics entity (attributes, constraints)

- [ ] **3.2 Define Entity Relationships**
  - [ ] StudentProfile → TrainingDataset relationship
  - [ ] TrainingDataset → ModelMetadata relationship
  - [ ] ModelMetadata → EvaluationMetrics relationship

- [ ] **3.3 Define Entity Validation Rules**
  - [ ] StudentProfile validation constraints
  - [ ] JobDescription validation constraints
  - [ ] TrainingDataset validation constraints

### Phase 4: Define Business Rules
- [ ] **4.1 Data Generation Rules**
  - [ ] CGPA range rules (0.0-10.0)
  - [ ] Skills rating rules (1-10)
  - [ ] Placement probability calculation rules
  - [ ] Branch distribution rules
  - [ ] Balanced dataset rules (50% placed, 50% not placed)

- [ ] **4.2 Data Quality Rules**
  - [ ] No duplicate records rule
  - [ ] No missing values rule
  - [ ] Valid data type rule
  - [ ] Range validation rules

- [ ] **4.3 Model Training Rules**
  - [ ] Minimum dataset size rule (1000+ records)
  - [ ] Train-test split ratio rule (80-20)
  - [ ] Cross-validation fold rule
  - [ ] Hyperparameter search space rules

- [ ] **4.4 Model Evaluation Rules**
  - [ ] Minimum accuracy threshold rule
  - [ ] Model comparison criteria rules
  - [ ] Performance degradation detection rules

- [ ] **4.5 Model Versioning Rules**
  - [ ] Version increment rules
  - [ ] Model replacement criteria
  - [ ] Backward compatibility rules

### Phase 5: Generate Artifacts
- [x] **5.1 Generate business-logic-model.md**
  - [x] Document dataset generation logic
  - [x] Document preprocessing logic
  - [x] Document feature engineering logic
  - [x] Document training logic
  - [x] Document evaluation logic
  - [x] Document versioning logic

- [x] **5.2 Generate domain-entities.md**
  - [x] Document all domain entities
  - [x] Document entity attributes and types
  - [x] Document entity relationships
  - [x] Document entity constraints

- [x] **5.3 Generate business-rules.md**
  - [x] Document all business rules
  - [x] Document rule conditions and actions
  - [x] Document rule priorities
  - [x] Document validation rules

### Phase 6: Validation
- [x] **6.1 Validate Completeness**
  - [x] All workflows covered
  - [x] All entities defined
  - [x] All business rules documented

- [x] **6.2 Validate Consistency**
  - [x] No conflicting rules
  - [x] Entity relationships are valid
  - [x] Logic flows are coherent

---

## Clarifying Questions

Please answer the following questions to guide the functional design for the ML Pipeline unit.

### Question 1: Synthetic Data Generation Strategy
How should the synthetic dataset be generated to ensure realistic placement predictions?

A) **Random Generation** - Completely random values within valid ranges
B) **Rule-Based Generation** - Use business rules to correlate features (e.g., high CGPA → higher placement probability)
C) **Distribution-Based** - Sample from realistic distributions (normal for CGPA, uniform for skills)
D) **Hybrid** - Combine rule-based correlations with realistic distributions
E) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 2: Feature Correlation Rules
Should there be correlations between input features in the synthetic dataset?

A) **Strong Correlations** - High CGPA strongly correlates with high skills, projects, internships
B) **Moderate Correlations** - Some correlation but with noise and exceptions
C) **Weak Correlations** - Minimal correlation, mostly independent features
D) **No Correlations** - All features are independent
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 3: Placement Probability Calculation
How should placement status be determined in the synthetic dataset?

A) **Threshold-Based** - Calculate score from features, apply threshold (e.g., score > 0.5 → placed)
B) **Weighted Formula** - Use weighted sum of features with domain-specific weights
C) **Probabilistic** - Use probability distribution based on feature values
D) **ML-Based** - Use a simple model to generate realistic placement patterns
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 4: Branch/Department Distribution
How should students be distributed across branches in the synthetic dataset?

A) **Equal Distribution** - Same number of students per branch
B) **Realistic Distribution** - More students in popular branches (CS, IT) vs niche branches
C) **Configurable** - Allow configuration of branch distribution percentages
D) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 5: Missing Value Handling
How should missing values be handled during data preprocessing?

A) **Drop Records** - Remove any records with missing values
B) **Imputation - Mean/Median** - Fill missing numeric values with mean/median
C) **Imputation - Mode** - Fill missing categorical values with mode
D) **No Missing Values** - Ensure synthetic dataset has no missing values
E) **Hybrid** - Different strategies for different field types
F) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 6: Feature Scaling Method
What feature scaling method should be used for numeric features?

A) **StandardScaler** - Standardize features (mean=0, std=1)
B) **MinMaxScaler** - Scale features to [0, 1] range
C) **RobustScaler** - Scale using median and IQR (robust to outliers)
D) **No Scaling** - Use raw feature values
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 7: Categorical Encoding Strategy
How should categorical features (Branch) be encoded?

A) **One-Hot Encoding** - Create binary columns for each branch
B) **Label Encoding** - Assign numeric labels to branches
C) **Target Encoding** - Encode based on placement rate per branch
D) **Ordinal Encoding** - Assign ordered numeric values
E) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 8: Hyperparameter Tuning Approach
What approach should be used for hyperparameter tuning?

A) **Grid Search** - Exhaustive search over parameter grid
B) **Random Search** - Random sampling of parameter space
C) **Bayesian Optimization** - Smart search using Bayesian methods
D) **Manual Tuning** - Use predefined "good" hyperparameters
E) **No Tuning** - Use scikit-learn defaults
F) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 9: Cross-Validation Strategy
What cross-validation strategy should be used during training?

A) **K-Fold (k=5)** - 5-fold cross-validation
B) **K-Fold (k=10)** - 10-fold cross-validation
C) **Stratified K-Fold** - K-fold with stratification to preserve class balance
D) **Leave-One-Out** - Each sample used as validation once
E) **No Cross-Validation** - Simple train-test split only
F) Other (please describe after [Answer]: tag below)

[Answer]: c

---

### Question 10: Ensemble Voting Strategy
How should the Voting Classifier combine predictions from individual models?

A) **Hard Voting** - Majority vote (classification labels)
B) **Soft Voting** - Average predicted probabilities
C) **Weighted Voting** - Weighted average based on model performance
D) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 11: Model Performance Threshold
What minimum performance threshold should models meet to be considered acceptable?

A) **Accuracy ≥ 80%** - Minimum 80% accuracy on test set
B) **Accuracy ≥ 85%** - Minimum 85% accuracy on test set
C) **Accuracy ≥ 90%** - Minimum 90% accuracy on test set
D) **F1-Score ≥ 0.80** - Minimum F1-score of 0.80
E) **No Threshold** - Accept any trained model
F) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 12: Model Versioning Scheme
How should model versions be numbered and tracked?

A) **Semantic Versioning** - MAJOR.MINOR.PATCH (e.g., 1.0.0, 1.1.0)
B) **Date-Based** - YYYYMMDD format (e.g., 20260505)
C) **Sequential** - Simple incrementing number (v1, v2, v3)
D) **Git Commit Hash** - Use Git commit SHA as version
E) Other (please describe after [Answer]: tag below)

[Answer]: c

---

### Question 13: Model Replacement Criteria
When should a new model replace an existing model in production?

A) **Always Replace** - Every new trained model replaces the old one
B) **Performance Improvement** - Replace only if new model has better accuracy
C) **Significant Improvement** - Replace only if improvement exceeds threshold (e.g., +2% accuracy)
D) **Manual Approval** - Require manual review and approval before replacement
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 14: Feature Engineering - Derived Features
Should the system create derived features from raw inputs?

A) **Yes - Extensive** - Create many derived features (e.g., CGPA*Projects, Skills_Total, Experience_Score)
B) **Yes - Minimal** - Create a few key derived features
C) **No** - Use only raw input features
D) Other (please describe after [Answer]: tag below)

If Yes, which derived features should be created?

[Answer]: b

---

### Question 15: Skill Dictionary Structure
How should the skill dictionary be structured and maintained?

A) **Flat List** - Simple list of skills (JSON array)
B) **Categorized** - Skills grouped by category (programming, tools, soft skills)
C) **Hierarchical** - Skills with parent-child relationships (e.g., Python → Django)
D) **Weighted** - Skills with importance weights
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 16: Data Quality Validation Rules
What data quality checks should be performed on the generated dataset?

A) **Basic Checks** - No nulls, correct data types, valid ranges
B) **Statistical Checks** - Distribution checks, outlier detection, correlation analysis
C) **Business Rule Checks** - Verify business logic (e.g., balanced classes, realistic patterns)
D) **Comprehensive** - All of the above
E) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 17: Model Evaluation Metrics Priority
Which evaluation metric is most important for model selection?

A) **Accuracy** - Overall correctness
B) **Precision** - Minimize false positives (predicting placed when not)
C) **Recall** - Minimize false negatives (predicting not placed when placed)
D) **F1-Score** - Balance between precision and recall
E) **ROC-AUC** - Overall discriminative ability
F) **Balanced** - Consider all metrics equally
G) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 18: Training Dataset Persistence
Should the training dataset be regenerated each time or persisted?

A) **Regenerate Always** - Generate new dataset for each training run
B) **Persist and Reuse** - Generate once, save to file, reuse for all training
C) **Versioned Datasets** - Generate and version datasets, allow selection
D) **Configurable** - Support both regeneration and reuse
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 19: Model Metadata Content
What metadata should be stored with each trained model?

A) **Basic** - Version, training date, accuracy
B) **Standard** - Version, date, all evaluation metrics, hyperparameters
C) **Comprehensive** - All of standard + dataset info, feature names, training duration, scikit-learn version
D) Other (please describe after [Answer]: tag below)

[Answer]: b

---

### Question 20: Error Handling During Training
How should errors during model training be handled?

A) **Fail Fast** - Stop immediately on any error
B) **Continue on Error** - Log error, skip failed model, continue with others
C) **Retry Logic** - Retry failed training with adjusted parameters
D) **Graceful Degradation** - Use fallback models if training fails
E) Other (please describe after [Answer]: tag below)

[Answer]: b

---

## Instructions

1. **Answer all questions** by filling in the letter choice (A, B, C, D, E, F, G) after each `[Answer]:` tag
2. **For "Other" choices**, provide a detailed description of your preferred approach
3. **For questions requesting additional details**, provide the information after the [Answer]: tag
4. **Consider the requirements** and unit responsibilities when making decisions
5. **Think about ML best practices**, data quality, and model performance
6. **Let me know when done** so I can analyze your answers and proceed with artifact generation

---

**Status**: Awaiting user input
