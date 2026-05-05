# Infrastructure Design Plan: ML Pipeline Unit

## Overview

This plan guides the infrastructure design for the ML Pipeline unit, mapping logical components to actual infrastructure services and deployment architecture.

**Unit**: ml-pipeline  
**Date**: 2026-05-05  
**Status**: In Progress

---

## Context Analysis

### Logical Components (from NFR Design)
- **Internal**: train.py (orchestration), Python Logging, Joblib Pool, Filesystem
- **External**: GitHub Actions (CI/CD), GitHub Dependabot (security), Git/Git LFS (version control)

### Key NFR Requirements
- Local filesystem storage (no cloud storage)
- CPU-only training (no GPU)
- Single container deployment (ML + Backend + Frontend)
- GitHub Actions CI/CD
- No additional infrastructure components (no queues, caches, circuit breakers)

---

## Infrastructure Design Questions

### Category 1: Compute Infrastructure

**Q1. What compute service will run the ML Pipeline training script?**

The ML Pipeline training script (train.py) needs to execute in a compute environment. Based on the NFR requirements, training happens during CI/CD and models are loaded by Backend at runtime.

Options:
- A) GitHub Actions runner (ubuntu-latest) for training, no separate compute for inference
- B) Dedicated VM for training, Backend container for inference
- C) Serverless function (AWS Lambda, Azure Functions) for training
- D) Kubernetes pod for training

[Answer]: a

---

**Q2. What are the compute resource specifications for training?**

The ML Pipeline has specific performance requirements (< 1 minute training time).

Options:
- A) GitHub Actions default runner (2-core CPU, 7 GB RAM)
- B) GitHub Actions larger runner (4-core CPU, 16 GB RAM)
- C) Self-hosted runner with custom specs
- D) No specific requirements (use defaults)

[Answer]: a

---

### Category 2: Storage Infrastructure

**Q3. What storage service will persist trained models and datasets?**

Models and datasets need to be stored and versioned.

Options:
- A) Git repository with Git LFS for large files
- B) Cloud object storage (S3, Azure Blob, GCS)
- C) Network file system (NFS, EFS)
- D) Container volume mounts

[Answer]: a

---

**Q4. What is the storage lifecycle policy for model versions?**

The NFR requirements specify keeping all model versions indefinitely.

Options:
- A) Keep all versions indefinitely in Git LFS (manual cleanup if needed)
- B) Automated retention policy (keep last N versions)
- C) Archive old versions to cold storage
- D) Delete versions older than X days

[Answer]: a

---

### Category 3: CI/CD Infrastructure

**Q5. What CI/CD platform will orchestrate training?**

The ML Pipeline needs automated training triggers.

Options:
- A) GitHub Actions (integrated with repository)
- B) Jenkins (self-hosted)
- C) GitLab CI/CD
- D) CircleCI

[Answer]: a

---

**Q6. What triggers will initiate training runs?**

Training needs to happen frequently (daily or on push).

Options:
- A) Push to main branch + daily schedule + manual trigger
- B) Push to main branch only
- C) Daily schedule only
- D) Manual trigger only

[Answer]: b

---

**Q7. How will trained models be deployed to Backend?**

Backend needs access to trained models for inference.

Options:
- A) Models committed to Git, Backend loads from filesystem at startup
- B) Models uploaded to artifact registry, Backend downloads at startup
- C) Models baked into Docker image during build
- D) Models served via separate model serving API

[Answer]: a

---

### Category 4: Monitoring Infrastructure

**Q8. What logging infrastructure will capture training logs?**

Training logs need to be persisted and accessible.

Options:
- A) File-based logging (training.log) committed to Git
- B) Centralized logging service (CloudWatch, Stackdriver, Azure Monitor)
- C) Log aggregation platform (ELK, Splunk)
- D) GitHub Actions logs only (no persistent storage)

[Answer]: a

---

**Q9. What metrics storage will persist model performance metrics?**

Model metrics need to be stored for comparison and analysis.

Options:
- A) JSON files committed to Git alongside models
- B) Time-series database (Prometheus, InfluxDB)
- C) Model registry (MLflow, Weights & Biases)
- D) Database table (PostgreSQL, MongoDB)

[Answer]: a

---

**Q10. What alerting mechanism will notify on training failures?**

