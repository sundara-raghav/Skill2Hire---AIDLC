# Application Design: Skill2Hire - Placement Prediction AI Web App

## Document Overview

This consolidated document provides a comprehensive overview of the Skill2Hire application architecture. For detailed specifications, refer to the individual design documents:

- **components.md** - Detailed component definitions and responsibilities
- **component-methods.md** - Method signatures and interfaces
- **services.md** - Service layer design and orchestration patterns
- **component-dependency.md** - Dependency relationships and data flow

---

## Executive Summary

**Architecture Style**: Hybrid Layered/Feature-based Architecture
- **Layered structure** for cross-cutting concerns (API, Data Access, Infrastructure)
- **Feature-based modules** for business capabilities (Prediction, Analytics, Resume)

**Key Design Decisions**:
1. **Component Organization**: Hybrid approach combining layers and features
2. **ML Model Management**: Singleton pattern, load once at startup
3. **NLP Processing**: Separate dedicated service component
4. **Data Access**: Direct Supabase client (no repository abstraction)
5. **API Structure**: Blueprint-based organization
6. **Frontend**: Single-page application with dynamic sections
7. **Resume Processing**: Synchronous parsing
8. **Caching**: Result caching based on input hash
9. **Error Handling**: Middleware-based with Flask error handlers
10. **Configuration**: Hybrid (config files + environment variables)
11. **Logging**: Centralized logger shared across components
12. **Service Layer**: Partial (only for complex workflows)
13. **Validation**: Schema-based using Pydantic/Marshmallow
14. **Analytics**: Hybrid (pre-computed + on-demand)
15. **Dependency Injection**: Partial (key components only)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                                                              │
│                      FrontendApp (Browser)                   │
│                  HTML5 + CSS3 + JavaScript + Chart.js       │
└──────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON REST API
┌─────────────────────────┴───────────────────────────────────┐
│                        API LAYER (Flask)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Prediction   │  │ Analytics    │  │ Resume       │     │
│  │ Blueprint    │  │ Blueprint    │  │ Blueprint    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────────────────────────┐   │
│  │ Job Analysis │  │ API Middleware                    │   │
│  │ Blueprint    │  │ (Security, Rate Limit, CORS, Log) │   │
│  └──────────────┘  └──────────────────────────────────┘   │
└─────────┬──────────────────┬──────────────────┬─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│                   BUSINESS LOGIC LAYER                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SERVICES (Partial Layer)                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ Prediction   │  │ Analytics    │  │ Resume     │ │  │
│  │  │ Service      │  │ Service      │  │ Parsing    │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              BUSINESS COMPONENTS                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ NLP Service  │  │ Skill Gap    │  │ Data       │ │  │
│  │  │              │  │ Analyzer     │  │ Validator  │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────┬──────────────────┬──────────────────┬─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│                    ML & DATA LAYERS                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ML Model     │  │ Feature      │  │ Data         │     │
│  │ Manager      │  │ Engineer     │  │ Repository   │     │
│  │ (Singleton)  │  │              │  │ (Supabase)   │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
└──────────────────────────────────────────────┼──────────────┘
                                              │
┌─────────────────────────────────────────────┴───────────────┐
│                   INFRASTRUCTURE LAYER                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Cache        │  │ Logger       │  │ Config       │     │
│  │ Manager      │  │ (Singleton)  │  │ Manager      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Security     │  │ Error        │                        │
│  │ Headers      │  │ Handler      │                        │
│  └──────────────┘  └──────────────┘                        │
└──────────────────────────────────────────────────────────────┘

External Services:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Supabase    │  │   Render     │  │   GitHub     │
│  Database    │  │  Hosting     │  │   Actions    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Component Catalog Summary

### Total Components: 21

**Presentation Layer** (1):
- FrontendApp - Single-page web application

**API Layer** (5):
- PredictionBlueprint - Prediction endpoints
- AnalyticsBlueprint - Analytics endpoints
- ResumeBlueprint - Resume upload endpoints
- JobAnalysisBlueprint - Job analysis endpoints
- APIMiddleware - Cross-cutting concerns

**Business Logic Layer** (6):
- PredictionService - Prediction orchestration
- AnalyticsService - Analytics orchestration
- ResumeParsingService - Resume parsing
- NLPService - Job description analysis
- SkillGapAnalyzer - Skill comparison
- DataValidator - Input validation

**ML Layer** (2):
- MLModelManager - Model lifecycle management
- FeatureEngineer - Feature transformation

