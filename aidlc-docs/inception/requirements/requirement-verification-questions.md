# Requirements Verification Questions

Please answer the following questions to help clarify and complete the requirements for the Skill2Hire Placement Prediction AI Web App.

---

## Question 1: User Authentication
Will the application require user authentication/login system?

A) No authentication - open access (as mentioned: "without login system")
B) Basic authentication for admin panel only
C) Full user authentication with registration
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 2: Data Privacy & Storage
How should user data and predictions be handled?

A) Store all inputs and predictions permanently in Supabase
B) Store only aggregated/anonymized data for insights
C) Temporary storage only - delete after session
D) User choice - opt-in for data storage
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 3: Job Description Analysis Depth
What level of NLP analysis should be performed on job descriptions?

A) Basic keyword extraction only (simple matching)
B) Advanced NLP with skill categorization and weighting
C) Full semantic analysis with context understanding
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 4: Model Training & Retraining
How should the ML model training and retraining be handled?

A) Train once with synthetic dataset, no retraining
B) Manual retraining triggered by admin
C) Automatic retraining on every push (as mentioned in DevOps)
D) Scheduled retraining (daily/weekly)
E) Other (please describe after [Answer]: tag below)

[Answer]: E)
Developer will train the model independenty with the dataset and push to github for automation 

---

## Question 5: Deployment Target
Where should the application be deployed?

A) Render (as mentioned in requirements)
B) Other cloud platform (AWS, Azure, GCP)
C) Local/on-premises deployment
D) Multiple deployment options supported
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6: Resume Upload Feature
The resume upload is listed as "BONUS" - should this be included in initial release?

A) Yes - include resume upload with parsing in initial release
B) No - skip for initial release, add later
C) Basic upload only (no parsing) in initial release
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 7: Real-time Suggestions Feature
The real-time suggestions are listed as "BONUS" - should this be included?

A) Yes - include real-time suggestions as user types
B) No - skip for initial release
C) Show suggestions only after form submission
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 8: College-wise Insights Data Source
Where will the college-wise insights data come from?

A) Generated from the synthetic dataset (1000 records)
B) Real historical data (if available)
C) Combination of synthetic and real data
D) User-uploaded institutional data
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 9: Synthetic Dataset Generation
What approach should be used for generating the 1000+ synthetic records?

A) Completely random generation with constraints
B) Based on real placement statistics/patterns
C) Use existing public datasets as reference
D) Combination of approaches
E) Other (please describe after [Answer]: tag below)

[Answer]: E
generate the dataset , no duplicates , preprocess it , give higher accuracy for each model

---

## Question 10: API Rate Limiting
Should the Flask API have rate limiting to prevent abuse?

A) Yes - implement rate limiting
B) No - open access without limits
C) Rate limiting only for prediction endpoint
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 11: Error Handling & Validation
What level of input validation and error handling is required?

A) Basic validation (required fields, data types)
B) Comprehensive validation with detailed error messages
C) Advanced validation with suggestions for corrections
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 12: Performance Requirements
What are the expected performance requirements?

A) Response time < 2 seconds for predictions
B) Response time < 5 seconds for predictions
C) No specific performance requirements
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 13: Browser Compatibility
Which browsers should be supported?

A) Modern browsers only (Chrome, Firefox, Safari, Edge - latest versions)
B) Include older browser versions (IE11, older Chrome/Firefox)
C) Mobile browsers priority
D) All of the above
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 14: Accessibility Requirements
What accessibility standards should be met?

A) Basic accessibility (semantic HTML, alt text)
B) WCAG 2.1 Level AA compliance
C) No specific accessibility requirements
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 15: Docker Configuration
What Docker setup is needed?

A) Single container (Flask app + dependencies)
B) Multi-container (Flask + Supabase local instance)
C) Docker for development only, not production
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 16: GitHub Actions CI/CD Pipeline
What should the CI/CD pipeline include?

A) Full pipeline: lint, test, train model, build, deploy to Render
B) Basic pipeline: test and deploy only
C) Model training separate from deployment pipeline
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 17: Model Versioning
How should trained models be versioned and stored?

A) Store in Git repository (.pkl files)
B) Store in cloud storage (S3, GCS, etc.)
C) Store in Supabase storage
D) No versioning - overwrite on each training
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 18: Monitoring & Logging
What monitoring and logging should be implemented?

A) Basic application logs only
B) Application logs + prediction tracking
C) Comprehensive monitoring (errors, performance, model metrics)
D) No monitoring in initial release
E) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 19: Testing Requirements
What testing coverage is expected?

A) Unit tests for ML model and API endpoints
B) Unit tests + integration tests
C) Full test suite (unit, integration, end-to-end)
D) Minimal testing - focus on functionality
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 20: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 21: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)
B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)
C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

**Instructions:**
1. Please answer each question by filling in the letter choice (A, B, C, D, E, or X) after the `[Answer]:` tag
2. If you choose "Other" or "X", please provide a brief description of your preference
3. Let me know when you've completed all answers so I can proceed with the requirements analysis

