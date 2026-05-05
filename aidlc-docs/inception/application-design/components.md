# Component Definitions: Skill2Hire Application

## Overview
This document defines all components in the Skill2Hire application, organized using a hybrid layered/feature-based architecture.

---

## Architecture Organization

The application follows a **Hybrid Architecture**:
- **Layered structure** for cross-cutting concerns (API, Data Access, Infrastructure)
- **Feature-based modules** for business capabilities (Prediction, Analytics, Resume)

---

## Component Catalog

### 1. Presentation Layer Components

#### 1.1 Frontend Application
**Component Name**: `FrontendApp`

**Purpose**: Single-page web application providing user interface for all features

**Responsibilities**:
- Render input forms for student profile data
- Display prediction results with visualizations
- Show college-wide insights dashboard
- Handle resume file uploads
- Provide real-time suggestions as user types
- Manage client-side state and UI interactions

**Technology**: HTML5, CSS3, JavaScript (ES6+), Chart.js

**Interface**: Browser-based web interface

---

### 2. API Layer Components

#### 2.1 Prediction API Blueprint
**Component Name**: `PredictionBlueprint`

**Purpose**: Handle prediction-related API endpoints

**Responsibilities**:
- Accept student profile and job description inputs
- Validate request data using schema validation
- Coordinate with prediction service
- Return prediction results with model breakdown
- Apply rate limiting
- Handle prediction-specific errors

**Endpoints**:
- `POST /api/predict` - Generate placement prediction

**Technology**: Flask Blueprint

---

#### 2.2 Analytics API Blueprint
**Component Name**: `AnalyticsBlueprint`

**Purpose**: Handle analytics and insights API endpoints

**Responsibilities**:
- Serve college-wide placement statistics
- Provide department-wise insights
- Return skill trends and patterns
- Support filtering by department and date range
- Apply rate limiting

**Endpoints**:
- `GET /api/insights` - Retrieve analytics data

**Technology**: Flask Blueprint

---

#### 2.3 Resume API Blueprint
**Component Name**: `ResumeBlueprint`

**Purpose**: Handle resume upload and parsing endpoints

**Responsibilities**:
- Accept resume file uploads (PDF, DOCX)
- Validate file type and size
- Coordinate with resume parsing service
- Return extracted profile data
- Handle file processing errors
- Apply rate limiting

**Endpoints**:
- `POST /api/resume/upload` - Upload and parse resume
- `POST /api/resume/parse` - Parse uploaded resume

**Technology**: Flask Blueprint

---

#### 2.4 Job Analysis API Blueprint
**Component Name**: `JobAnalysisBlueprint`

**Purpose**: Handle job description analysis endpoints

**Responsibilities**:
- Accept job description text
- Coordinate with NLP service
- Return extracted skills and keywords
- Apply rate limiting

**Endpoints**:
- `POST /api/analyze-job` - Analyze job description

**Technology**: Flask Blueprint

---

#### 2.5 API Middleware
**Component Name**: `APIMiddleware`

**Purpose**: Cross-cutting concerns for all API requests

**Responsibilities**:
- Apply security headers (CSP, HSTS, X-Content-Type-Options, etc.)
- Enforce rate limiting across all endpoints
- Handle CORS configuration
- Global error handling and formatting
- Request/response logging
- Request ID generation and propagation

**Technology**: Flask middleware, Flask-Limiter, Flask-CORS

---

### 3. Business Logic Layer Components

#### 3.1 Prediction Service
**Component Name**: `PredictionService`

**Purpose**: Orchestrate placement prediction workflow

**Responsibilities**:
- Coordinate ML model inference
- Aggregate ensemble model results
- Calculate confidence scores
- Perform skill gap analysis
- Cache prediction results
- Store predictions in database
- Handle prediction errors gracefully

**Dependencies**: MLModelManager, NLPService, SkillGapAnalyzer, CacheManager, DataRepository

---

