# Tech Stack Decisions: ML Pipeline Unit

## Overview

This document defines all technology stack decisions for the ML Pipeline unit, including ML libraries, data processing libraries, development tools, and version pinning strategy.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## 1. Core ML Libraries

### 1.1 scikit-learn

**Decision**: Use scikit-learn as the primary machine learning library

**Version**: `scikit-learn~=1.3.0` (minor version pinning)

**Rationale**:
- Industry-standard ML library for classical algorithms
- Excellent support for Random Forest, Gradient Boosting, Logistic Regression
- Built-in cross-validation and evaluation metrics
- Well-documented and stable API
- No GPU required (CPU-optimized)
- Lightweight and fast for small datasets

**Features Used**:
- `RandomForestClassifier` - Ensemble tree-based model
- `GradientBoostingClassifier` - Boosting ensemble model
- `LogisticRegression` - Linear classification model
- `VotingClassifier` - Soft voting ensemble
- `train_test_split` - Stratified train-test splitting
- `StratifiedKFold` - Stratified cross-validation
- `cross_val_score` - Cross-validation scoring
- `MinMaxScaler` - Feature scaling
- `OneHotEncoder` - Categorical encoding
- Metrics: `accuracy_score`, `precision_score`, `recall_score`, `f1_score`, `roc_auc_score`

**Alternatives Considered**:
- **XGBoost**: More powerful but overkill for dataset size, adds complexity
- **LightGBM**: Similar to XGBoost, unnecessary for project scope
- **TensorFlow/PyTorch**: Deep learning frameworks, not needed for tabular data
- **CatBoost**: Good for categorical features but scikit-learn sufficient

**Impact**: Proven, stable, sufficient for project requirements

---

### 1.2 NumPy

**Decision**: Use NumPy for numerical operations and array manipulation

**Version**: `numpy~=1.24.0` (minor version pinning)

**Rationale**:
- Foundation for scientific computing in Python
- Required dependency for scikit-learn and pandas
- Efficient array operations for data generation
- Random number generation with fixed seeds

**Features Used**:
- `np.random` - Random number generation (normal, uniform, poisson, choice)
- `np.clip` - Clipping values to valid ranges
- `np.array` - Array creation and manipulation
- `np.random.seed` - Reproducibility via fixed seeds

**Alternatives Considered**:
- None - NumPy is the standard for numerical computing in Python

**Impact**: Essential dependency, no alternatives

---

### 1.3 Pickle (Standard Library)

**Decision**: Use Python's built-in pickle module for model serialization

**Version**: Built-in (Python 3.9+)

**Rationale**:
- Standard Python serialization format
- Supported by scikit-learn for model persistence
- No additional dependencies
- Acceptable security risk (models trained internally in trusted environment)
- Simple and fast

**Features Used**:
- `pickle.dump` - Serialize models to .pkl files
- `pickle.load` - Deserialize models from .pkl files

**Alternatives Considered**:
- **joblib**: scikit-learn's preferred serialization, but pickle is simpler and sufficient
- **ONNX**: Cross-platform model format, overkill for project scope
- **JSON**: Not suitable for complex model objects

**Security Considerations**:
- Pickle is vulnerable to arbitrary code execution if loading untrusted files
- **Mitigation**: Models trained internally only, no external model sources
- **Acceptable Risk**: Controlled training environment (GitHub Actions CI/CD)

**Impact**: Simple, fast, acceptable security risk for internal use

---

## 2. Data Processing Libraries

### 2.1 pandas

**Decision**: Use pandas for data manipulation and CSV I/O

**Version**: `pandas~=2.0.0` (minor version pinning)

**Rationale**:
- Industry-standard for tabular data manipulation
- Excellent CSV reading/writing support
- DataFrame API simplifies data operations
- Integration with scikit-learn

**Features Used**:
- `pd.DataFrame` - Tabular data structure
- `pd.read_csv` - Load datasets from CSV
- `pd.to_csv` - Save datasets to CSV
- DataFrame operations: filtering, grouping, aggregation
- `drop_duplicates` - Duplicate detection
- `isnull` - Missing value detection

**Alternatives Considered**:
- **Polars**: Faster than pandas but less mature, unnecessary for dataset size
- **Dask**: Distributed computing, overkill for 1000 records
- **CSV module**: Too low-level, pandas provides better API