**Data Access Layer** (1):
- DataRepository - Supabase operations

**Infrastructure Layer** (4):
- CacheManager - Result caching
- Logger - Centralized logging
- ConfigManager - Configuration management
- SecurityHeadersMiddleware - HTTP security headers

**Utility Components** (2):
- SkillDictionary - Skill taxonomy
- ErrorHandler - Global error handling

---

## Key Workflows

### 1. Prediction Workflow

```
User Input → PredictionBlueprint → PredictionService
    ↓
1. Calculate input hash
2. Check cache (CacheManager)
3. If cache miss:
   a. Analyze job description (NLPService)
   b. Transform features (FeatureEngineer)
   c. Generate predictions (MLModelManager)
      - Random Forest
      - Gradient Boosting
      - Logistic Regression
      - Voting Classifier (ensemble)
   d. Analyze skill gaps (SkillGapAnalyzer)
   e. Store in database (DataRepository)
   f. Cache result
4. Return PredictionResult
    ↓
Frontend Display (charts, suggestions)
```

**Performance Target**: <5 seconds end-to-end

---

### 2. Analytics Workflow

```
User Request → AnalyticsBlueprint → AnalyticsService
    ↓
1. Parse filters (branch, date range)
2. Generate cache key
3. Check cache (CacheManager)
4. If cache miss:
   a. Check pre-computed metrics (DataRepository)
   b. Calculate on-demand if needed:
      - Department placement rates
      - CGPA correlation
      - Top skills frequency
   c. Format results
   d. Cache with TTL
5. Return AnalyticsResult
    ↓
Frontend Dashboard (charts, statistics)
```

**Caching Strategy**: Pre-computed (24h TTL), On-demand (1h TTL)

---

### 3. Resume Upload Workflow

```
User Upload → ResumeBlueprint → ResumeParsingService
    ↓
1. Validate file (type, size)
2. Extract text (PDF/DOCX)
3. Parse sections:
   a. Education (CGPA, branch)
   b. Skills (match against dictionary)
   c. Experience (projects, internships, certs)
4. Validate extracted data (DataValidator)
5. Calculate confidence score
6. Return ResumeData
    ↓
Frontend Form Population
```

**Processing**: Synchronous (immediate response)

---

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Styling (Flexbox/Grid)
- **JavaScript (ES6+)** - Client-side logic
- **Chart.js** - Data visualization

### Backend
- **Python 3.9+** - Programming language
- **Flask** - Web framework
- **Flask-CORS** - CORS handling
- **Flask-Limiter** - Rate limiting
- **Pydantic/Marshmallow** - Schema validation

### Machine Learning
- **scikit-learn** - ML models and preprocessing
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **NLTK/spaCy** - NLP processing

### Database
- **Supabase** - PostgreSQL database
- **supabase-py** - Python client

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **Render** - Hosting platform
- **gunicorn** - WSGI server

### Testing
- **pytest** - Testing framework
- **hypothesis** - Property-based testing
- **pytest-mock** - Mocking

---

## Data Models

### Database Schema (Supabase)

#### Table: user_inputs
```sql
CREATE TABLE user_inputs (
    input_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    cgpa DECIMAL(3,2) NOT NULL,
    aptitude_score DECIMAL(5,2) NOT NULL,
    programming_skills INTEGER NOT NULL CHECK (programming_skills BETWEEN 1 AND 10),
    communication_skills INTEGER NOT NULL CHECK (communication_skills BETWEEN 1 AND 10),
    num_projects INTEGER NOT NULL,
    internship_experience BOOLEAN NOT NULL,
    certifications_count INTEGER NOT NULL,
    branch VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Table: predictions
```sql
CREATE TABLE predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    input_id UUID REFERENCES user_inputs(input_id),
    prediction_probability DECIMAL(5,2) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    random_forest_pred DECIMAL(5,2),
    gradient_boosting_pred DECIMAL(5,2),
    logistic_regression_pred DECIMAL(5,2),
    ensemble_pred DECIMAL(5,2),
    skill_gap_suggestions TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Table: job_descriptions