#### 3.2 Analytics Service
**Component Name**: `AnalyticsService`

**Purpose**: Orchestrate analytics and insights generation

**Responsibilities**:
- Retrieve pre-computed metrics from database
- Calculate on-demand aggregations when needed
- Generate department-wise statistics
- Compute CGPA vs placement correlations
- Identify top skills from historical data
- Cache frequently requested insights

**Dependencies**: DataRepository, CacheManager

---

#### 3.3 Resume Parsing Service
**Component Name**: `ResumeParsingService`

**Purpose**: Extract structured data from resume files

**Responsibilities**:
- Parse PDF and DOCX resume files
- Extract education details (CGPA, branch)
- Identify skills and technologies
- Count projects and certifications
- Detect internship experience
- Map extracted data to student profile schema
- Handle parsing errors and incomplete data

**Dependencies**: ResumeParser (library), DataValidator

---

#### 3.4 NLP Service
**Component Name**: `NLPService`

**Purpose**: Dedicated component for natural language processing of job descriptions

**Responsibilities**:
- Extract keywords from job description text
- Identify technical skills and tools
- Categorize skills (programming, soft skills, domain knowledge)
- Match skills against predefined skill dictionary
- Perform basic text preprocessing (tokenization, stopword removal)
- Cache NLP analysis results

**Dependencies**: NLP libraries (NLTK, spaCy), SkillDictionary, CacheManager

---

#### 3.5 Skill Gap Analyzer
**Component Name**: `SkillGapAnalyzer`

**Purpose**: Compare student profile against job requirements

**Responsibilities**:
- Compare student skills with job description skills
- Identify missing skills
- Generate actionable improvement suggestions
- Prioritize skill gaps by importance
- Format suggestions for user display

**Dependencies**: NLPService

---

#### 3.6 Data Validator
**Component Name**: `DataValidator`

**Purpose**: Schema-based validation for all input data

**Responsibilities**:
- Validate student profile inputs (types, ranges, required fields)
- Validate job description inputs
- Validate resume file uploads
- Validate API request payloads
- Return detailed validation error messages
- Sanitize inputs to prevent injection attacks

**Technology**: Pydantic or Marshmallow

---

### 4. ML Layer Components

#### 4.1 ML Model Manager
**Component Name**: `MLModelManager`

**Purpose**: Singleton pattern for managing ML model lifecycle

**Responsibilities**:
- Load all ensemble models at application startup
- Maintain model instances in memory
- Provide thread-safe access to models
- Handle model loading errors
- Support model versioning
- Preprocess input features for prediction
- Post-process model outputs

**Models Managed**:
- Random Forest Classifier
- Gradient Boosting Classifier
- Logistic Regression
- Voting Classifier (ensemble)

**Technology**: scikit-learn, pickle

---

#### 4.2 Feature Engineer
**Component Name**: `FeatureEngineer`

**Purpose**: Transform raw inputs into model-ready features

**Responsibilities**:
- Encode categorical variables (branch/department)
- Scale numerical features (CGPA, aptitude, skills)
- Create derived features if needed
- Handle missing values
- Ensure feature order matches training data
- Validate feature ranges

**Dependencies**: scikit-learn preprocessing

---

### 5. Data Access Layer Components

#### 5.1 Data Repository
**Component Name**: `DataRepository`

**Purpose**: Direct Supabase client for all database operations

**Responsibilities**:
- Store user inputs in `user_inputs` table
- Store predictions in `predictions` table
- Store job descriptions in `job_descriptions` table
- Store/retrieve pre-computed insights in `insights` table
- Execute queries for analytics aggregations
- Handle database connection errors
- Implement retry logic for transient failures

**Technology**: Supabase Python client

**Tables**:
- `user_inputs`: Student profile submissions
- `predictions`: Prediction results with model outputs
- `job_descriptions`: Analyzed job postings
- `insights`: Pre-computed analytics metrics

---

### 6. Infrastructure Layer Components

