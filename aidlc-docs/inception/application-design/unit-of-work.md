# Units of Work: Skill2Hire - Placement Prediction AI Web App

## Overview

This document defines the 4 units of work for the Skill2Hire project, organized for sequential development with clear boundaries and responsibilities.

**Decomposition Strategy**: 4 separate logical units in a monorepo structure, deployed as a single container.

**Development Sequence**: ML Pipeline → Backend API → Frontend → DevOps

---

## Unit Catalog

### Unit 1: ML Pipeline

**Unit ID**: `ml-pipeline`

**Purpose**: Complete machine learning lifecycle from dataset generation through model training, evaluation, and versioning.

**Type**: Standalone development unit (produces artifacts consumed by Backend)

**Components Assigned** (2 from application design + scripts):
- MLModelManager (ML Layer) - *Note: Implementation in Backend, but model artifacts produced here*
- FeatureEngineer (ML Layer) - *Note: Implementation in Backend, but feature engineering logic defined here*
- SkillDictionary (Utility) - Skill taxonomy data
- **Additional**: Data generation scripts, training scripts, evaluation scripts

**Responsibilities**:
1. **Dataset Generation**
   - Generate synthetic dataset with 1000+ records
   - Ensure balanced dataset (50% placed, 50% not placed)
   - No duplicate records
   - Fields: CGPA, Aptitude Score, Programming Skills (1-10), Communication Skills (1-10), Number of Projects, Internship Experience, Certifications Count, Branch, Placement Status

2. **Data Preprocessing**
   - Clean and validate data
   - Handle missing values
   - Feature scaling and encoding
   - Train-test split (80-20)

3. **Model Training**
   - Train Random Forest Classifier
   - Train Gradient Boosting Classifier
   - Train Logistic Regression
   - Train Voting Classifier (ensemble)
   - Hyperparameter tuning
   - Cross-validation

4. **Model Evaluation**
   - Calculate accuracy, precision, recall, F1-score, ROC-AUC
   - Generate confusion matrices
   - Compare model performance
   - Document evaluation metrics

5. **Model Versioning**
   - Save trained models as .pkl files
   - Version models in Git repository
   - Document model metadata (version, accuracy, training date)

**Inputs**:
- None (generates own data)
- Skill dictionary (JSON/CSV)

**Outputs**:
- Trained model files (.pkl):
  - `random_forest.pkl`
  - `gradient_boosting.pkl`
  - `logistic_regression.pkl`
  - `voting_classifier.pkl`
- Dataset files (CSV):
  - `synthetic_dataset.csv`
  - `train_data.csv`
  - `test_data.csv`
- Evaluation reports:
  - `model_evaluation.md`
  - `metrics.json`

**Dependencies**:
- **External**: scikit-learn, pandas, numpy
- **Internal**: None (standalone)

**Integration Points**:
- **→ Backend API**: Provides trained model files

**Directory Structure**:
```
ml-pipeline/
├── data/
│   ├── generate_dataset.py
│   ├── raw/
│   └── processed/
├── models/
│   ├── train.py
│   ├── evaluate.py
│   └── trained/
├── notebooks/
├── tests/
├── requirements.txt
└── README.md
```

---

### Unit 2: Backend API

**Unit ID**: `backend`

**Purpose**: Flask REST API serving prediction endpoints, orchestrating business logic, managing ML inference, and accessing database.

**Type**: Core application unit (serves Frontend, uses ML models)

**Components Assigned** (17 components):

**API Layer** (5):
1. PredictionBlueprint - `/api/predict` endpoint
2. AnalyticsBlueprint - `/api/insights` endpoint
3. ResumeBlueprint - `/api/resume/upload` endpoint
4. JobAnalysisBlueprint - `/api/analyze-job` endpoint
5. APIMiddleware - Security headers, rate limiting, CORS, logging

