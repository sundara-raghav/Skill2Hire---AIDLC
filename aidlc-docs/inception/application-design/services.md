# Service Layer Design: Skill2Hire Application

## Overview
This document defines the service layer design using a **Partial Service Layer** approach - services are used only for complex workflows (prediction, analytics) while simpler operations access components directly.

---

## Service Layer Philosophy

### Partial Service Layer Rationale
Based on design decision (Question 12: Answer C), the application uses services selectively:

**Services ARE used for**:
- Complex orchestration (prediction workflow)
- Multi-component coordination (analytics aggregation)
- Transaction management
- Business logic that spans multiple components

**Services are NOT used for**:
- Simple CRUD operations
- Single-component operations
- Straightforward data retrieval
- Utility functions

---

## Service Catalog

### 1. PredictionService

**Purpose**: Orchestrate the complete placement prediction workflow

**Complexity Justification**: 
- Coordinates 5+ components (MLModelManager, NLPService, SkillGapAnalyzer, CacheManager, DataRepository)
- Implements caching strategy
- Handles transaction-like behavior (store input + prediction atomically)
- Manages error recovery across multiple steps

**Responsibilities**:
1. **Input Processing**: Receive and validate student profile and job description
2. **Cache Management**: Check cache before expensive operations
3. **NLP Coordination**: Trigger job description analysis
4. **ML Orchestration**: Coordinate ensemble model predictions
5. **Skill Gap Analysis**: Compare profile against job requirements
6. **Result Aggregation**: Combine all outputs into unified result
7. **Persistence**: Store inputs and predictions in database
8. **Error Handling**: Gracefully handle failures at any step

**Workflow**:
```
1. Calculate input hash for caching
2. Check cache for existing prediction
3. If cache miss:
   a. Analyze job description (NLPService)
   b. Transform student profile to features (FeatureEngineer)
   c. Generate predictions from all models (MLModelManager)
   d. Analyze skill gaps (SkillGapAnalyzer)
   e. Aggregate results
   f. Store in database (DataRepository)
   g. Cache result (CacheManager)
4. Return prediction result
```

**Dependencies**:
- `MLModelManager`: Model inference
- `NLPService`: Job description analysis
- `SkillGapAnalyzer`: Skill comparison
- `FeatureEngineer`: Feature transformation
- `CacheManager`: Result caching
- `DataRepository`: Data persistence
- `Logger`: Logging
- `ConfigManager`: Configuration

**Error Handling Strategy**:
- **ML Model Failure**: Return error, log details, suggest retry
- **NLP Failure**: Use fallback keyword extraction, log warning
- **Database Failure**: Return prediction without storing, log error
- **Cache Failure**: Continue without caching, log warning

**Performance Considerations**:
- Cache hit rate target: >60%
- Total workflow time: <5 seconds (per NFR-01)
- Parallel execution where possible (NLP + feature engineering)

---

### 2. AnalyticsService

**Purpose**: Orchestrate analytics and insights generation with hybrid computation strategy

**Complexity Justification**:
- Coordinates pre-computed and on-demand metrics
- Implements multi-level caching
- Handles complex aggregation queries
- Manages data freshness vs performance tradeoff

**Responsibilities**:
1. **Request Routing**: Determine if metrics are pre-computed or need calculation
2. **Cache Management**: Check cache before database queries
3. **Pre-computed Retrieval**: Fetch pre-computed metrics from database
4. **On-demand Calculation**: Execute aggregation queries when needed
5. **Result Formatting**: Format data for frontend consumption
6. **Cache Population**: Store results for future requests

**Workflow**:
```
1. Parse analytics filters (branch, date range)
2. Generate cache key
3. Check cache for insights
4. If cache miss:
   a. Check for pre-computed metrics in database
   b. If not available, calculate on-demand:
      - Department-wise placement rates
      - CGPA vs placement correlation
      - Top skills frequency
      - Overall statistics
   c. Format results
   d. Cache with appropriate TTL
5. Return analytics result
```

**Dependencies**:
- `DataRepository`: Database queries
- `CacheManager`: Result caching
- `Logger`: Logging
- `ConfigManager`: Configuration (TTL, cache settings)

**Hybrid Computation Strategy**:

| Metric | Computation Strategy | Rationale |
|--------|---------------------|-----------|
| Department placement rate | Pre-computed | Changes infrequently, expensive to calculate |
| CGPA correlation | Pre-computed | Statistical calculation, stable over time |
| Top 10 skills | Pre-computed | Aggregation over large dataset |
| Custom date range queries | On-demand | Too many combinations to pre-compute |
| Single department filter | On-demand | Fast query, specific to request |