#### 6.1 Cache Manager
**Component Name**: `CacheManager`

**Purpose**: Result caching based on input hash

**Responsibilities**:
- Cache prediction results by input hash
- Cache NLP analysis results by job description hash
- Cache analytics insights with TTL
- Implement cache invalidation strategies
- Handle cache misses gracefully
- Monitor cache hit rates

**Technology**: In-memory cache (Python dict with LRU) or Redis (if needed)

---

#### 6.2 Logger
**Component Name**: `Logger`

**Purpose**: Centralized logging for all components

**Responsibilities**:
- Provide single logger instance shared across application
- Log to centralized log service
- Include timestamp, request ID, log level, message
- Exclude sensitive data (passwords, tokens, PII)
- Support structured logging format
- Configure log levels per environment

**Technology**: Python logging module, structured logging library

---

#### 6.3 Configuration Manager
**Component Name**: `ConfigManager`

**Purpose**: Hybrid configuration management

**Responsibilities**:
- Load default configuration from config files
- Override with environment variables
- Provide type-safe config access
- Validate required configuration at startup
- Support different configs per environment (dev, prod)

**Configuration Sources**:
- `config.py`: Default values
- Environment variables: Overrides (Supabase URL, API keys, etc.)

---

#### 6.4 Security Headers Middleware
**Component Name**: `SecurityHeadersMiddleware`

**Purpose**: Apply HTTP security headers to all responses

**Responsibilities**:
- Set Content-Security-Policy header
- Set Strict-Transport-Security header
- Set X-Content-Type-Options header
- Set X-Frame-Options header
- Set Referrer-Policy header
- Ensure headers meet SECURITY-04 requirements

---

### 7. Utility Components

#### 7.1 Skill Dictionary
**Component Name**: `SkillDictionary`

**Purpose**: Maintain predefined list of skills for matching

**Responsibilities**:
- Store comprehensive skill taxonomy
- Categorize skills (programming languages, frameworks, tools, soft skills)
- Support skill lookup and matching
- Allow skill dictionary updates
- Provide skill synonyms and variations

**Data Source**: JSON file or database table

---

#### 7.2 Error Handler
**Component Name**: `ErrorHandler`

**Purpose**: Global error handling for Flask application

**Responsibilities**:
- Catch unhandled exceptions
- Format error responses consistently
- Log errors with full context
- Return user-friendly error messages (no stack traces in production)
- Map exception types to HTTP status codes
- Implement fail-closed behavior

---

## Component Interaction Summary

### Request Flow Example (Prediction):
1. **FrontendApp** → Sends prediction request
2. **PredictionBlueprint** → Validates request, applies rate limiting
3. **PredictionService** → Orchestrates prediction workflow
4. **NLPService** → Analyzes job description
5. **MLModelManager** → Generates predictions from ensemble models
6. **SkillGapAnalyzer** → Compares skills and generates suggestions
7. **CacheManager** → Caches result
8. **DataRepository** → Stores prediction in Supabase
9. **PredictionBlueprint** → Returns formatted response
10. **FrontendApp** → Displays results with charts

---

## Component Count Summary

- **Presentation Layer**: 1 component
- **API Layer**: 5 components (4 blueprints + middleware)
- **Business Logic Layer**: 6 components
- **ML Layer**: 2 components
- **Data Access Layer**: 1 component
- **Infrastructure Layer**: 4 components
- **Utility Components**: 2 components

**Total**: 21 components

---

## Design Principles Applied

1. **Single Responsibility**: Each component has one clear purpose
2. **Separation of Concerns**: Layers have distinct responsibilities
3. **Dependency Direction**: Dependencies flow inward (API → Business Logic → Data/ML)
4. **Testability**: Components designed for unit testing with partial DI
5. **Maintainability**: Clear boundaries and interfaces
6. **Scalability**: Stateless components, caching strategy, singleton models

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Next**: Define component methods and interfaces

