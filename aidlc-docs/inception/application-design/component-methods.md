# Component Methods: Skill2Hire Application

## Overview
This document defines method signatures and interfaces for all components. Detailed business logic and algorithms will be specified in Functional Design (CONSTRUCTION phase).

---

## 1. Presentation Layer

### 1.1 FrontendApp (JavaScript)

```javascript
class FrontendApp {
    // Initialization
    init(): void
    
    // Form handling
    handleFormSubmit(event: Event): Promise<void>
    validateFormInputs(formData: FormData): ValidationResult
    
    // Prediction display
    displayPredictionResults(results: PredictionResponse): void
    renderModelComparison(modelResults: ModelResults): void
    renderSkillGapSuggestions(suggestions: string[]): void
    
    // Analytics dashboard
    loadInsightsDashboard(): Promise<void>
    renderDepartmentChart(data: DepartmentStats[]): void
    renderCGPACorrelation(data: CGPAStats[]): void
    renderTopSkills(skills: SkillFrequency[]): void
    
    // Resume upload
    handleResumeUpload(file: File): Promise<void>
    populateFormFromResume(extractedData: ResumeData): void
    
    // Real-time suggestions
    handleInputChange(fieldName: string, value: any): void
    showSuggestions(suggestions: string[]): void
    
    // Error handling
    displayError(message: string): void
    clearError(): void
    
    // Loading states
    showLoading(): void
    hideLoading(): void
}
```

---

## 2. API Layer

### 2.1 PredictionBlueprint (Flask)

```python
class PredictionBlueprint:
    """Flask blueprint for prediction endpoints"""
    
    def predict() -> Response:
        """
        POST /api/predict
        Generate placement prediction
        
        Request Body:
            {
                "name": str (optional),
                "cgpa": float,
                "aptitude_score": float,
                "programming_skills": int,
                "communication_skills": int,
                "num_projects": int,
                "internship_experience": bool,
                "certifications_count": int,
                "branch": str,
                "job_description": str
            }
        
        Returns:
            {
                "prediction_probability": float,
                "confidence_score": float,
                "model_results": {
                    "random_forest": float,
                    "gradient_boosting": float,
                    "logistic_regression": float,
                    "ensemble": float
                },
                "skill_gap_suggestions": list[str],
                "prediction_id": str
            }
        """
        pass
```

---

### 2.2 AnalyticsBlueprint (Flask)

```python
class AnalyticsBlueprint:
    """Flask blueprint for analytics endpoints"""
    
    def get_insights() -> Response:
        """
        GET /api/insights?branch=<branch>&start_date=<date>&end_date=<date>
        Retrieve college-wide analytics
        
        Query Parameters:
            branch: str (optional) - Filter by department
            start_date: str (optional) - ISO date
            end_date: str (optional) - ISO date
        
        Returns:
            {
                "department_stats": list[DepartmentStat],
                "cgpa_correlation": list[CGPAStat],
                "top_skills": list[SkillFrequency],
                "overall_placement_rate": float,
                "total_students": int
            }
        """
        pass
```

---

### 2.3 ResumeBlueprint (Flask)

```python
class ResumeBlueprint:
    """Flask blueprint for resume processing endpoints"""
    
    def upload_resume() -> Response:
        """
        POST /api/resume/upload
        Upload and parse resume file
        
        Request: multipart/form-data with 'file' field
        
        Returns:
            {
                "extracted_data": {
                    "cgpa": float,
                    "branch": str,
                    "skills": list[str],
                    "num_projects": int,
                    "internship_experience": bool,
                    "certifications_count": int
                },
                "parsing_confidence": float,
                "warnings": list[str]
            }
        """
        pass
```

---

### 2.4 JobAnalysisBlueprint (Flask)

```python
class JobAnalysisBlueprint:
    """Flask blueprint for job description analysis"""
    
    def analyze_job() -> Response:
        """
        POST /api/analyze-job
        Analyze job description for skills
        
        Request Body:
            {
                "job_description": str
            }
        
        Returns:
            {
                "extracted_skills": list[str],
                "skill_categories": dict[str, list[str]],
                "keywords": list[str],
                "required_experience": str (optional)
            }
        """
        pass
```

---

### 2.5 APIMiddleware (Flask)

