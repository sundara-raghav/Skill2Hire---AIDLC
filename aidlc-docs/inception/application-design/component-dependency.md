# Component Dependencies: Skill2Hire Application

## Overview
This document maps component relationships, dependencies, and communication patterns for the Skill2Hire application.

---

## Dependency Matrix

### Legend
- ✅ **Direct Dependency**: Component directly instantiates or calls another component
- 🔗 **Indirect Dependency**: Component depends through service or intermediary
- ⚡ **Data Flow**: Data passes through component
- ❌ **No Dependency**: No relationship

---

## Component Dependency Table

| Component | ML Manager | NLP Service | Skill Gap | Feature Eng | Data Repo | Cache Mgr | Logger | Config Mgr |
|-----------|-----------|-------------|-----------|-------------|-----------|-----------|--------|------------|
| **PredictionBlueprint** | 🔗 | 🔗 | 🔗 | 🔗 | 🔗 | 🔗 | ✅ | ✅ |
| **AnalyticsBlueprint** | ❌ | ❌ | ❌ | ❌ | 🔗 | 🔗 | ✅ | ✅ |
| **ResumeBlueprint** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **JobAnalysisBlueprint** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **PredictionService** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AnalyticsService** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **ResumeParsingService** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **NLPService** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **SkillGapAnalyzer** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **MLModelManager** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **FeatureEngineer** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## Dependency Graph

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                                                              │
│                      FrontendApp (Browser)                   │
└──────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON
┌─────────────────────────┴───────────────────────────────────┐
│                        API LAYER                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Prediction   │  │ Analytics    │  │ Resume       │     │
│  │ Blueprint    │  │ Blueprint    │  │ Blueprint    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Job Analysis │  │ API          │                        │
│  │ Blueprint    │  │ Middleware   │                        │
│  └──────┬───────┘  └──────────────┘                        │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│                   BUSINESS LOGIC LAYER                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Prediction   │  │ Analytics    │  │ Resume       │     │
│  │ Service      │  │ Service      │  │ Parsing Svc  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐     │
│  │ NLP Service  │  │ Skill Gap    │  │ Data         │     │
│  │              │  │ Analyzer     │  │ Validator    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────┬──────────────────┬──────────────────┬─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│                    ML & DATA LAYERS                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ML Model     │  │ Feature      │  │ Data         │     │
│  │ Manager      │  │ Engineer     │  │ Repository   │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                              │              │
└──────────────────────────────────────────────┼──────────────┘
                                              │
                                    ┌─────────┴─────────┐
                                    │    SUPABASE       │
                                    │    DATABASE       │
                                    └───────────────────┘
```

---

## Detailed Component Dependencies

### 1. PredictionBlueprint Dependencies

**Direct Dependencies**:
- `PredictionService` - Orchestrates prediction workflow
- `DataValidator` - Validates request payload
- `Logger` - Logs requests and errors
- `ConfigManager` - Gets configuration

**Indirect Dependencies** (through PredictionService):
- `MLModelManager` - Model inference
- `NLPService` - Job analysis
- `SkillGapAnalyzer` - Skill comparison
- `FeatureEngineer` - Feature transformation
- `CacheManager` - Result caching
- `DataRepository` - Data persistence

**Communication Pattern**: Synchronous HTTP → Service call → Response

---

### 2. PredictionService Dependencies

**Direct Dependencies**:
- `MLModelManager` ✅ - Generate model predictions
- `NLPService` ✅ - Analyze job descriptions
- `SkillGapAnalyzer` ✅ - Compare skills
- `FeatureEngineer` ✅ - Transform features
- `CacheManager` ✅ - Cache results
- `DataRepository` ✅ - Store predictions
- `Logger` ✅ - Log operations
- `ConfigManager` ✅ - Get settings

**Dependency Injection**: Constructor injection (partial DI)

```python
def __init__(self,
             ml_manager: MLModelManager,
             nlp_service: NLPService,
             skill_gap_analyzer: SkillGapAnalyzer,
             feature_engineer: FeatureEngineer,
             cache_manager: CacheManager,
             data_repository: DataRepository,
             logger: Logger,
             config: ConfigManager):
    self.ml_manager = ml_manager
    self.nlp_service = nlp_service
    # ... etc