**Caching Strategy**:
- Pre-computed metrics: TTL = 24 hours
- On-demand queries: TTL = 1 hour
- Cache invalidation: On new prediction stored

**Performance Considerations**:
- Pre-computed metrics updated daily (background job)
- On-demand queries optimized with database indexes
- Cache hit rate target: >80% for common queries

---

### 3. ResumeParsingService

**Purpose**: Extract structured data from uploaded resume files

**Complexity Justification**:
- Handles multiple file formats (PDF, DOCX)
- Implements complex text extraction and parsing logic
- Coordinates multiple extraction steps
- Manages parsing confidence scoring

**Responsibilities**:
1. **File Validation**: Check file type, size, format
2. **Text Extraction**: Extract text from PDF or DOCX
3. **Data Extraction**: Parse education, skills, experience
4. **Validation**: Validate extracted data against schema
5. **Confidence Scoring**: Calculate parsing confidence
6. **Error Handling**: Handle malformed or incomplete resumes

**Workflow**:
```
1. Validate file (type, size)
2. Extract text based on file type:
   - PDF: Use PyPDF2 or pdfplumber
   - DOCX: Use python-docx
3. Parse extracted text:
   a. Extract education (CGPA, branch)
   b. Extract skills (match against skill dictionary)
   c. Extract experience (projects, internships, certifications)
4. Validate extracted data
5. Calculate confidence score
6. Return ResumeData with warnings
```

**Dependencies**:
- `DataValidator`: Schema validation
- `SkillDictionary`: Skill matching
- `Logger`: Logging
- PDF/DOCX parsing libraries

**Parsing Strategies**:

| Section | Extraction Method | Confidence Factors |
|---------|------------------|-------------------|
| Education | Regex patterns for CGPA, degree | Format match, value range |
| Skills | Keyword matching against dictionary | Number of matches, context |
| Projects | Section headers, bullet points | Section found, count extracted |
| Internships | Keywords (intern, internship) | Keyword presence, duration |
| Certifications | Section headers, course names | Section found, count extracted |

**Error Handling**:
- **Unsupported format**: Return error with supported formats
- **Corrupted file**: Return error, log details
- **No data extracted**: Return empty result with low confidence
- **Partial extraction**: Return partial data with warnings

**Confidence Scoring**:
```
Confidence = (
    0.3 * education_confidence +
    0.3 * skills_confidence +
    0.2 * projects_confidence +
    0.1 * internship_confidence +
    0.1 * certifications_confidence
)
```

---

## Service Interaction Patterns

### Pattern 1: API → Service → Components (Complex Workflows)

**Used for**: Prediction, Analytics

```
API Blueprint
    ↓ (calls)
Service (orchestration)
    ↓ (coordinates)
Multiple Components
    ↓ (returns)
Service (aggregates)
    ↓ (returns)
API Blueprint (formats response)
```

**Example**: Prediction Request
```
PredictionBlueprint.predict()
    → PredictionService.predict_placement()
        → NLPService.analyze_job_description()
        → FeatureEngineer.transform()
        → MLModelManager.predict()
        → SkillGapAnalyzer.analyze_skill_gap()
        → DataRepository.store_prediction()
        → CacheManager.set()
    ← PredictionResult
← HTTP Response
```

---

### Pattern 2: API → Component (Simple Operations)

**Used for**: Job analysis, Resume upload (parsing only)

```
API Blueprint
    ↓ (calls directly)
Component
    ↓ (returns)
API Blueprint (formats response)
```

**Example**: Job Analysis Request
```
JobAnalysisBlueprint.analyze_job()
    → NLPService.analyze_job_description()
    ← JobAnalysisResult
← HTTP Response
```

---

## Service Communication

### Synchronous Communication
All services use **synchronous method calls** - no message queues or async processing in initial release.

**Rationale**:
- Simpler architecture
- Easier debugging and testing
- Meets performance requirements (<5 seconds)
- No complex workflows requiring async

**Future Consideration**: If resume parsing becomes slow (>5 seconds), consider async processing with job queue.

---

## Service Error Handling

### Error Propagation Strategy
Services use **middleware-based error handling** (per design decision):

1. **Service Level**: Catch expected errors, return error results
2. **Middleware Level**: Catch unexpected errors, format responses
3. **Global Handler**: Catch unhandled exceptions, log and return 500

**Service Error Handling Pattern**:
```python
def service_method():
    try:
        # Business logic
        result = perform_operation()
        return result
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        raise  # Let middleware handle
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise  # Let middleware handle
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise  # Let global handler catch
```

---

## Service Transaction Management

### Pseudo-Transactions
Services implement **pseudo-transaction** behavior for multi-step operations:

**PredictionService Example**:
```python
def predict_placement(self, profile, job_desc):
    input_id = None
    prediction_id = None
    
    try:
        # Step 1: Store input
        input_id = self.data_repository.store_user_input(profile)
        
        # Step 2: Generate prediction
        result = self._generate_prediction(profile, job_desc)
        
        # Step 3: Store prediction
        prediction_id = self.data_repository.store_prediction(result, input_id)
        
        # Step 4: Cache result
        self.cache_manager.set(input_hash, result)
        
        return result
        
    except Exception as e:
        # Rollback: Mark input as failed if prediction failed
        if input_id and not prediction_id:
            self.data_repository.mark_input_failed(input_id)
        raise
```

**Note**: Supabase doesn't support traditional transactions, so we use compensating actions.

---

## Service Testing Strategy

### Unit Testing
Each service should be unit tested with **mocked dependencies**:

```python
def test_prediction_service_cache_hit():
    # Arrange
    mock_cache = Mock(CacheManager)
    mock_cache.get.return_value = expected_result
    service = PredictionService(cache_manager=mock_cache, ...)
    
    # Act
    result = service.predict_placement(profile, job_desc)
    
    # Assert
    assert result == expected_result
    mock_cache.get.assert_called_once()
```

### Integration Testing
Services should be integration tested with **real components** but **test database**:

```python
def test_prediction_service_integration():
    # Arrange
    test_db = TestSupabaseClient()
    real_ml_manager = MLModelManager()
    service = PredictionService(data_repository=test_db, ml_manager=real_ml_manager, ...)
    
    # Act
    result = service.predict_placement(profile, job_desc)
    
    # Assert
    assert result.prediction_probability > 0
    assert test_db.has_prediction(result.prediction_id)
```

---

## Service Configuration

### Service Initialization
Services are initialized at application startup with **partial dependency injection**:

```python
# app.py
def create_app():
    app = Flask(__name__)
    
    # Initialize infrastructure
    config = ConfigManager()
    logger = Logger()
    cache = CacheManager()
    db = DataRepository(config.get('SUPABASE_URL'), config.get('SUPABASE_KEY'))
    
    # Initialize ML components
    ml_manager = MLModelManager()
    ml_manager.load_models(config.get('MODEL_DIR'))
    feature_engineer = FeatureEngineer()
    
    # Initialize business components
    skill_dict = SkillDictionary(config.get('SKILL_DICT_PATH'))
    nlp_service = NLPService(skill_dict, cache)
    skill_gap_analyzer = SkillGapAnalyzer(nlp_service)
    
    # Initialize services
    prediction_service = PredictionService(
        ml_manager=ml_manager,
        nlp_service=nlp_service,
        skill_gap_analyzer=skill_gap_analyzer,
        feature_engineer=feature_engineer,
        cache_manager=cache,
        data_repository=db,
        logger=logger
    )
    
    analytics_service = AnalyticsService(
        data_repository=db,
        cache_manager=cache,
        logger=logger
    )
    
    resume_service = ResumeParsingService(
        data_validator=DataValidator(),
        skill_dictionary=skill_dict,
        logger=logger
    )
    
    # Register blueprints with services
    app.register_blueprint(create_prediction_blueprint(prediction_service))
    app.register_blueprint(create_analytics_blueprint(analytics_service))
    app.register_blueprint(create_resume_blueprint(resume_service))
    
    return app
```

---

## Service Monitoring

### Metrics to Track
Each service should expose metrics for monitoring:

**PredictionService**:
- Prediction requests per minute
- Average prediction time
- Cache hit rate
- Model inference time
- Database write time
- Error rate by type

**AnalyticsService**:
- Insights requests per minute
- Cache hit rate
- Pre-computed vs on-demand ratio
- Query execution time
- Error rate

**ResumeParsingService**:
- Parse requests per minute
- Average parsing time by file type
- Parsing success rate
- Average confidence score
- Error rate by error type

### Logging
Services should log:
- **INFO**: Service method entry/exit, cache hits/misses
- **WARNING**: Fallback behavior, partial failures
- **ERROR**: Exceptions, database errors, external service failures

---

## Service Evolution

### Future Enhancements

**PredictionService**:
- Add A/B testing for model versions
- Implement prediction explanation (SHAP values)
- Add batch prediction endpoint

**AnalyticsService**:
- Add real-time streaming analytics
- Implement custom report generation
- Add predictive analytics (trend forecasting)

**ResumeParsingService**:
- Add async processing for large files
- Implement ML-based parsing (NER models)
- Add support for more file formats

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Next**: Define component dependencies and data flow