```python
class APIMiddleware:
    """Middleware for cross-cutting API concerns"""
    
    def apply_security_headers(response: Response) -> Response:
        """Add security headers to response"""
        pass
    
    def apply_rate_limiting(request: Request) -> Optional[Response]:
        """Check rate limits, return 429 if exceeded"""
        pass
    
    def handle_cors(request: Request, response: Response) -> Response:
        """Apply CORS headers"""
        pass
    
    def generate_request_id() -> str:
        """Generate unique request ID"""
        pass
    
    def log_request(request: Request, request_id: str) -> None:
        """Log incoming request"""
        pass
    
    def log_response(response: Response, request_id: str, duration_ms: float) -> None:
        """Log outgoing response"""
        pass
```

---

## 3. Business Logic Layer

### 3.1 PredictionService

```python
class PredictionService:
    """Orchestrate placement prediction workflow"""
    
    def __init__(self, 
                 ml_manager: MLModelManager,
                 nlp_service: NLPService,
                 skill_gap_analyzer: SkillGapAnalyzer,
                 cache_manager: CacheManager,
                 data_repository: DataRepository):
        pass
    
    def predict_placement(self, student_profile: StudentProfile, 
                         job_description: str) -> PredictionResult:
        """
        Generate placement prediction with skill gap analysis
        
        Args:
            student_profile: Student data (CGPA, skills, etc.)
            job_description: Job posting text
        
        Returns:
            PredictionResult with probability, confidence, model breakdown, suggestions
        """
        pass
    
    def _get_cached_prediction(self, input_hash: str) -> Optional[PredictionResult]:
        """Check cache for existing prediction"""
        pass
    
    def _cache_prediction(self, input_hash: str, result: PredictionResult) -> None:
        """Store prediction in cache"""
        pass
    
    def _store_prediction(self, student_profile: StudentProfile, 
                         result: PredictionResult) -> str:
        """Store prediction in database, return prediction ID"""
        pass
    
    def _calculate_input_hash(self, student_profile: StudentProfile, 
                             job_description: str) -> str:
        """Generate hash for caching"""
        pass
```

---

### 3.2 AnalyticsService

```python
class AnalyticsService:
    """Orchestrate analytics and insights generation"""
    
    def __init__(self, 
                 data_repository: DataRepository,
                 cache_manager: CacheManager):
        pass
    
    def get_insights(self, filters: AnalyticsFilters) -> AnalyticsResult:
        """
        Retrieve analytics data with optional filtering
        
        Args:
            filters: Branch, date range filters
        
        Returns:
            AnalyticsResult with department stats, correlations, top skills
        """
        pass
    
    def _get_precomputed_metrics(self, filters: AnalyticsFilters) -> Optional[dict]:
        """Retrieve pre-computed metrics from database"""
        pass
    
    def _calculate_on_demand(self, filters: AnalyticsFilters) -> dict:
        """Calculate metrics on-demand when not pre-computed"""
        pass
    
    def _get_cached_insights(self, cache_key: str) -> Optional[AnalyticsResult]:
        """Check cache for insights"""
        pass
    
    def _cache_insights(self, cache_key: str, result: AnalyticsResult, ttl: int) -> None:
        """Store insights in cache with TTL"""
        pass
```

---

### 3.3 ResumeParsingService

```python
class ResumeParsingService:
    """Extract structured data from resume files"""
    
    def __init__(self, data_validator: DataValidator):
        pass
    
    def parse_resume(self, file_path: str, file_type: str) -> ResumeData:
        """
        Parse resume and extract profile data
        
        Args:
            file_path: Path to uploaded file
            file_type: 'pdf' or 'docx'
        
        Returns:
            ResumeData with extracted fields and confidence scores
        """
        pass
    
    def _parse_pdf(self, file_path: str) -> dict:
        """Extract text and structure from PDF"""
        pass
    
    def _parse_docx(self, file_path: str) -> dict:
        """Extract text and structure from DOCX"""
        pass
    
    def _extract_education(self, text: str) -> dict:
        """Extract CGPA and branch from text"""
        pass
    
    def _extract_skills(self, text: str) -> list[str]:
        """Extract technical skills from text"""
        pass
    
    def _extract_experience(self, text: str) -> dict:
        """Extract projects, internships, certifications"""
        pass
    
    def _calculate_confidence(self, extracted_data: dict) -> float:
        """Calculate parsing confidence score"""
        pass
```

---

### 3.4 NLPService

