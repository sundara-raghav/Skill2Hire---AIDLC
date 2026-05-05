# Unit Dependencies: Skill2Hire - Placement Prediction AI Web App

## Overview

This document defines dependencies, integration points, and data flow between the 4 units of work.

---

## Dependency Matrix

### Unit-to-Unit Dependencies

| From Unit ↓ / To Unit → | ML Pipeline | Backend API | Frontend | DevOps |
|--------------------------|-------------|-------------|----------|--------|
| **ML Pipeline** | - | Produces models | - | Deployed by |
| **Backend API** | Consumes models | - | Serves files | Deployed by |
| **Frontend** | - | Calls API | - | Deployed by |
| **DevOps** | Deploys | Deploys | Deploys | - |

### Dependency Types

**Build-time Dependencies**:
- Backend API ← ML Pipeline (model files)
- Backend API ← Frontend (static files)

**Runtime Dependencies**:
- Frontend → Backend API (REST API calls)
- Backend API → Supabase (database)

**Deployment Dependencies**:
- All Units ← DevOps (containerization, CI/CD)

---

## Integration Points

### 1. ML Pipeline → Backend API

**Type**: Build-time / File-based

**Mechanism**: Backend loads trained model files at startup

**Data Flow**:
```
ml-pipeline/models/trained/*.pkl
    ↓ (file system)
backend/app/ml/model_manager.py (MLModelManager.load_models())
    ↓ (in-memory)
Loaded models ready for inference
```

**Files Transferred**:
- `random_forest.pkl` (~5-10 MB)
- `gradient_boosting.pkl` (~5-10 MB)
- `logistic_regression.pkl` (~1-2 MB)
- `voting_classifier.pkl` (~15-20 MB)

**Integration Contract**:
- **Location**: Models must be in `ml-pipeline/models/trained/`
- **Format**: scikit-learn pickle format (.pkl)
- **Naming**: Exact filenames as specified
- **Compatibility**: Models trained with same scikit-learn version as Backend

**Error Handling**:
- If models not found: Backend fails to start, logs error
- If models incompatible: Backend fails to start, logs version mismatch
- If models corrupted: Backend fails to start, logs corruption error

---

### 2. Frontend → Backend API

**Type**: Runtime / HTTP-based

**Mechanism**: JavaScript fetch() calls to REST endpoints

**Data Flow**:
```
frontend/src/js/api.js
    ↓ HTTP POST /api/predict (JSON)
backend/app/api/prediction.py (PredictionBlueprint)
    ↓ PredictionService
    ↓ MLModelManager, NLPService, etc.
    ↑ PredictionResult (JSON)
frontend/src/js/app.js (display results)
```

**API Endpoints Used**:
1. **POST /api/predict**
   - Request: StudentProfile + job_description
   - Response: PredictionResult

2. **GET /api/insights**
   - Request: Query params (branch, date range)
   - Response: AnalyticsResult

3. **POST /api/resume/upload**
   - Request: multipart/form-data (file)
   - Response: ResumeData

4. **POST /api/analyze-job**
   - Request: job_description
   - Response: JobAnalysisResult

**Integration Contract**:
- **Protocol**: HTTPS in production, HTTP in development
- **Format**: JSON for all requests/responses (except file upload)
- **Authentication**: None (open access)
- **Rate Limiting**: 60 requests per minute per IP
- **CORS**: Allowed origins configured in Backend

**Error Handling**:
- **Network Error**: Frontend displays "Connection failed" message
- **4xx Errors**: Frontend displays validation error messages
- **5xx Errors**: Frontend displays "Server error, please try again"
- **Timeout**: Frontend displays "Request timeout" after 10 seconds

---

### 3. Backend API → Frontend

**Type**: Build-time + Runtime / File serving

**Mechanism**: Flask serves static files from `/static` directory

**Data Flow (Build)**:
```
frontend/src/*.html, *.css, *.js
    ↓ (copy during build)
backend/app/static/
    ↓ (Flask static file serving)
Browser (HTTP GET /)
```

**Data Flow (Runtime)**:
```
Browser: GET /
    ↓
backend/app/__init__.py (Flask route)
    ↓
Serve backend/app/static/index.html
    ↓
Browser loads HTML, CSS, JS
```

**Files Served**:
- `index.html` - Main HTML page
- `css/styles.css` - Stylesheet
- `js/app.js` - Main application logic
- `js/api.js` - API client
- `js/charts.js` - Chart.js visualizations
- `js/forms.js` - Form handling

**Integration Contract**:
- **Location**: Frontend files must be in `backend/app/static/`
- **Root Route**: `/` serves `index.html`
- **Static Route**: `/static/*` serves static files
- **Cache Headers**: Set appropriate cache headers for static assets

**Build Process**:
```bash
# Copy frontend files to backend static directory
cp -r frontend/src/* backend/app/static/
```

---

### 4. Backend API → Supabase

**Type**: Runtime / Database connection

**Mechanism**: Supabase Python client

**Data Flow**:
```
backend/app/data/repository.py (DataRepository)
    ↓ supabase-py client
    ↓ HTTPS (TLS 1.2+)
Supabase PostgreSQL database
```

**Tables Accessed**:
1. **user_inputs** - Store student profiles
2. **predictions** - Store prediction results
3. **job_descriptions** - Store analyzed job descriptions
4. **insights** - Store pre-computed analytics

**Integration Contract**:
- **Connection**: HTTPS with TLS 1.2+
- **Authentication**: API key (environment variable)
- **Queries**: Parameterized queries only (no SQL injection)
- **Connection Pool**: Managed by Supabase client
- **Retry Logic**: 3 retries with exponential backoff

