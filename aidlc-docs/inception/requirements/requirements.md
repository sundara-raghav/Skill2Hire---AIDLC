# Requirements Document: Skill2Hire - Placement Prediction AI Web App

## Intent Analysis Summary

### User Request
Build a full-stack AI-powered Placement Prediction Web Application using Python Flask that predicts student placement probability for specific jobs using ensemble machine learning models, provides skill gap analysis, and includes college-wide insights dashboard.

### Request Type
**New Project** - Greenfield development

### Scope Estimate
**System-wide** - Full-stack application including:
- Frontend (HTML/CSS/JavaScript with Chart.js)
- Backend (Flask REST API)
- Machine Learning Pipeline (Ensemble models)
- Database (Supabase)
- DevOps (Docker, GitHub Actions CI/CD)
- Deployment (Render)

### Complexity Estimate
**Complex** - Multi-component system with:
- Machine learning model training and inference
- NLP processing for job descriptions
- Real-time predictions with multiple models
- Data visualization and analytics
- CI/CD automation with model retraining
- Production deployment with monitoring

---

## 1. Functional Requirements

### 1.1 User Input Collection
**FR-01**: The system SHALL collect the following inputs from users:
- Name (optional text field)
- CGPA (numeric, 0.0-10.0 scale)
- Aptitude Score (numeric)
- Programming Skills (numeric scale 1-10)
- Communication Skills (numeric scale 1-10)
- Number of Projects (integer)
- Internship Experience (boolean: Yes/No)
- Certifications Count (integer)
- Branch/Department (dropdown/text)
- Job Description (multi-line text area)

**FR-02**: All fields except Name SHALL be required for prediction.

**FR-03**: The system SHALL provide basic input validation:
- Required field checks
- Data type validation
- Range validation for numeric fields

### 1.2 Job Description Analysis
**FR-04**: The system SHALL perform basic NLP analysis on job descriptions:
- Keyword extraction using simple text processing
- Skill matching against predefined skill list
- Identification of technical skills, tools, and technologies mentioned

**FR-05**: The system SHALL maintain a skill dictionary for matching purposes.

### 1.3 Machine Learning Prediction
**FR-06**: The system SHALL use an ensemble learning approach with:
- Random Forest Classifier
- Gradient Boosting Classifier
- Logistic Regression
- Voting Classifier (final aggregated model)

**FR-07**: The system SHALL output:
- Overall Placement Probability (percentage 0-100%)
- Confidence Score
- Individual predictions from each model (RF, GB, LR)

**FR-08**: The system SHALL generate predictions within 5 seconds of request submission.

### 1.4 Skill Gap Analysis
**FR-09**: The system SHALL analyze missing skills by:
- Comparing user's profile against job description keywords
- Identifying skills present in job description but not in user profile
- Generating actionable improvement suggestions

**FR-10**: Suggestions SHALL include specific areas for improvement:
- Technical skills (e.g., "Improve DSA, SQL")
- Soft skills (e.g., "Enhance Communication")
- Experience gaps (e.g., "Add more projects")

### 1.5 Multi-Model Comparison Dashboard
**FR-11**: The system SHALL display prediction results from all models:
- Random Forest prediction (%)
- Gradient Boosting prediction (%)
- Logistic Regression prediction (%)
- Final ensemble prediction (%)

**FR-12**: Results SHALL be visualized using bar charts (Chart.js).

### 1.6 College-wide Insights
**FR-13**: The system SHALL provide analytics dashboard showing:
- Placement percentage by department/branch
- Average CGPA vs placement correlation
- Top skills required across all placements
- Trends and patterns from historical data

**FR-14**: Insights SHALL be generated from the synthetic dataset (1000+ records).

### 1.7 Resume Upload Feature (BONUS - Included)
**FR-15**: The system SHALL support resume upload:
- Accept PDF and DOCX formats
- Parse resume to extract relevant information
- Auto-populate form fields from parsed data