```python
class NLPService:
    """Natural language processing for job descriptions"""
    
    def __init__(self, 
                 skill_dictionary: SkillDictionary,
                 cache_manager: CacheManager):
        pass
    
    def analyze_job_description(self, job_description: str) -> JobAnalysisResult:
        """
        Extract skills and keywords from job description
        
        Args:
            job_description: Job posting text
        
        Returns:
            JobAnalysisResult with skills, categories, keywords
        """
        pass
    
    def _preprocess_text(self, text: str) -> list[str]:
        """Tokenize, remove stopwords, lowercase"""
        pass
    
    def _extract_keywords(self, tokens: list[str]) -> list[str]:
        """Extract important keywords"""
        pass
    
    def _match_skills(self, tokens: list[str]) -> list[str]:
        """Match tokens against skill dictionary"""
        pass
    
    def _categorize_skills(self, skills: list[str]) -> dict[str, list[str]]:
        """Categorize skills (programming, tools, soft skills)"""
        pass
    
    def _get_cached_analysis(self, job_hash: str) -> Optional[JobAnalysisResult]:
        """Check cache for analysis"""
        pass
    
    def _cache_analysis(self, job_hash: str, result: JobAnalysisResult) -> None:
        """Store analysis in cache"""
        pass
```

---

### 3.5 SkillGapAnalyzer

```python
class SkillGapAnalyzer:
    """Compare student profile against job requirements"""
    
    def __init__(self, nlp_service: NLPService):
        pass
    
    def analyze_skill_gap(self, student_profile: StudentProfile, 
                         job_skills: list[str]) -> list[str]:
        """
        Identify missing skills and generate suggestions
        
        Args:
            student_profile: Student data with skills
            job_skills: Skills extracted from job description
        
        Returns:
            List of actionable improvement suggestions
        """
        pass
    
    def _extract_student_skills(self, profile: StudentProfile) -> list[str]:
        """Extract skills from student profile"""
        pass
    
    def _identify_missing_skills(self, student_skills: list[str], 
                                job_skills: list[str]) -> list[str]:
        """Find skills in job but not in student profile"""
        pass
    
    def _prioritize_skills(self, missing_skills: list[str]) -> list[str]:
        """Prioritize skills by importance"""
        pass
    
    def _generate_suggestions(self, missing_skills: list[str], 
                            profile: StudentProfile) -> list[str]:
        """Generate actionable improvement suggestions"""
        pass
```

---

### 3.6 DataValidator

```python
class DataValidator:
    """Schema-based validation for all inputs"""
    
    def validate_student_profile(self, data: dict) -> ValidationResult:
        """Validate student profile data"""
        pass
    
    def validate_job_description(self, data: dict) -> ValidationResult:
        """Validate job description input"""
        pass
    
    def validate_resume_file(self, file: FileStorage) -> ValidationResult:
        """Validate resume file upload"""
        pass
    
    def sanitize_input(self, value: str) -> str:
        """Sanitize string input to prevent injection"""
        pass
    
    def _check_required_fields(self, data: dict, required: list[str]) -> list[str]:
        """Check for missing required fields"""
        pass
    
    def _validate_types(self, data: dict, schema: dict) -> list[str]:
        """Validate data types match schema"""
        pass
    
    def _validate_ranges(self, data: dict, constraints: dict) -> list[str]:
        """Validate numeric values within ranges"""
        pass
```

---

## 4. ML Layer

### 4.1 MLModelManager

```python
class MLModelManager:
    """Singleton for managing ML models"""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance"""
        pass
    
    def __init__(self):
        """Load models at startup"""
        pass
    
    def load_models(self, model_dir: str) -> None:
        """Load all ensemble models from disk"""
        pass
    
    def predict(self, features: np.ndarray) -> ModelPredictions:
        """
        Generate predictions from all models
        
        Args:
            features: Preprocessed feature array
        
        Returns:
            ModelPredictions with individual and ensemble results
        """
        pass
    
    def predict_random_forest(self, features: np.ndarray) -> float:
        """Get Random Forest prediction"""
        pass
    
    def predict_gradient_boosting(self, features: np.ndarray) -> float:
        """Get Gradient Boosting prediction"""
        pass
    
    def predict_logistic_regression(self, features: np.ndarray) -> float:
        """Get Logistic Regression prediction"""
        pass
    
    def predict_ensemble(self, features: np.ndarray) -> float:
        """Get Voting Classifier prediction"""
        pass
    
    def calculate_confidence(self, predictions: ModelPredictions) -> float:
        """Calculate confidence score from model agreement"""
        pass
    
    def get_model_info(self) -> dict:
        """Return model metadata (versions, accuracy, etc.)"""
        pass
```

---

### 4.2 FeatureEngineer