**Business Logic Layer** (6):
6. PredictionService - Prediction workflow orchestration
7. AnalyticsService - Analytics generation orchestration
8. ResumeParsingService - Resume parsing orchestration
9. NLPService - Job description NLP analysis
10. SkillGapAnalyzer - Skill comparison and suggestions
11. DataValidator - Schema-based input validation

**ML Layer** (2):
12. MLModelManager - Load and manage trained models (Singleton)
13. FeatureEngineer - Transform inputs to model features

**Data Access Layer** (1):
14. DataRepository - Supabase database operations

**Infrastructure Layer** (4):
15. CacheManager - Result caching (LRU, input hash)
16. Logger - Centralized logging (Singleton)
17. ConfigManager - Configuration management (Singleton)
18. SecurityHeadersMiddleware - HTTP security headers

**Utilities** (1):
19. ErrorHandler - Global error handling

**Responsibilities**:
1. **API Endpoints**
   - POST /api/predict - Generate placement prediction
   - GET /api/insights - Retrieve analytics
   - POST /api/resume/upload - Parse resume
   - POST /api/analyze-job - Analyze job description

2. **ML Inference**
   - Load trained models at startup (MLModelManager)
   - Transform user inputs to features (FeatureEngineer)
   - Generate predictions from ensemble models
   - Calculate confidence scores

3. **Business Logic**
   - Orchestrate prediction workflow (PredictionService)
   - Perform NLP analysis on job descriptions (NLPService)
   - Analyze skill gaps (SkillGapAnalyzer)
   - Parse resume files (ResumeParsingService)
   - Generate analytics (AnalyticsService)

4. **Data Management**
   - Store user inputs in Supabase
   - Store predictions in Supabase
   - Store job descriptions in Supabase
   - Query analytics data
   - Cache prediction results

5. **Security & Monitoring**
   - Apply security headers (SECURITY-04)
   - Enforce rate limiting
   - Validate all inputs (SECURITY-05)
   - Log all requests and errors (SECURITY-03)
   - Handle errors gracefully (SECURITY-15)

6. **Frontend Serving**
   - Serve static HTML/CSS/JS files from `/static`
   - Serve index.html at root `/`

**Inputs**:
- HTTP requests (JSON)
- Trained model files from ML Pipeline
- Frontend static files from Frontend unit

**Outputs**:
- HTTP responses (JSON)
- Served HTML/CSS/JS files
- Database records (Supabase)
- Log entries

**Dependencies**:
- **External**: Flask, Flask-CORS, Flask-Limiter, Pydantic/Marshmallow, supabase-py, NLTK/spaCy, PyPDF2/python-docx
- **Internal**: ML Pipeline (consumes models), Frontend (serves static files)

**Integration Points**:
- **← ML Pipeline**: Loads trained model files from `ml-pipeline/models/trained/`
- **→ Frontend**: Serves static files from `backend/app/static/`
- **← Frontend**: Receives API calls from JavaScript
- **→ Supabase**: Database operations
- **→ DevOps**: Deployed by Docker/GitHub Actions