```sql
CREATE TABLE job_descriptions (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_description TEXT NOT NULL,
    extracted_skills TEXT[],
    skill_categories JSONB,
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Table: insights
```sql
CREATE TABLE insights (
    insight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value JSONB NOT NULL,
    filters JSONB,
    computed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

---

## API Endpoints

### Prediction API
- **POST /api/predict** - Generate placement prediction
  - Request: StudentProfile + job_description
  - Response: PredictionResult with model breakdown

### Analytics API
- **GET /api/insights** - Retrieve college-wide analytics
  - Query params: branch, start_date, end_date
  - Response: AnalyticsResult with charts data

### Resume API
- **POST /api/resume/upload** - Upload and parse resume
  - Request: multipart/form-data with file
  - Response: ResumeData with extracted fields

### Job Analysis API
- **POST /api/analyze-job** - Analyze job description
  - Request: job_description text
  - Response: JobAnalysisResult with skills

---

## Security Implementation

### Security Baseline Compliance

The application implements all 15 security baseline rules (SECURITY-01 through SECURITY-15):

**SECURITY-01**: Encryption at Rest and in Transit
- Supabase enforces TLS 1.2+ for all connections
- Database storage encryption enabled

**SECURITY-02**: Access Logging
- All API requests logged with timestamp, request ID, endpoint

**SECURITY-03**: Application-Level Logging
- Centralized Logger with structured logging
- No sensitive data in logs (passwords, tokens, PII)

**SECURITY-04**: HTTP Security Headers
- SecurityHeadersMiddleware applies all required headers:
  - Content-Security-Policy
  - Strict-Transport-Security
  - X-Content-Type-Options
  - X-Frame-Options
  - Referrer-Policy

**SECURITY-05**: Input Validation
- DataValidator validates all API parameters
- Schema-based validation (Pydantic/Marshmallow)
- Parameterized queries (Supabase client)

**SECURITY-06**: Least-Privilege Access
- Supabase RLS policies restrict data access
- API keys scoped to minimum required permissions

**SECURITY-07**: Restrictive Network Configuration
- Render platform handles network security
- No direct database access from public internet

**SECURITY-08**: Application-Level Access Control
- Rate limiting on all endpoints (Flask-Limiter)
- CORS restricted to allowed origins
- No authentication required (open access per requirements)

**SECURITY-09**: Security Hardening
- No default credentials
- Production error responses hide stack traces
- Framework versions kept current

**SECURITY-10**: Software Supply Chain Security
- Dependency pinning with requirements.txt
- Vulnerability scanning in CI/CD
- No `latest` tags in Dockerfile

**SECURITY-11**: Secure Design Principles
- Rate limiting on all public endpoints
- Defense in depth (validation + sanitization + parameterized queries)

**SECURITY-12**: Authentication and Credential Management
- No hardcoded credentials
- Secrets in environment variables
- (Note: No user authentication per requirements)

**SECURITY-13**: Software and Data Integrity
- No unsafe deserialization
- CI/CD pipeline access controlled

**SECURITY-14**: Alerting and Monitoring
- Comprehensive logging to centralized service
- Log retention: 90 days minimum
- Monitoring dashboard for key metrics

**SECURITY-15**: Exception Handling
- Global error handler catches unhandled exceptions
- Fail-closed behavior (deny on error)
- Resource cleanup in error paths

---

## Performance Considerations

### Optimization Strategies

**1. Model Loading**
- Load models once at startup (Singleton pattern)
- Models kept in memory for fast inference
- Estimated load time: 5-10 seconds

**2. Caching**
- Result caching based on input hash
- Cache hit rate target: >60%
- TTL: Predictions (1 hour), Analytics (24 hours)

**3. Database Queries**
- Pre-computed analytics metrics
- Indexed columns for common queries
- Connection pooling via Supabase client

**4. NLP Processing**
- Cache job description analysis
- Simple keyword extraction (not deep NLP)
- Preprocessing optimized for speed

**5. Feature Engineering**
- Pre-fitted encoders and scalers
- Vectorized operations with numpy
- Minimal transformation overhead

---

## Scalability Considerations

### Current Limitations
- Single-container deployment
- In-memory caching (not distributed)
- Synchronous request processing

### Future Scaling Options
1. **Horizontal Scaling**: Deploy multiple containers behind load balancer
2. **Distributed Caching**: Replace in-memory cache with Redis
3. **Async Processing**: Move resume parsing to background queue
4. **Database Optimization**: Add read replicas for analytics queries
5. **CDN**: Serve static frontend assets from CDN

---

## Testing Strategy

### Unit Testing
- **Services**: Mock all dependencies
- **Components**: Test in isolation
- **Utilities**: Test pure functions

### Property-Based Testing (Partial)
- **Feature Engineering**: Test transformation properties
- **Model Serialization**: Test save/load round-trips
- **Data Validation**: Test validation rules

### Integration Testing
- **API Endpoints**: Test with test database
- **ML Pipeline**: Test with real models
- **Database Operations**: Test with Supabase test project

### End-to-End Testing
- **Prediction Flow**: Full workflow from input to result
- **Analytics Flow**: Full dashboard data retrieval
- **Resume Flow**: Upload to form population

---

## Deployment Architecture

### Docker Container
```
┌─────────────────────────────────────┐
│         Docker Container            │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   gunicorn (WSGI Server)      │ │
│  │   ├─ Worker 1 (Flask App)     │ │
│  │   ├─ Worker 2 (Flask App)     │ │
│  │   └─ Worker N (Flask App)     │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   ML Models (.pkl files)      │ │
│  │   ├─ random_forest.pkl        │ │
│  │   ├─ gradient_boosting.pkl    │ │
│  │   ├─ logistic_regression.pkl  │ │
│  │   └─ voting_classifier.pkl    │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Static Files                │ │
│  │   ├─ index.html               │ │
│  │   ├─ styles.css               │ │
│  │   └─ app.js                   │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
         │
         ↓ HTTPS
┌─────────────────────────────────────┐
│         Render Platform             │
│  ├─ Load Balancer                  │
│  ├─ TLS Termination                │
│  └─ Health Checks                  │
└─────────────────────────────────────┘
```

### CI/CD Pipeline (GitHub Actions)
```
1. Code Push to main branch
    ↓
2. Lint (flake8, pylint)
    ↓
3. Run Unit Tests (pytest)
    ↓
4. Run Property-Based Tests (hypothesis)
    ↓
5. Security Scan (bandit, safety)
    ↓
6. Build Docker Image
    ↓
7. Push to Container Registry
    ↓
8. Deploy to Render
    ↓
9. Health Check
    ↓
10. Notify (success/failure)
```

---

## Configuration Management

### Environment Variables (Production)
```
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=xxx

# ML Models
MODEL_DIR=/app/models

# Caching
CACHE_MAX_SIZE=1000
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_SERVICE_URL=https://logs.example.com
```

### Config Files (Defaults)
```python
# config.py
class Config:
    # Flask
    DEBUG = False
    TESTING = False
    
    # ML
    MODEL_DIR = 'models/'
    
    # Cache
    CACHE_MAX_SIZE = 1000
    CACHE_TTL = 3600
    
    # Rate Limiting
    RATE_LIMIT = "60 per minute"
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # Security Headers
    CSP_POLICY = "default-src 'self'"
    HSTS_MAX_AGE = 31536000
```

---

## Monitoring and Observability

### Metrics to Track
- **API Metrics**: Request rate, response time, error rate
- **ML Metrics**: Prediction time, model accuracy, cache hit rate
- **Database Metrics**: Query time, connection pool usage
- **System Metrics**: CPU, memory, disk usage

### Logging Strategy
- **Structured Logging**: JSON format with context
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Aggregation**: Centralized log service
- **Log Retention**: 90 days minimum

### Alerting
- **Error Rate**: Alert if >5% of requests fail
- **Response Time**: Alert if p95 >5 seconds
- **Model Loading**: Alert if models fail to load
- **Database**: Alert on connection failures

---

## Future Enhancements

### Phase 2 Features
1. **User Authentication**: Add login system for personalized tracking
2. **Batch Predictions**: Support bulk student data upload
3. **Model Retraining**: Automated retraining pipeline
4. **Advanced NLP**: Semantic analysis with transformers
5. **Real-time Dashboard**: WebSocket-based live updates

### Phase 3 Features
1. **Mobile App**: Native iOS/Android applications
2. **Recommendation Engine**: Personalized job recommendations
3. **Interview Preparation**: AI-powered interview coaching
4. **Career Path Planning**: Long-term career guidance
5. **Integration**: Connect with job portals and ATS systems

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Approved (Pending)
- **Author**: AI-DLC Application Design
- **Reviewers**: Project Stakeholder

---

## Related Documents

- **components.md** - Detailed component specifications
- **component-methods.md** - Method signatures and interfaces
- **services.md** - Service layer design patterns
- **component-dependency.md** - Dependency analysis and data flow
- **requirements.md** - Functional and non-functional requirements
- **execution-plan.md** - Workflow planning and stage sequence

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial application design document |