**Impact**: Simplifies data manipulation, standard choice

---

### 2.2 SciPy

**Decision**: Use SciPy for statistical tests and distributions

**Version**: `scipy~=1.10.0` (minor version pinning)

**Rationale**:
- Statistical functions for data quality validation
- Distribution tests (normality tests)
- Complement to NumPy for scientific computing

**Features Used**:
- `scipy.stats.normaltest` - Test for normal distribution
- Statistical distributions (if needed for advanced validation)

**Alternatives Considered**:
- **statsmodels**: More comprehensive but heavier, SciPy sufficient

**Impact**: Lightweight statistical validation

---

## 3. Development Tools

### 3.1 pytest

**Decision**: Use pytest as the testing framework

**Version**: `pytest~=7.4.0` (minor version pinning)

**Rationale**:
- Industry-standard Python testing framework
- Simple and intuitive API
- Excellent plugin ecosystem
- Good integration with CI/CD

**Features Used**:
- Test discovery and execution
- Fixtures for test setup
- Assertions
- Test coverage reporting (with pytest-cov)

**Test Scope**:
- Unit tests for data generation functions
- Unit tests for preprocessing functions
- Unit tests for feature engineering functions
- Unit tests for validation functions
- No property-based tests (partial enforcement)

**Alternatives Considered**:
- **unittest**: Standard library but more verbose
- **nose**: Deprecated, pytest is the modern choice

**Impact**: Standard testing framework, good developer experience

---

### 3.2 flake8

**Decision**: Use flake8 for PEP 8 linting

**Version**: `flake8~=6.0.0` (minor version pinning)

**Rationale**:
- Enforces PEP 8 coding standards
- Catches common errors and style issues
- Fast and lightweight
- Good CI/CD integration

**Configuration**:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203,W503
```

**Alternatives Considered**:
- **pylint**: More comprehensive but slower and stricter
- **black**: Auto-formatter, not just linter
- **ruff**: Faster but less mature

**Impact**: Enforces code quality standards

---

### 3.3 pytest-cov

**Decision**: Use pytest-cov for test coverage reporting

**Version**: `pytest-cov~=4.1.0` (minor version pinning)

**Rationale**:
- Integrates with pytest
- Generates coverage reports
- Identifies untested code

**Coverage Target**: > 60% for core modules

**Usage**:
```bash
pytest --cov=ml-pipeline --cov-report=html --cov-report=term
```

**Alternatives Considered**:
- **coverage.py**: Lower-level, pytest-cov provides better integration

**Impact**: Visibility into test coverage

---

### 3.4 Jupyter (Optional - Excluded)

**Decision**: Do NOT include Jupyter notebooks in the ML Pipeline

**Rationale**:
- Pure Python scripts are sufficient for training pipeline
- Notebooks add complexity and versioning challenges
- CI/CD requires executable scripts, not notebooks
- Notebooks useful for exploration but not production

**Impact**: Simplified codebase, no notebook dependencies

---

## 4. Version Pinning Strategy

### 4.1 Minor Version Pinning

**Decision**: Use minor version pinning (~=) for all dependencies

**Rationale**:
- **Exact pinning (==)**: Blocks security patches, too restrictive
- **No pinning**: Breaks reproducibility, unpredictable behavior
- **Minor pinning (~=)**: Balances reproducibility with security updates

**Pinning Format**:
```
package~=X.Y.Z
```

**Behavior**:
- Allows: X.Y.Z → X.Y.(Z+1) (patch updates)
- Blocks: X.Y.Z → X.(Y+1).0 (minor updates)
- Blocks: X.Y.Z → (X+1).0.0 (major updates)

**Examples**:
```
scikit-learn~=1.3.0   # Allows 1.3.1, 1.3.2, blocks 1.4.0
pandas~=2.0.0         # Allows 2.0.1, 2.0.2, blocks 2.1.0
numpy~=1.24.0         # Allows 1.24.1, 1.24.2, blocks 1.25.0
```

**Rationale for Compromise**:
- **Reproducibility**: Minor versions maintain API compatibility, results should be similar (±1% metrics)
- **Security**: Patch updates include security fixes and bug fixes
- **Maintenance**: Reduces dependency update burden

**Impact**: Balances reproducibility with security and maintainability

---

### 4.2 Dependency Update Policy

**Decision**: Review and update dependencies quarterly

**Process**:
1. Check for new minor versions quarterly
2. Test new versions in development environment
3. Validate model performance (metrics should be within ±2% of previous)
4. Update pinning if tests pass
5. Document changes in Git commit

**Rationale**: Regular updates prevent dependency drift while maintaining stability

**Impact**: Keeps dependencies reasonably current without frequent churn

---

## 5. Python Version

### 5.1 Python 3.9

**Decision**: Use Python 3.9 as the target Python version

**Rationale**:
- Stable and mature (released 2020)
- Good support from all dependencies
- Available on GitHub Actions and Render
- Balance between modern features and stability

**Features Used**:
- Type hints (PEP 484)
- f-strings
- Dataclasses (for configuration)
- pathlib for file operations

**Alternatives Considered**:
- **Python 3.11**: Faster but newer, potential compatibility issues
- **Python 3.8**: Older, missing some modern features
- **Python 3.10**: Good alternative, 3.9 chosen for broader compatibility

**Impact**: Stable, well-supported Python version

---

## 6. Complete Dependency List

### 6.1 Production Dependencies

**File**: `ml-pipeline/requirements.txt`

```txt
# Core ML Libraries
scikit-learn~=1.3.0
numpy~=1.24.0
scipy~=1.10.0