```python
class FeatureEngineer:
    """Transform raw inputs into model-ready features"""
    
    def __init__(self):
        """Initialize encoders and scalers"""
        pass
    
    def transform(self, student_profile: StudentProfile) -> np.ndarray:
        """
        Transform student profile to feature array
        
        Args:
            student_profile: Raw student data
        
        Returns:
            Numpy array ready for model input
        """
        pass
    
    def encode_categorical(self, branch: str) -> np.ndarray:
        """Encode branch/department as one-hot or label"""
        pass
    
    def scale_numerical(self, values: dict) -> np.ndarray:
        """Scale CGPA, aptitude, skills to standard range"""
        pass
    
    def handle_missing(self, features: np.ndarray) -> np.ndarray:
        """Handle missing values with imputation"""
        pass
    
    def validate_features(self, features: np.ndarray) -> bool:
        """Validate feature array shape and ranges"""
        pass
```

---

## 5. Data Access Layer

### 5.1 DataRepository

```python
class DataRepository:
    """Direct Supabase client for database operations"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        pass
    
    # User inputs
    def store_user_input(self, profile: StudentProfile) -> str:
        """Store student profile, return input_id"""
        pass
    
    def get_user_input(self, input_id: str) -> Optional[StudentProfile]:
        """Retrieve student profile by ID"""
        pass
    
    # Predictions
    def store_prediction(self, prediction: PredictionResult, input_id: str) -> str:
        """Store prediction result, return prediction_id"""
        pass
    
    def get_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """Retrieve prediction by ID"""
        pass
    
    def get_predictions_by_branch(self, branch: str, limit: int) -> list[PredictionResult]:
        """Get recent predictions for a branch"""
        pass
    
    # Job descriptions
    def store_job_description(self, job_desc: str, analysis: JobAnalysisResult) -> str:
        """Store job description and analysis, return job_id"""
        pass
    
    def get_job_description(self, job_id: str) -> Optional[dict]:
        """Retrieve job description by ID"""
        pass
    
    # Analytics
    def get_department_stats(self, filters: AnalyticsFilters) -> list[dict]:
        """Query department-wise placement statistics"""
        pass
    
    def get_cgpa_correlation(self, filters: AnalyticsFilters) -> list[dict]:
        """Query CGPA vs placement correlation"""
        pass
    
    def get_top_skills(self, filters: AnalyticsFilters, limit: int) -> list[dict]:
        """Query most frequent skills in placements"""
        pass
    
    def store_precomputed_insights(self, insights: dict) -> None:
        """Store pre-computed analytics metrics"""
        pass
    
    def get_precomputed_insights(self, metric_name: str) -> Optional[dict]:
        """Retrieve pre-computed metrics"""
        pass
    
    # Utility
    def execute_query(self, table: str, query: dict) -> list[dict]:
        """Execute generic Supabase query"""
        pass
    
    def handle_error(self, error: Exception) -> None:
        """Handle database errors with retry logic"""
        pass
```

---

## 6. Infrastructure Layer

### 6.1 CacheManager

```python
class CacheManager:
    """Result caching based on input hash"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """Initialize cache with size limit and TTL"""
        pass
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        pass
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL"""
        pass
    
    def delete(self, key: str) -> None:
        """Remove value from cache"""
        pass
    
    def clear(self) -> None:
        """Clear all cache entries"""
        pass
    
    def get_stats(self) -> dict:
        """Return cache statistics (hits, misses, size)"""
        pass
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        pass
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired"""
        pass
```

---

### 6.2 Logger

```python
class Logger:
    """Centralized logging for all components"""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance"""
        pass
    
    def __init__(self):
        """Configure logger"""
        pass
    
    def info(self, message: str, **context) -> None:
        """Log info level message"""
        pass
    
    def warning(self, message: str, **context) -> None:
        """Log warning level message"""
        pass
    
    def error(self, message: str, error: Optional[Exception] = None, **context) -> None:
        """Log error level message"""
        pass
    
    def debug(self, message: str, **context) -> None:
        """Log debug level message"""
        pass
    
    def _format_log(self, level: str, message: str, context: dict) -> str:
        """Format log entry with timestamp, request ID, level"""
        pass
    
    def _sanitize_context(self, context: dict) -> dict:
        """Remove sensitive data from context"""
        pass
```

---

### 6.3 ConfigManager