```

---

### 3. AnalyticsService Dependencies

**Direct Dependencies**:
- `DataRepository` ✅ - Query analytics data
- `CacheManager` ✅ - Cache insights
- `Logger` ✅ - Log operations
- `ConfigManager` ✅ - Get cache TTL settings

**No ML or NLP dependencies** - Pure data aggregation

---

### 4. NLPService Dependencies

**Direct Dependencies**:
- `SkillDictionary` ✅ - Match skills
- `CacheManager` ✅ - Cache analysis results
- `Logger` ✅ - Log operations
- `ConfigManager` ✅ - Get NLP settings

**External Libraries**:
- NLTK or spaCy for text processing

---

### 5. SkillGapAnalyzer Dependencies

**Direct Dependencies**:
- `NLPService` ✅ - Get job skills
- `Logger` ✅ - Log operations

**Note**: Lightweight component with minimal dependencies

---

### 6. MLModelManager Dependencies

**Direct Dependencies**:
- `Logger` ✅ - Log model operations
- `ConfigManager` ✅ - Get model paths

**External Libraries**:
- scikit-learn for models
- pickle for serialization

**Singleton Pattern**: No external dependencies injected

---

### 7. DataRepository Dependencies

**Direct Dependencies**:
- `Logger` ✅ - Log database operations
- `ConfigManager` ✅ - Get Supabase credentials

**External Libraries**:
- Supabase Python client

---

## Data Flow Diagrams

### Prediction Request Flow

```
User Input (Frontend)
    │
    ↓ POST /api/predict
PredictionBlueprint
    │
    ├─→ DataValidator.validate_student_profile()
    │       └─→ ValidationResult
    │
    ↓ prediction_service.predict_placement()
PredictionService
    │
    ├─→ _calculate_input_hash()
    │       └─→ hash_string
    │
    ├─→ cache_manager.get(hash)
    │       └─→ None (cache miss)
    │
    ├─→ nlp_service.analyze_job_description()
    │       ├─→ _preprocess_text()
    │       ├─→ _extract_keywords()
    │       ├─→ skill_dictionary.match_skill()
    │       └─→ JobAnalysisResult
    │
    ├─→ feature_engineer.transform()
    │       ├─→ encode_categorical()
    │       ├─→ scale_numerical()
    │       └─→ feature_array
    │
    ├─→ ml_manager.predict()
    │       ├─→ predict_random_forest()
    │       ├─→ predict_gradient_boosting()
    │       ├─→ predict_logistic_regression()
    │       ├─→ predict_ensemble()
    │       └─→ ModelPredictions
    │
    ├─→ skill_gap_analyzer.analyze_skill_gap()
    │       ├─→ _identify_missing_skills()
    │       ├─→ _generate_suggestions()
    │       └─→ suggestions[]
    │
    ├─→ data_repository.store_user_input()
    │       └─→ input_id
    │
    ├─→ data_repository.store_prediction()
    │       └─→ prediction_id
    │
    ├─→ cache_manager.set(hash, result)
    │
    └─→ PredictionResult
            │
            ↓ JSON Response
        Frontend Display
```

---

### Analytics Request Flow

```
User Request (Frontend)
    │
    ↓ GET /api/insights?branch=CS
AnalyticsBlueprint
    │
    ↓ analytics_service.get_insights()
AnalyticsService
    │
    ├─→ _generate_cache_key(filters)
    │       └─→ cache_key
    │
    ├─→ cache_manager.get(cache_key)
    │       └─→ None (cache miss)
    │
    ├─→ data_repository.get_precomputed_insights()
    │       └─→ precomputed_data (partial)
    │
    ├─→ data_repository.get_department_stats(filters)
    │       └─→ department_stats[]
    │
    ├─→ data_repository.get_cgpa_correlation(filters)
    │       └─→ cgpa_data[]
    │
    ├─→ data_repository.get_top_skills(filters)
    │       └─→ skills[]
    │
    ├─→ _format_results()
    │       └─→ AnalyticsResult
    │
    ├─→ cache_manager.set(cache_key, result, ttl=3600)
    │
    └─→ AnalyticsResult
            │
            ↓ JSON Response
        Frontend Dashboard
```

---

### Resume Upload Flow

```
User Upload (Frontend)
    │
    ↓ POST /api/resume/upload (multipart/form-data)
ResumeBlueprint
    │
    ├─→ data_validator.validate_resume_file()
    │       └─→ ValidationResult
    │
    ↓ resume_service.parse_resume()
ResumeParsingService
    │
    ├─→ _parse_pdf() or _parse_docx()
    │       └─→ raw_text
    │
    ├─→ _extract_education(text)
    │       └─→ {cgpa, branch}
    │
    ├─→ _extract_skills(text)
    │       ├─→ skill_dictionary.match_skill()
    │       └─→ skills[]
    │
    ├─→ _extract_experience(text)
    │       └─→ {projects, internships, certs}
    │
    ├─→ data_validator.validate_student_profile()
    │       └─→ ValidationResult
    │
    ├─→ _calculate_confidence()
    │       └─→ confidence_score
    │
    └─→ ResumeData
            │
            ↓ JSON Response
        Frontend Form Population
```

---

## Communication Patterns

### Pattern 1: Synchronous Method Calls
**Used by**: All components

```python
# Caller
result = component.method(args)