# Data Processing
pandas~=2.0.0

# No additional dependencies needed (pickle is built-in)
```

**Total Dependencies**: 4 packages (+ transitive dependencies)

**Rationale**: Minimal dependency footprint, only essential libraries

---

### 6.2 Development Dependencies

**File**: `ml-pipeline/requirements-dev.txt`

```txt
# Include production dependencies
-r requirements.txt

# Testing
pytest~=7.4.0
pytest-cov~=4.1.0

# Linting
flake8~=6.0.0

# Type Checking (optional)
mypy~=1.4.0
```

**Total Dev Dependencies**: 4 additional packages

**Rationale**: Standard development tools for testing and quality assurance

---

## 7. Dependency Security

### 7.1 Dependency Scanning

**Decision**: Use GitHub Dependabot for automated dependency scanning

**Rationale**:
- Built into GitHub, no additional setup
- Automatically detects vulnerable dependencies
- Creates pull requests for security updates
- Free for public repositories

**Configuration**: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/ml-pipeline"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

**Impact**: Automated security vulnerability detection

---

### 7.2 Dependency Pinning in Docker

**Decision**: Use same minor version pinning in Dockerfile

**Rationale**: Consistent dependency versions across development and production

**Dockerfile Snippet**:
```dockerfile
# Install ML Pipeline dependencies
COPY ml-pipeline/requirements.txt /app/ml-pipeline/
RUN pip install --no-cache-dir -r /app/ml-pipeline/requirements.txt
```

**Impact**: Consistent environment across dev and prod

---

## 8. Technology Stack Summary

### 8.1 Stack Overview

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **ML Framework** | scikit-learn | ~1.3.0 | Industry standard, CPU-optimized, sufficient for project |
| **Numerical Computing** | NumPy | ~1.24.0 | Foundation for scientific computing |
| **Data Processing** | pandas | ~2.0.0 | Standard for tabular data manipulation |
| **Statistics** | SciPy | ~1.10.0 | Statistical validation and tests |
| **Serialization** | pickle | Built-in | Simple, fast, acceptable security risk |
| **Testing** | pytest | ~7.4.0 | Industry-standard testing framework |
| **Linting** | flake8 | ~6.0.0 | PEP 8 enforcement |
| **Coverage** | pytest-cov | ~4.1.0 | Test coverage reporting |
| **Python Version** | Python | 3.9 | Stable, well-supported |
| **Version Pinning** | Minor (~=) | N/A | Balance reproducibility and security |

---

### 8.2 Dependency Graph

```
ML Pipeline
├── scikit-learn~=1.3.0
│   ├── numpy~=1.24.0
│   ├── scipy~=1.10.0
│   └── joblib (transitive)
├── pandas~=2.0.0
│   ├── numpy~=1.24.0
│   └── python-dateutil (transitive)
├── numpy~=1.24.0
└── scipy~=1.10.0
    └── numpy~=1.24.0