```python
class ConfigManager:
    """Hybrid configuration management"""
    
    def __init__(self, config_file: str = "config.py"):
        """Load config from file and environment"""
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    def get_required(self, key: str) -> Any:
        """Get required config value, raise if missing"""
        pass
    
    def _load_from_file(self, config_file: str) -> dict:
        """Load default config from file"""
        pass
    
    def _load_from_env(self) -> dict:
        """Load overrides from environment variables"""
        pass
    
    def _merge_configs(self, file_config: dict, env_config: dict) -> dict:
        """Merge configs with env taking precedence"""
        pass
    
    def validate(self) -> None:
        """Validate required configuration at startup"""
        pass
```

---

### 6.4 SecurityHeadersMiddleware

```python
class SecurityHeadersMiddleware:
    """Apply HTTP security headers"""
    
    def __init__(self, app: Flask):
        """Register middleware with Flask app"""
        pass
    
    def apply_headers(self, response: Response) -> Response:
        """Add all security headers to response"""
        pass
    
    def _set_csp(self, response: Response) -> None:
        """Set Content-Security-Policy header"""
        pass
    
    def _set_hsts(self, response: Response) -> None:
        """Set Strict-Transport-Security header"""
        pass
    
    def _set_content_type_options(self, response: Response) -> None:
        """Set X-Content-Type-Options header"""
        pass
    
    def _set_frame_options(self, response: Response) -> None:
        """Set X-Frame-Options header"""
        pass
    
    def _set_referrer_policy(self, response: Response) -> None:
        """Set Referrer-Policy header"""
        pass
```

---

## 7. Utility Components

### 7.1 SkillDictionary

```python
class SkillDictionary:
    """Maintain predefined list of skills"""
    
    def __init__(self, data_source: str):
        """Load skill dictionary from JSON or database"""
        pass
    
    def get_all_skills(self) -> list[str]:
        """Return all skills in dictionary"""
        pass
    
    def get_skills_by_category(self, category: str) -> list[str]:
        """Return skills in specific category"""
        pass
    
    def match_skill(self, token: str) -> Optional[str]:
        """Match token to skill (handles synonyms)"""
        pass
    
    def add_skill(self, skill: str, category: str, synonyms: list[str]) -> None:
        """Add new skill to dictionary"""
        pass
    
    def get_categories(self) -> list[str]:
        """Return all skill categories"""
        pass
```

---

### 7.2 ErrorHandler

```python
class ErrorHandler:
    """Global error handling for Flask"""
    
    def __init__(self, app: Flask, logger: Logger):
        """Register error handlers with Flask app"""
        pass
    
    def handle_validation_error(self, error: ValidationError) -> Response:
        """Handle validation errors (400)"""
        pass
    
    def handle_not_found(self, error: NotFound) -> Response:
        """Handle 404 errors"""
        pass
    
    def handle_rate_limit_exceeded(self, error: RateLimitExceeded) -> Response:
        """Handle rate limit errors (429)"""
        pass
    
    def handle_internal_error(self, error: Exception) -> Response:
        """Handle unhandled exceptions (500)"""
        pass
    
    def _format_error_response(self, status_code: int, message: str, 
                              details: Optional[dict] = None) -> dict:
        """Format consistent error response"""
        pass
    
    def _log_error(self, error: Exception, request: Request) -> None:
        """Log error with full context"""
        pass
```

---

## Data Transfer Objects (DTOs)

### StudentProfile
```python
@dataclass
class StudentProfile:
    name: Optional[str]
    cgpa: float
    aptitude_score: float
    programming_skills: int
    communication_skills: int
    num_projects: int
    internship_experience: bool
    certifications_count: int
    branch: str
```

### PredictionResult
```python
@dataclass
class PredictionResult:
    prediction_probability: float
    confidence_score: float
    model_results: ModelPredictions
    skill_gap_suggestions: list[str]
    prediction_id: str
    timestamp: datetime
```

### ModelPredictions
```python
@dataclass
class ModelPredictions:
    random_forest: float
    gradient_boosting: float
    logistic_regression: float
    ensemble: float
```

### JobAnalysisResult
```python
@dataclass
class JobAnalysisResult:
    extracted_skills: list[str]
    skill_categories: dict[str, list[str]]
    keywords: list[str]
    required_experience: Optional[str]
```

### ResumeData
```python
@dataclass
class ResumeData:
    cgpa: Optional[float]
    branch: Optional[str]
    skills: list[str]
    num_projects: int
    internship_experience: bool
    certifications_count: int
    parsing_confidence: float
    warnings: list[str]
```

### ValidationResult
```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
```

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Next**: Define services and orchestration patterns