# Callee
def method(args):
    # Process
    return result
```

**Characteristics**:
- Blocking calls
- Direct return values
- Exception propagation
- Simple error handling

---

### Pattern 2: Dependency Injection (Partial)
**Used by**: Services, key components

```python
# Initialization (app.py)
service = PredictionService(
    ml_manager=ml_manager,
    nlp_service=nlp_service,
    # ... other dependencies
)

# Usage
class PredictionService:
    def __init__(self, ml_manager, nlp_service, ...):
        self.ml_manager = ml_manager
        self.nlp_service = nlp_service
```

**Benefits**:
- Testability (mock dependencies)
- Flexibility (swap implementations)
- Clear dependencies

---

### Pattern 3: Singleton Access
**Used by**: MLModelManager, Logger

```python
# Access singleton
ml_manager = MLModelManager()  # Returns same instance
logger = Logger()  # Returns same instance

# Usage
ml_manager.predict(features)
logger.info("Message")
```

**Characteristics**:
- Global state
- Single initialization
- Thread-safe access

---

## Circular Dependency Prevention

### Potential Circular Dependencies

**Avoided**: NLPService ↔ SkillGapAnalyzer
- **Solution**: SkillGapAnalyzer depends on NLPService (one direction only)
- SkillGapAnalyzer calls NLPService for job analysis
- NLPService never calls SkillGapAnalyzer

**Avoided**: PredictionService ↔ CacheManager
- **Solution**: PredictionService depends on CacheManager (one direction only)
- CacheManager is pure infrastructure, no business logic dependencies

**Avoided**: DataRepository ↔ Services
- **Solution**: Services depend on DataRepository (one direction only)
- DataRepository never calls services

---

## Dependency Injection Strategy

### Components with DI (Partial DI)
- `PredictionService` - Full constructor injection
- `AnalyticsService` - Full constructor injection
- `ResumeParsingService` - Partial constructor injection
- `NLPService` - Partial constructor injection
- `SkillGapAnalyzer` - Partial constructor injection

### Components without DI (Direct Instantiation)
- `MLModelManager` - Singleton, no injection needed
- `Logger` - Singleton, no injection needed
- `CacheManager` - Simple infrastructure, no injection needed
- `ConfigManager` - Singleton, no injection needed
- `DataRepository` - Initialized with config, no complex dependencies

### Rationale for Partial DI
- **Full DI overhead not justified** for simple components
- **Testability achieved** where it matters (services, complex logic)
- **Simplicity maintained** for infrastructure components
- **Flexibility preserved** for future changes

---

## Component Coupling Analysis

### Tight Coupling (Acceptable)
- `PredictionService` → `MLModelManager` - Core business logic
- `PredictionService` → `NLPService` - Core business logic
- `SkillGapAnalyzer` → `NLPService` - Functional requirement

### Loose Coupling (Desired)
- All Blueprints → Services - Interface-based
- Services → DataRepository - Interface-based
- Services → CacheManager - Infrastructure abstraction

### No Coupling (Independent)
- `MLModelManager` ↔ `NLPService` - Independent domains
- `AnalyticsService` ↔ `MLModelManager` - No interaction
- `ResumeParsingService` ↔ `MLModelManager` - No interaction

---

## Testing Implications

### Unit Testing Strategy

**Highly Testable** (with mocks):
- `PredictionService` - Mock all dependencies
- `AnalyticsService` - Mock DataRepository, CacheManager
- `SkillGapAnalyzer` - Mock NLPService

**Moderately Testable**:
- `NLPService` - Mock SkillDictionary, CacheManager
- `ResumeParsingService` - Mock DataValidator

**Integration Testing Required**:
- `MLModelManager` - Needs real models
- `DataRepository` - Needs test database
- `FeatureEngineer` - Needs real transformations

---

## Dependency Initialization Order

### Application Startup Sequence

```
1. ConfigManager (load config)
2. Logger (initialize logging)
3. CacheManager (initialize cache)
4. DataRepository (connect to Supabase)
5. SkillDictionary (load skill data)
6. MLModelManager (load models - SLOW)
7. FeatureEngineer (initialize transformers)
8. NLPService (initialize NLP tools)
9. SkillGapAnalyzer (depends on NLPService)
10. DataValidator (initialize schemas)
11. PredictionService (depends on all above)
12. AnalyticsService (depends on DataRepository, Cache)
13. ResumeParsingService (depends on DataValidator)
14. API Blueprints (depends on services)
15. Flask App (register blueprints, middleware)
```

**Critical Path**: MLModelManager loading (can take 5-10 seconds)

**Optimization**: Load models in background thread, return 503 until ready

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Next**: Consolidate into application-design.md