**Directory Structure**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   ├── services/
│   ├── components/
│   ├── ml/
│   ├── data/
│   ├── infrastructure/
│   ├── utils/
│   └── static/  # Frontend files
├── tests/
├── config.py
├── requirements.txt
├── wsgi.py
└── README.md
```

---

### Unit 3: Frontend

**Unit ID**: `frontend`

**Purpose**: Single-page web application providing user interface for all features.

**Type**: Development unit (tightly coupled with Backend, served as static files)

**Components Assigned** (1):
1. FrontendApp - Complete client-side application

**Responsibilities**:
1. **User Input Forms**
   - Student profile form (9 fields)
   - Job description text area
   - Form validation (client-side)
   - Real-time input suggestions

2. **Prediction Display**
   - Show prediction probability (%)
   - Display confidence score
   - Render model comparison chart (Chart.js)
   - Show skill gap suggestions

3. **Analytics Dashboard**
   - Department-wise placement charts
   - CGPA vs placement correlation
   - Top skills visualization
   - Interactive filters

4. **Resume Upload**
   - File upload interface (PDF, DOCX)
   - Display parsing results
   - Auto-populate form fields
   - Show parsing confidence

5. **User Experience**
   - Loading states during API calls
   - Error message display
   - Responsive design (desktop, tablet)
   - Accessible UI (WCAG 2.1 AA)

**Inputs**:
- User interactions (clicks, form inputs, file uploads)
- API responses from Backend (JSON)

**Outputs**:
- Static files (HTML, CSS, JavaScript)
- HTTP requests to Backend API
- Rendered UI in browser

**Dependencies**:
- **External**: Chart.js (CDN)
- **Internal**: Backend API (REST endpoints)

**Integration Points**:
- **→ Backend API**: Calls REST endpoints via fetch()
- **← Backend**: Served as static files from Flask

**Directory Structure**:
```
frontend/
├── src/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       ├── charts.js
│       └── forms.js
├── tests/
└── README.md