**FR-16**: Resume parsing SHALL extract:
- Education details (CGPA, branch)
- Skills and technologies
- Project count
- Internship experience
- Certifications

### 1.8 Real-time Suggestions (BONUS - Included)
**FR-17**: The system SHALL provide real-time suggestions as user types:
- Skill recommendations based on partial input
- Common skills for selected branch/department
- Trending skills in job market

### 1.9 Data Storage
**FR-18**: The system SHALL store all data permanently in Supabase:
- User inputs (all form data)
- Predictions (all model outputs)
- Job descriptions analyzed
- Timestamps for all records

**FR-19**: No user authentication required - open access model.

---

## 2. Non-Functional Requirements

### 2.1 Performance
**NFR-01**: Prediction API response time SHALL be less than 5 seconds under normal load.

**NFR-02**: The system SHALL handle concurrent requests efficiently.

**NFR-03**: Frontend page load time SHALL be optimized for modern browsers.

### 2.2 Usability
**NFR-04**: The UI SHALL use a light theme with clean, modern design.

**NFR-05**: The interface SHALL be responsive and work on desktop and tablet devices.

**NFR-06**: The system SHALL provide clear error messages for validation failures.

**NFR-07**: The system SHALL meet WCAG 2.1 Level AA accessibility standards:
- Semantic HTML structure
- Proper alt text for images
- Keyboard navigation support
- Sufficient color contrast
- Screen reader compatibility

### 2.3 Browser Compatibility
**NFR-08**: The system SHALL support modern browsers:
- Chrome (latest version)
- Firefox (latest version)
- Safari (latest version)
- Edge (latest version)

### 2.4 Security
**NFR-09**: The system SHALL implement rate limiting on all API endpoints to prevent abuse.

**NFR-10**: The system SHALL follow security baseline rules (SECURITY-01 through SECURITY-15):
- Encryption at rest and in transit (Supabase, API)
- HTTP security headers for web application
- Input validation on all API parameters
- Application-level logging with centralized log service
- Secure error handling (no stack traces in production)
- Software supply chain security (dependency scanning)
- No hardcoded credentials

**NFR-11**: The system SHALL validate and sanitize all user inputs to prevent injection attacks.

### 2.5 Reliability
**NFR-12**: The system SHALL implement comprehensive error handling.

**NFR-13**: The system SHALL log all errors and exceptions.

**NFR-14**: The system SHALL provide graceful degradation if external services fail.

### 2.6 Maintainability
**NFR-15**: Code SHALL follow Python PEP 8 style guidelines.

**NFR-16**: The system SHALL include inline documentation and docstrings.

**NFR-17**: The system SHALL use modular architecture for easy maintenance.

### 2.7 Monitoring & Logging
**NFR-18**: The system SHALL implement comprehensive monitoring:
- Application errors and exceptions
- API performance metrics
- Model prediction accuracy tracking
- User interaction patterns

**NFR-19**: Logs SHALL include:
- Timestamp
- Request ID
- Log level
- Message
- No sensitive data (passwords, tokens, PII)

---

## 3. Data Requirements

### 3.1 Synthetic Dataset
**DR-01**: The system SHALL use a synthetic dataset with 1000+ records.

**DR-02**: Dataset SHALL include fields:
- CGPA (float)
- Aptitude Score (numeric)
- Programming Skills (1-10)
- Communication Skills (1-10)
- Number of Projects (integer)
- Internship Experience (boolean)
- Certifications Count (integer)
- Branch/Department (categorical)
- Placement Status (boolean: Placed/Not Placed)

**DR-03**: Dataset SHALL be balanced (approximately 50% placed, 50% not placed).

**DR-04**: Dataset SHALL have no duplicate records.

**DR-05**: Dataset SHALL be preprocessed and cleaned before model training.

**DR-06**: Dataset generation SHALL aim for higher accuracy across all models through:
- Realistic feature correlations
- Appropriate feature distributions
- Balanced class representation