**Error Handling**:
- **Connection Failed**: Log error, return 503 Service Unavailable
- **Query Failed**: Log error, return 500 Internal Server Error
- **Timeout**: Log error, retry up to 3 times
- **Rate Limit**: Log warning, implement backoff

---

### 5. DevOps → All Units

**Type**: Deployment / CI/CD orchestration

**Mechanism**: Docker build + GitHub Actions + Render deployment

**Data Flow**:
```
GitHub Push
    ↓
.github/workflows/ci-cd.yml (GitHub Actions)
    ↓
1. Lint all units
2. Test all units
3. Train models (ML Pipeline)
4. Build Docker image (all units)
5. Push to registry
6. Deploy to Render
    ↓
Render platform (running container)
```

**Docker Build Process**:
```dockerfile
# Multi-stage build
FROM python:3.9 AS builder
# Install dependencies

FROM python:3.9-slim
# Copy ML models
COPY ml-pipeline/models/trained/ /app/models/
# Copy Backend code
COPY backend/ /app/backend/
# Copy Frontend static files
COPY frontend/src/ /app/backend/app/static/
# Set entrypoint
CMD ["gunicorn", "backend.wsgi:app"]
```

**Integration Contract**:
- **Build Context**: Repository root
- **Model Location**: Models copied to `/app/models/` in container
- **Backend Location**: Backend code in `/app/backend/`
- **Frontend Location**: Static files in `/app/backend/app/static/`
- **Port**: Container exposes port 8000
- **Health Check**: `/health` endpoint returns 200 OK

---

## Critical Path Dependencies

### Development Sequence

```
1. ML Pipeline (standalone)
   ↓ Produces: trained models
2. Backend API (depends on ML Pipeline)
   ↓ Provides: REST API
3. Frontend (depends on Backend API)
   ↓ Produces: static files
4. DevOps (depends on all units)
   ↓ Produces: deployed application
```

**Critical Path**: ML Pipeline → Backend API → Frontend → DevOps

**Parallel Opportunities**: None (sequential development per approved plan)

---

## Shared Resources

### 1. Skill Dictionary

**Shared By**: ML Pipeline, Backend API (NLPService)

**Location**: `ml-pipeline/data/skill_dictionary.json`

**Access Pattern**:
- ML Pipeline: Reads during data generation
- Backend API: Loads at startup, used by NLPService

**Format**:
```json
{
  "programming_languages": ["Python", "Java", "JavaScript", ...],
  "frameworks": ["Flask", "React", "Django", ...],
  "tools": ["Git", "Docker", "AWS", ...],
  "soft_skills": ["Communication", "Leadership", ...]
}
```

---

### 2. Configuration

**Shared By**: All units

**Location**: Environment variables + config files

**Backend Config**:
- `backend/config.py` - Default configuration
- Environment variables - Overrides

**ML Pipeline Config**:
- `ml-pipeline/config.py` - Training hyperparameters

**DevOps Config**:
- `devops/config/render.yaml` - Render configuration
- `devops/config/.env.example` - Environment template

---

### 3. Logging

**Shared By**: Backend API (all components)

**Mechanism**: Centralized Logger (Singleton)

**Log Destination**: Centralized log service (configured in Backend)

**Log Format**:
```json
{
  "timestamp": "2026-05-05T12:00:00Z",
  "level": "INFO",
  "request_id": "abc123",
  "component": "PredictionService",
  "message": "Prediction generated",
  "context": {...}
}
```

---

## Dependency Validation

### Pre-Development Checklist

**Before Backend Development**:
- [ ] ML Pipeline has produced trained models
- [ ] Models are in `ml-pipeline/models/trained/`
- [ ] Models are compatible with Backend scikit-learn version

**Before Frontend Development**:
- [ ] Backend API is running
- [ ] API endpoints are accessible
- [ ] API contract is documented

**Before DevOps Setup**:
- [ ] All units have code complete
- [ ] Tests are passing
- [ ] Models are trained
- [ ] Frontend files are ready

---

## Integration Testing Strategy

### Per-Unit Integration Tests

**ML Pipeline**:
- Test: Model training pipeline end-to-end
- Verify: Models saved correctly, can be loaded

**Backend API**:
- Test: Load models from ML Pipeline
- Test: Serve frontend static files
- Test: Database operations with Supabase
- Verify: All integration points working

**Frontend**:
- Test: API calls to Backend
- Verify: Responses handled correctly

**DevOps**:
- Test: Docker build includes all units
- Test: Deployment to Render succeeds
- Verify: Health check passes

### End-to-End Tests

**Complete User Flow**:
1. User loads frontend (served by Backend)
2. User submits prediction request
3. Backend loads models (from ML Pipeline)
4. Backend generates prediction
5. Backend stores in Supabase
6. Frontend displays results

**Verify**:
- All units working together
- Data flows correctly
- No integration failures

---

## Dependency Management

### Python Dependencies

**ML Pipeline** (`ml-pipeline/requirements.txt`):
```
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
```

**Backend** (`backend/requirements.txt`):
```
Flask==2.3.2
Flask-CORS==4.0.0
Flask-Limiter==3.3.1
scikit-learn==1.3.0  # Must match ML Pipeline
pandas==2.0.3
numpy==1.24.3
pydantic==2.0.3
supabase==1.0.3
nltk==3.8.1
PyPDF2==3.0.1
python-docx==0.8.11
gunicorn==21.2.0
```

**Version Compatibility**:
- scikit-learn version MUST match between ML Pipeline and Backend
- Python version: 3.9+ for all units

### JavaScript Dependencies

**Frontend** (CDN):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0"></script>
```

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Approved (Pending)
- **Created By**: AI-DLC Units Generation

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial unit dependency document |