Training failures need to be detected and reported.

Options:
- A) GitHub Actions failure notifications (email + UI)
- B) Dedicated alerting service (PagerDuty, Opsgenie)
- C) Slack/Teams webhook notifications
- D) Email alerts via SMTP

[Answer]: a

---

### Category 5: Security Infrastructure

**Q11. What vulnerability scanning service will monitor dependencies?**

Dependencies need to be scanned for security vulnerabilities.

Options:
- A) GitHub Dependabot (integrated with repository)
- B) Snyk
- C) WhiteSource
- D) OWASP Dependency-Check

[Answer]: a

---

**Q12. What secrets management service will store sensitive configuration?**

Training may need access to secrets (API keys, credentials).

Options:
- A) GitHub Secrets (for CI/CD environment variables)
- B) HashiCorp Vault
- C) AWS Secrets Manager / Azure Key Vault / GCP Secret Manager
- D) No secrets needed (synthetic data, no external services)

[Answer]: a

---

### Category 6: Deployment Infrastructure

**Q13. What container platform will host the deployed application?**

The application (Backend + ML + Frontend) needs to be deployed.

Options:
- A) Render (platform-as-a-service)
- B) Docker on VM (self-hosted)
- C) Kubernetes cluster
- D) Serverless containers (AWS Fargate, Azure Container Instances)

[Answer]: a

---

**Q14. How will the Docker image be built and stored?**

The application needs to be containerized.

Options:
- A) GitHub Actions builds image, pushes to Docker Hub, Render pulls and deploys
- B) GitHub Actions builds image, pushes to GitHub Container Registry
- C) Render builds image from Dockerfile in repository
- D) Manual Docker build and push

[Answer]: a

---

**Q15. What is the deployment strategy for model updates?**

When new models are trained, they need to be deployed to production.

Options:
- A) Commit models to Git, trigger new deployment (full redeploy)
- B) Hot-reload models without redeploying Backend
- C) Blue-green deployment with model version switching
- D) Canary deployment with gradual rollout

[Answer]: a

---

### Category 7: Development Infrastructure

**Q16. What development environment will developers use for local testing?**

Developers need to test ML Pipeline locally before pushing.

Options:
- A) Local Python environment with requirements.txt
- B) Docker Compose for local development
- C) Virtual machine with full environment
- D) Cloud development environment (GitHub Codespaces, Gitpod)

[Answer]: a

---

**Q17. What artifact storage will preserve training artifacts for debugging?**

Training artifacts (logs, reports, intermediate results) may need to be preserved.

Options:
- A) GitHub Actions artifacts (90-day retention)
- B) Committed to Git repository
- C) Cloud storage bucket
- D) No artifact preservation (logs only)

[Answer]: d

---

### Category 8: Networking Infrastructure

**Q18. What network connectivity is required for training?**

Training may need network access for dependencies or external services.

Options:
- A) Internet access for pip install only (no external services during training)
- B) Internet access for external APIs (data sources, model registries)
- C) Private network access to internal services
- D) No network access (fully offline training)

[Answer]: a

---

**Q19. What network connectivity is required for Backend inference?**

Backend needs to load models and serve predictions.

Options:
- A) No network access needed (models loaded from local filesystem)
- B) Network access to model storage service
- C) Network access to external ML APIs
- D) Private network access to ML serving infrastructure

[Answer]: a

---

### Category 9: Scalability Infrastructure

**Q20. What infrastructure supports parallel model training?**

Multiple models need to train in parallel.

Options:
- A) Joblib multiprocessing on single machine (use all CPU cores)
- B) Distributed training framework (Dask, Ray, Spark)
- C) Multiple CI/CD runners in parallel
- D) GPU cluster for parallel training

[Answer]: c

---

## Answer Summary

Once all questions are answered, this section will summarize the infrastructure decisions.

[To be completed after answers are provided]

---

## Checklist

- [x] All 20 questions answered
- [x] Answers analyzed for ambiguities
- [x] Clarifications requested (if needed)
- [x] Clarifications resolved
- [x] Infrastructure design artifacts generated
- [x] Deployment architecture documented
- [ ] Infrastructure design reviewed and approved

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-05-05
- **Status**: Awaiting Answers
- **Next**: Generate infrastructure-design.md and deployment-architecture.md