### 3.2 Database Schema (Supabase)
**DR-07**: The system SHALL maintain the following tables:
- **user_inputs**: Store all form submissions
- **predictions**: Store prediction results with model outputs
- **job_descriptions**: Store analyzed job descriptions
- **insights**: Store aggregated analytics data

---

## 4. Machine Learning Requirements

### 4.1 Model Training
**ML-01**: Models SHALL be trained on the synthetic dataset.

**ML-02**: Training process SHALL include:
- Data preprocessing (scaling, encoding)
- Feature engineering
- Train-test split (80-20)
- Cross-validation
- Hyperparameter tuning

**ML-03**: Model training SHALL be performed independently by developer.

**ML-04**: Trained models SHALL be saved as .pkl files.

**ML-05**: Models SHALL be versioned and stored in Git repository.

### 4.2 Model Evaluation
**ML-06**: Models SHALL be evaluated using:
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC

**ML-07**: Model performance metrics SHALL be logged and tracked.

### 4.3 Model Deployment
**ML-08**: Trained models SHALL be loaded at Flask application startup.

**ML-09**: Model inference SHALL be performed in-memory for fast predictions.

**ML-10**: Model retraining SHALL be triggered by developer push to GitHub.

---

## 5. API Requirements

### 5.1 Endpoints
**API-01**: The system SHALL provide the following REST API endpoints:

#### POST /predict
- **Purpose**: Generate placement prediction
- **Input**: JSON with all user input fields + job description
- **Output**: JSON with prediction results, confidence, model breakdown
- **Rate Limit**: Applied

#### POST /analyze-job
- **Purpose**: Analyze job description for skills
- **Input**: JSON with job description text
- **Output**: JSON with extracted keywords and skills
- **Rate Limit**: Applied

#### GET /insights
- **Purpose**: Retrieve college-wide analytics
- **Input**: Optional query parameters (branch, date range)
- **Output**: JSON with aggregated insights
- **Rate Limit**: Applied

### 5.2 API Design
**API-02**: All APIs SHALL return JSON responses.

**API-03**: All APIs SHALL include appropriate HTTP status codes.

**API-04**: All APIs SHALL implement CORS with appropriate restrictions.

**API-05**: All APIs SHALL validate input parameters before processing.

---

## 6. Frontend Requirements

### 6.1 User Interface
**UI-01**: The frontend SHALL include:
- Input form with all required fields
- Job description text area
- Submit button
- Results display cards
- Model comparison charts
- Insights dashboard

**UI-02**: The UI SHALL use Chart.js for data visualization.

**UI-03**: The UI SHALL provide visual feedback during prediction (loading state).

**UI-04**: The UI SHALL display results in an intuitive, easy-to-read format.

### 6.2 Responsive Design
**UI-05**: The interface SHALL be responsive and adapt to different screen sizes.

**UI-06**: The layout SHALL use modern CSS (Flexbox/Grid).

---

## 7. DevOps & Deployment Requirements

### 7.1 Docker
**DEV-01**: The system SHALL be containerized using Docker.

**DEV-02**: Docker configuration SHALL use single container approach:
- Flask application
- All Python dependencies
- Trained ML models

**DEV-03**: Dockerfile SHALL use specific Python version (not latest tag).

### 7.2 CI/CD Pipeline (GitHub Actions)
**DEV-04**: The system SHALL implement full CI/CD pipeline:
- Code linting (flake8, pylint)
- Unit tests execution
- Model training (triggered by developer push)
- Docker image build
- Deployment to Render

**DEV-05**: Pipeline SHALL run automatically on push to main branch.

**DEV-06**: Pipeline SHALL fail if tests fail or linting errors exist.

**DEV-07**: Pipeline SHALL use pinned versions for all tools and dependencies.

### 7.3 Deployment
**DEV-08**: The system SHALL be deployed to Render platform.

**DEV-09**: Deployment SHALL be automated via GitHub Actions.

**DEV-10**: Environment variables SHALL be configured in Render dashboard:
- Supabase credentials
- API keys
- Configuration settings