Development
├── pytest~=7.4.0
│   └── pluggy (transitive)
├── pytest-cov~=4.1.0
│   ├── pytest~=7.4.0
│   └── coverage (transitive)
└── flake8~=6.0.0
    ├── pycodestyle (transitive)
    ├── pyflakes (transitive)
    └── mccabe (transitive)
```

---

### 8.3 Technology Decisions Rationale Summary

**Why scikit-learn?**
- Industry standard for classical ML
- CPU-optimized (no GPU needed)
- Excellent documentation and community
- Sufficient for project requirements

**Why NumPy/pandas?**
- Standard Python data science stack
- Required by scikit-learn
- Excellent performance and API

**Why pickle?**
- Simple and fast
- Built-in (no dependencies)
- Acceptable security risk for internal use

**Why pytest/flake8?**
- Industry-standard development tools
- Good CI/CD integration
- Enforce code quality

**Why minor version pinning?**
- Balance reproducibility with security
- Allow patch updates (security fixes)
- Block breaking changes (minor/major updates)

**Why Python 3.9?**
- Stable and mature
- Good dependency support
- Available on deployment platforms

---

## 9. Technology Alternatives Not Chosen

### 9.1 ML Frameworks

**XGBoost / LightGBM / CatBoost**
- **Reason Not Chosen**: More powerful but overkill for dataset size (1000 records)
- **Trade-off**: Simpler stack vs. potentially better performance
- **Decision**: scikit-learn sufficient for project scope

**TensorFlow / PyTorch**
- **Reason Not Chosen**: Deep learning frameworks, not needed for tabular data
- **Trade-off**: Simpler stack vs. deep learning capabilities
- **Decision**: Classical ML sufficient for placement prediction

---

### 9.2 Serialization Formats

**joblib**
- **Reason Not Chosen**: scikit-learn's preferred format, but pickle is simpler
- **Trade-off**: Slightly better compression vs. standard library simplicity
- **Decision**: pickle sufficient, no additional dependency

**ONNX**
- **Reason Not Chosen**: Cross-platform model format, overkill for project
- **Trade-off**: Portability vs. complexity
- **Decision**: pickle sufficient for Python-only deployment

---

### 9.3 Data Processing

**Polars**
- **Reason Not Chosen**: Faster than pandas but less mature
- **Trade-off**: Performance vs. maturity and ecosystem
- **Decision**: pandas is standard, performance not critical for 1000 records

**Dask**
- **Reason Not Chosen**: Distributed computing, overkill for 1000 records
- **Trade-off**: Scalability vs. complexity
- **Decision**: pandas sufficient for dataset size

---

### 9.4 Development Tools

**Jupyter Notebooks**
- **Reason Not Chosen**: Useful for exploration but not production
- **Trade-off**: Interactive development vs. CI/CD compatibility
- **Decision**: Pure Python scripts for production pipeline

**pylint**
- **Reason Not Chosen**: More comprehensive but slower and stricter than flake8
- **Trade-off**: Comprehensive checks vs. speed and simplicity
- **Decision**: flake8 sufficient for code quality

---

## 10. Future Technology Considerations

### 10.1 Potential Future Additions

**MLflow**
- **Use Case**: Model registry and experiment tracking
- **When**: If model versioning becomes more complex
- **Impact**: Better model management, additional dependency

**DVC (Data Version Control)**
- **Use Case**: Dataset versioning and lineage
- **When**: If dataset versioning becomes critical
- **Impact**: Better data management, additional tooling

**Automated Hyperparameter Tuning**
- **Use Case**: Optuna, Hyperopt for automated tuning
- **When**: If manual tuning becomes insufficient
- **Impact**: Better model performance, longer training time

---

### 10.2 Technology Upgrade Path

**Python 3.11+**
- **Benefit**: Significant performance improvements (10-60% faster)
- **Risk**: Potential dependency compatibility issues
- **Timeline**: Consider after Python 3.11 becomes standard on deployment platforms

**scikit-learn 2.0+**
- **Benefit**: New features and performance improvements
- **Risk**: Breaking API changes
- **Timeline**: Evaluate when released, test thoroughly before upgrading

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC NFR Requirements

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial tech stack decisions document |