# Note: Built files copied to backend/app/static/
```

**Deployment Note**: Despite being a separate development unit, Frontend is deployed as part of Backend (served as static files). This is a logical unit for development organization, not a separate deployment unit.

---

### Unit 4: DevOps

**Unit ID**: `devops`

**Purpose**: CI/CD pipeline, containerization, deployment automation, and infrastructure configuration.

**Type**: Infrastructure unit (deploys all other units)

**Components Assigned**: None (infrastructure configuration, not application components)

**Responsibilities**:
1. **Containerization**
   - Dockerfile for single-container deployment
   - Docker Compose for local development
   - Multi-stage build optimization
   - Include ML models, Backend, Frontend in container

2. **CI/CD Pipeline (GitHub Actions)**
   - **Linting**: flake8, pylint for Python code
   - **Testing**: pytest for unit tests, hypothesis for property-based tests
   - **Model Training**: Trigger training on push (developer-initiated)
   - **Build**: Docker image build
   - **Deploy**: Automated deployment to Render
   - **Health Check**: Post-deployment verification

3. **Deployment Configuration**
   - Render platform configuration (render.yaml)
   - Environment variable templates (.env.example)
   - Deployment scripts (deploy.sh)
   - Health check endpoints

4. **Environment Management**
   - Development environment setup
   - Staging environment (optional)
   - Production environment
   - Environment variable management

5. **Monitoring Setup**
   - Log aggregation configuration
   - Metrics collection setup
   - Alert configuration
   - Health check monitoring

**Inputs**:
- Source code from all units
- Trained models from ML Pipeline
- Environment variables (secrets)

**Outputs**:
- Docker image
- Deployed application on Render
- CI/CD workflow files
- Deployment scripts
- Configuration files

**Dependencies**:
- **External**: Docker, GitHub Actions, Render platform
- **Internal**: All units (deploys everything)

**Integration Points**:
- **← ML Pipeline**: Includes trained models in Docker image
- **← Backend**: Includes Backend code in Docker image
- **← Frontend**: Includes Frontend static files in Docker image
- **→ Render**: Deploys container to hosting platform
- **→ GitHub**: CI/CD workflows

**Directory Structure**:
```
devops/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── deploy.sh
│   ├── health_check.sh
│   └── setup_env.sh
├── config/
│   ├── render.yaml
│   └── .env.example
└── README.md
```

**CI/CD Workflow**:
```
1. Code Push → GitHub
2. Lint (flake8, pylint)
3. Run Tests (pytest, hypothesis)
4. Train Models (if ML code changed)
5. Build Docker Image
6. Push to Registry
7. Deploy to Render
8. Health Check
9. Notify (success/failure)
```

---

## Unit Summary

| Unit | Components | Type | Dependencies | Outputs |
|------|-----------|------|--------------|---------|
| **ML Pipeline** | 2 + scripts | Standalone | None | Model files (.pkl), datasets |
| **Backend API** | 17 | Core application | ML Pipeline, Frontend | REST API, served frontend |
| **Frontend** | 1 | Development | Backend API | Static files (HTML/CSS/JS) |
| **DevOps** | 0 | Infrastructure | All units | Docker image, deployed app |

**Total Components**: 20 application components + infrastructure

---

## Code Organization Strategy (Greenfield)

### Repository Structure: Monorepo

**Rationale**: Single repository with separate directories for each unit enables:
- Unified version control
- Simplified dependency management
- Easier cross-unit refactoring
- Single CI/CD pipeline
- Shared documentation

### Directory Layout

```
skill2hire/                    # Repository root
├── .github/workflows/         # CI/CD pipelines
├── ml-pipeline/               # Unit 1
├── backend/                   # Unit 2
├── frontend/                  # Unit 3
├── devops/                    # Unit 4
├── aidlc-docs/                # AI-DLC documentation
├── .gitignore
├── README.md
├── LICENSE
└── requirements.txt           # Root dependencies (if any)
```

### Deployment Model: Single Container

**Physical Deployment**: Despite 4 logical units, deployment is a single Docker container containing:
- Backend Flask application
- ML models (loaded from ml-pipeline/models/trained/)
- Frontend static files (served from backend/app/static/)
- All dependencies

**Rationale**:
- Simplified deployment (single container)
- Reduced operational complexity
- Meets performance requirements
- Cost-effective for initial release
- Frontend tightly coupled with Backend

### Development Workflow

**Sequential Development** (as per approved plan):
1. **ML Pipeline** → Develop and train models first
2. **Backend API** → Develop API using trained models
3. **Frontend** → Develop UI calling Backend API
4. **DevOps** → Set up CI/CD and deployment

**Integration Points**:
- ML Pipeline produces models → Backend consumes
- Backend exposes API → Frontend calls
- Frontend builds static files → Backend serves
- DevOps deploys all units together

---

## Naming Conventions

### Python Modules
- **Packages**: lowercase with underscores (e.g., `prediction_service`)
- **Classes**: PascalCase (e.g., `PredictionService`)
- **Functions**: lowercase with underscores (e.g., `predict_placement`)
- **Constants**: UPPERCASE with underscores (e.g., `MAX_CACHE_SIZE`)

### JavaScript
- **Files**: camelCase (e.g., `app.js`, `charts.js`)
- **Classes**: PascalCase (e.g., `FrontendApp`)
- **Functions**: camelCase (e.g., `handleFormSubmit`)
- **Constants**: UPPERCASE with underscores (e.g., `API_BASE_URL`)

### Files and Directories
- **Directories**: lowercase with hyphens (e.g., `ml-pipeline`, `backend`)
- **Python files**: lowercase with underscores (e.g., `prediction_service.py`)
- **Config files**: lowercase with dots (e.g., `config.py`, `.env.example`)

---

## Testing Strategy by Unit

### ML Pipeline
- **Unit Tests**: Test data generation, preprocessing, feature engineering
- **Property-Based Tests**: Test feature transformation properties
- **Integration Tests**: Test model training pipeline end-to-end

### Backend API
- **Unit Tests**: Test services, components, API endpoints (mocked dependencies)
- **Property-Based Tests**: Test feature engineering, serialization
- **Integration Tests**: Test prediction flow with real models and test database
- **API Tests**: Test REST endpoints with various inputs

### Frontend
- **Unit Tests**: Test JavaScript functions (if complex logic)
- **Integration Tests**: Test API client interactions
- **E2E Tests**: Test complete user workflows (optional)

### DevOps
- **Pipeline Tests**: Test CI/CD workflow stages
- **Deployment Tests**: Test deployment scripts
- **Health Checks**: Test application health endpoints

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Approved (Pending)
- **Created By**: AI-DLC Units Generation
- **Next**: unit-of-work-dependency.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial units of work document |