---

## 8. Testing Requirements

### 8.1 Unit Testing
**TEST-01**: The system SHALL include unit tests for:
- ML model prediction functions
- API endpoint handlers
- Data validation functions
- NLP processing functions

**TEST-02**: Unit tests SHALL achieve reasonable code coverage.

**TEST-03**: Tests SHALL use pytest framework.

### 8.2 Property-Based Testing (Partial Enforcement)
**TEST-04**: Property-based testing SHALL be applied to:
- Pure functions (data preprocessing, feature engineering)
- Serialization round-trips (model save/load)

**TEST-05**: Property-based tests SHALL use hypothesis library.

---

## 9. Extension Configuration

### 9.1 Security Extension
**EXT-01**: Security baseline rules (SECURITY-01 through SECURITY-15) SHALL be enforced as blocking constraints.

**EXT-02**: All security verification criteria SHALL be met before stage completion.

### 9.2 Property-Based Testing Extension
**EXT-03**: Property-based testing rules SHALL be partially enforced:
- Full enforcement for pure functions and serialization
- Not required for UI components or simple CRUD operations

---

## 10. Success Criteria

### 10.1 Functional Success
**SC-01**: User can input data and receive placement prediction within 5 seconds.

**SC-02**: Prediction accuracy across ensemble models meets acceptable threshold.

**SC-03**: Skill gap suggestions are relevant and actionable.

**SC-04**: College-wide insights display correctly with visualizations.

**SC-05**: Resume upload successfully extracts and populates data.

### 10.2 Technical Success
**SC-06**: Application deploys successfully to Render via GitHub Actions.

**SC-07**: All unit tests pass in CI/CD pipeline.

**SC-08**: Application handles errors gracefully without crashes.

**SC-09**: Security baseline rules are fully compliant.

**SC-10**: Application meets WCAG 2.1 Level AA accessibility standards.

### 10.3 User Experience Success
**SC-11**: UI is intuitive and requires no training to use.

**SC-12**: Results are presented clearly with visual aids.

**SC-13**: Application is responsive and works on multiple devices.

---

## 11. Out of Scope (Initial Release)

The following are explicitly out of scope for the initial release:
- User authentication and authorization
- Multi-language support
- Mobile native applications
- Advanced NLP (semantic analysis, context understanding)
- Real-time collaborative features
- Integration with external job portals
- Email notifications
- Payment processing
- Advanced analytics (predictive trends, ML model drift detection)

---

## 12. Assumptions

1. Supabase account and project are already set up
2. Render account is available for deployment
3. GitHub repository is created and accessible
4. Developer has Python 3.9+ environment
5. Synthetic dataset generation is handled before model training
6. No real student data is used (privacy compliance)
7. Internet connectivity is available for API calls
8. Modern browsers are used by end users

---

## 13. Dependencies

### 13.1 External Services
- Supabase (database and storage)
- Render (hosting platform)
- GitHub (version control and CI/CD)

### 13.2 Python Libraries (Estimated)
- Flask (web framework)
- scikit-learn (ML models)
- pandas (data processing)
- numpy (numerical operations)
- nltk or spacy (NLP processing)
- supabase-py (database client)
- pytest (testing)
- hypothesis (property-based testing)
- gunicorn (WSGI server)

### 13.3 Frontend Libraries
- Chart.js (data visualization)
- Vanilla JavaScript (no framework required)

---

## 14. Constraints

1. **Budget**: Free tier limitations on Supabase and Render
2. **Performance**: Single-container deployment may limit scalability
3. **Data**: Synthetic dataset only (no real student data)
4. **Time**: Initial release timeline (to be determined in workflow planning)
5. **Resources**: Solo developer or small team
6. **Technology**: Python Flask stack (no alternative frameworks)

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Approved (Pending)
- **Author**: AI-DLC Requirements Analysis
- **Reviewers**: Project Stakeholder

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial requirements document |

