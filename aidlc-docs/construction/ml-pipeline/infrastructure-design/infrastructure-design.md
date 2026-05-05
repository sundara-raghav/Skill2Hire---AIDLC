# Infrastructure Design: ML Pipeline Unit

## Overview

This document maps logical components from the NFR Design to actual infrastructure services and deployment architecture for the ML Pipeline unit.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## Infrastructure Architecture

### Architecture Principle

**Simple Script-Based Pipeline with Minimal Infrastructure**

The ML Pipeline follows a minimalist infrastructure approach with no additional infrastructure components (no queues, caches, circuit breakers, or orchestration platforms). All infrastructure is provided by GitHub's platform and standard filesystem operations.

**Key Characteristics**:
- Single GitHub Actions runner for training
- Git + Git LFS for storage and versioning
- File-based logging and metrics
- No cloud services (S3, CloudWatch, etc.)
- No container orchestration (Kubernetes, ECS, etc.)
- No message queues or caches

---

## 1. Compute Infrastructure

### 1.1 Training Compute

**Service**: GitHub Actions Runner (ubuntu-latest)

**Specifications**:
- **CPU**: 2 cores
- **RAM**: 7 GB
- **Disk**: 14 GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.9

**Rationale**: GitHub Actions default runner provides sufficient compute for training 1000-record dataset in < 1 minute. No need for larger runners or custom infrastructure.

**Cost**: Free (included in GitHub Free tier for public repositories)

**Availability**: On-demand (runner provisioned when workflow triggers)

**Scalability**: 
- Vertical: Cannot scale (fixed runner specs)
- Horizontal: Hybrid approach - Joblib parallelizes models on single runner, multiple workflow runs can execute concurrently

---

### 1.2 Inference Compute

**Service**: Render Web Service (Backend container)

**Specifications**:
- **CPU**: Shared (Render Free tier)
- **RAM**: 512 MB (Render Free tier)
- **Disk**: Ephemeral (models loaded from Git)
- **OS**: Container (Linux)
- **Python**: 3.9

**Rationale**: Backend loads trained models at startup and serves predictions. No separate ML inference service needed.

**Cost**: Free (Render Free tier)

**Availability**: 24/7 (web service)

**Scalability**: Vertical scaling only (upgrade Render plan for more resources)

---

## 2. Storage Infrastructure

### 2.1 Model Storage

**Service**: Git + Git LFS (Large File Storage)

**Storage Type**: Version-controlled file storage

**Storage Location**: GitHub repository (`ml-pipeline/models/trained/`)

**File Types**:
- Model files: `.pkl` (pickle format)
- Preprocessing artifacts: `.pkl` (scaler, encoder)
- Metrics: `.json` (JSON format)

**Storage Capacity**:
- Git LFS: 1 GB free storage, 1 GB/month bandwidth
- Estimated usage: ~50 MB per model version
- Capacity: ~20 model versions before hitting limit

**Versioning Strategy**: Sequential versioning (v1, v2, v3, ...)

**Lifecycle Policy**: Keep all versions indefinitely (manual cleanup if storage limit reached)

**Access Pattern**:
- Write: GitHub Actions commits models after training
- Read: Backend loads models from filesystem at startup

**Rationale**: Git LFS provides version control, audit trail, and sufficient storage for project scope. No need for cloud object storage (S3, Azure Blob).

---

### 2.2 Dataset Storage

**Service**: Git + Git LFS

**Storage Location**: `ml-pipeline/data/processed/`

**File Types**: `.csv` (CSV format)

**Storage Capacity**: ~1 MB per dataset

**Versioning**: Committed to Git with each training run

**Rationale**: Datasets are small (~1000 records) and benefit from version control.

---

### 2.3 Log Storage

**Service**: GitHub Actions Artifacts (90-day retention)

**Storage Location**: GitHub Actions workflow artifacts

**File Types**: `.log` (plain text)

**Retention Policy**: 90 days (GitHub Actions default)

**Access Pattern**: Download from GitHub Actions UI or API

**Rationale**: Logs are useful for debugging but don't need permanent storage. 90-day retention is sufficient. Not committed to Git to avoid repository bloat.

---

### 2.4 Metrics Storage

**Service**: GitHub Actions Artifacts (90-day retention)

**Storage Location**: GitHub Actions workflow artifacts

**File Types**: `.json` (JSON format), `.md` (Markdown reports)

**Retention Policy**: 90 days

**Access Pattern**: Download from GitHub Actions UI or API

**Rationale**: Metrics and reports are useful for analysis but don't need permanent storage. 90-day retention is sufficient.

---

## 3. CI/CD Infrastructure

### 3.1 CI/CD Platform

**Service**: GitHub Actions

**Workflow File**: `.github/workflows/ml-pipeline.yml`

**Triggers**:
1. **Push to main branch**: Automatic training on code changes
2. **Daily schedule**: Cron job at midnight UTC (`0 0 * * *`)
3. **Manual trigger**: `workflow_dispatch` for on-demand training

**Workflow Steps**:
1. Checkout code (with Git LFS)
2. Set up Python 3.9
3. Install dependencies (`pip install -r ml-pipeline/requirements.txt`)
4. Run training script (`python ml-pipeline/train.py`)
5. Upload artifacts (logs, reports) to GitHub Actions
6. Commit trained models to Git (if training successful)
7. Trigger deployment (Render auto-deploys on Git push)

**Timeout**: 10 minutes (training should complete in < 1 minute)

**Concurrency**: Allow multiple workflow runs in parallel (hybrid scalability)

**Rationale**: GitHub Actions is integrated with repository, provides free compute, and handles all CI/CD needs without additional infrastructure.

---

### 3.2 Model Deployment Pipeline

**Deployment Flow**:
```
1. GitHub Actions trains models
2. Models committed to Git repository
3. Git push triggers Render deployment
4. Render builds Docker image (includes models)
5. Render deploys new container
6. Backend loads models at startup
7. New models available for inference
```

**Deployment Strategy**: Full redeploy (commit models → trigger deployment)

**Deployment Time**: ~5-10 minutes (Render build + deploy)

**Rollback Strategy**: Git revert to previous commit, trigger redeploy

**Rationale**: Simple deployment flow with no additional infrastructure. Full redeploy is acceptable for infrequent model updates.

---

## 4. Monitoring Infrastructure

### 4.1 Logging Infrastructure

**Service**: GitHub Actions Artifacts

**Log Format**: Simple structured logging
```
2026-05-05 12:00:00 INFO: Starting dataset generation (target: 1000 records)
2026-05-05 12:00:09 INFO: Dataset generation complete (1000 records)
```

**Log Levels**:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Model-specific failures
- CRITICAL: Pipeline failures

**Log Destinations**:
- GitHub Actions console (real-time)
- GitHub Actions artifacts (90-day retention)

**Log Access**: GitHub Actions UI or API

**Rationale**: Simple file-based logging is sufficient. No need for centralized logging service (CloudWatch, Stackdriver).

---

### 4.2 Metrics Infrastructure

**Service**: GitHub Actions Artifacts

**Metrics Format**: JSON files
```json
{
  "model_name": "random_forest",
  "version": "v1",
  "metrics": {
    "accuracy": 0.87,
    "f1_score": 0.87,
    "roc_auc": 0.92
  }
}
```

**Metrics Storage**: GitHub Actions artifacts (90-day retention)

**Metrics Access**: Download from GitHub Actions UI or API

**Rationale**: JSON files are human-readable and machine-parseable. No need for time-series database (Prometheus, InfluxDB).

---

### 4.3 Alerting Infrastructure

**Service**: GitHub Actions Notifications

**Alert Triggers**:
- Workflow failure (training errors)
- Workflow timeout (> 10 minutes)

**Alert Channels**:
- Email (GitHub account email)
- GitHub UI (workflow status badge)
- GitHub commit status checks

**Alert Recipients**: Repository collaborators

**Rationale**: GitHub Actions provides built-in failure notifications. No need for dedicated alerting service (PagerDuty, Opsgenie).

---

## 5. Security Infrastructure

### 5.1 Vulnerability Scanning

**Service**: GitHub Dependabot

**Configuration**: `.github/dependabot.yml`
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/ml-pipeline"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

**Scan Frequency**: Weekly

**Scan Scope**: `ml-pipeline/requirements.txt`

**Action on Vulnerability**: Automatic PR creation with dependency update

**Rationale**: Dependabot is integrated with GitHub, requires no additional setup, and automatically creates PRs for vulnerable dependencies.

---

### 5.2 Secrets Management

**Service**: GitHub Secrets

**Secrets Stored**:
- `DOCKER_HUB_USERNAME`: Docker Hub username (for image push)
- `DOCKER_HUB_TOKEN`: Docker Hub access token (for image push)
- `RENDER_API_KEY`: Render API key (for deployment trigger, if needed)

**Access Control**: Repository secrets accessible only to GitHub Actions workflows

**Rationale**: GitHub Secrets provides secure storage for CI/CD credentials. No external secrets needed for training (synthetic data, no external APIs).

---

## 6. Deployment Infrastructure

### 6.1 Container Platform

**Service**: Render (Platform-as-a-Service)

**Service Type**: Web Service

**Container Specifications**:
- **CPU**: Shared (Free tier)
- **RAM**: 512 MB (Free tier)
- **Disk**: Ephemeral
- **Region**: US (default)

**Deployment Source**: GitHub repository (auto-deploy on push)

**Build Process**:
1. Render detects push to main branch
2. Render clones repository (with Git LFS)
3. Render builds Docker image from Dockerfile
4. Render deploys new container
5. Health check validates deployment

**Rationale**: Render provides free hosting, automatic deployments, and handles all infrastructure management.

---

### 6.2 Container Registry

**Service**: Docker Hub

**Registry**: Public Docker Hub registry

**Image Name**: `<username>/skill2hire:latest`

**Image Build**: GitHub Actions builds and pushes image

**Image Pull**: Render pulls image from Docker Hub

**Rationale**: Docker Hub provides free public image hosting. Render can pull images from Docker Hub for deployment.

---

### 6.3 Deployment Strategy

**Strategy**: Full Redeploy (Blue-Green at platform level)

**Deployment Flow**:
1. New models committed to Git
2. Git push triggers Render deployment
3. Render builds new Docker image (includes new models)
4. Render deploys new container
5. Render performs health check
6. Render switches traffic to new container (zero-downtime)
7. Old container terminated

**Rollback**: Git revert + redeploy

**Downtime**: Zero (Render handles blue-green deployment)

**Rationale**: Simple deployment strategy with no additional infrastructure. Render handles zero-downtime deployments automatically.

---

## 7. Development Infrastructure

### 7.1 Local Development Environment

**Environment**: Local Python environment

**Setup**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r ml-pipeline/requirements.txt

# Run training locally
python ml-pipeline/train.py
```

**IDE**: Any Python IDE (VS Code, PyCharm, etc.)

**Testing**: Local execution before pushing to GitHub

**Rationale**: Simple local environment with no additional infrastructure. Developers can test training locally before pushing.

---

### 7.2 Artifact Storage (Development)

**Service**: GitHub Actions Artifacts

**Retention**: 90 days

**Artifacts Stored**:
- Training logs (`.log`)
- Evaluation reports (`.md`)
- Metrics (`.json`)

**Access**: Download from GitHub Actions UI

**Rationale**: GitHub Actions artifacts provide temporary storage for debugging. No need for permanent artifact storage.

---

## 8. Networking Infrastructure

### 8.1 Training Network Connectivity

**Network Access**: Internet access for dependency installation only

**Allowed Connections**:
- PyPI (pip install)
- GitHub (git clone, git push)

**Blocked Connections**:
- External APIs (no data sources)
- External ML services (no model registries)

**Rationale**: Training uses synthetic data and requires no external services. Internet access only needed for dependency installation.

---

### 8.2 Inference Network Connectivity

**Network Access**: No network access needed for model loading

**Model Loading**: Local filesystem (models in Docker image)

**Inference**: In-process (no external ML APIs)

**Rationale**: Models are loaded from local filesystem at Backend startup. No network access needed for inference.

---

## 9. Scalability Infrastructure

### 9.1 Parallel Training Infrastructure

**Approach**: Hybrid Scalability

**Level 1 - Intra-Workflow Parallelization**:
- **Service**: Joblib multiprocessing
- **Parallelization**: 4 models train in parallel on single runner
- **CPU Utilization**: 100% (use all 2 cores)
- **Speedup**: 3-4x compared to sequential training

**Level 2 - Inter-Workflow Parallelization**:
- **Service**: GitHub Actions concurrency
- **Parallelization**: Multiple workflow runs can execute concurrently
- **Use Case**: Multiple developers push simultaneously, or scheduled run overlaps with push trigger
- **Concurrency Limit**: No limit (GitHub Actions default)

**Implementation**:
```python
# Joblib parallelization (Level 1)
from joblib import Parallel, delayed

results = Parallel(n_jobs=-1)(
    delayed(train_model)(config) for config in model_configs
)
```

```yaml
# GitHub Actions concurrency (Level 2)
concurrency:
  group: ml-pipeline-${{ github.ref }}
  cancel-in-progress: false  # Allow multiple runs
```

**Rationale**: Hybrid approach provides parallelization at both model level (Joblib) and workflow level (GitHub Actions), maximizing throughput without additional infrastructure.

---

## Infrastructure Component Summary

| Component | Service | Purpose | Cost |
|-----------|---------|---------|------|
| **Training Compute** | GitHub Actions (ubuntu-latest) | Execute training script | Free |
| **Inference Compute** | Render Web Service | Serve predictions | Free |
| **Model Storage** | Git + Git LFS | Version-controlled model storage | Free (1 GB) |
| **Dataset Storage** | Git + Git LFS | Version-controlled dataset storage | Free |
| **Log Storage** | GitHub Actions Artifacts | Temporary log storage (90 days) | Free |
| **Metrics Storage** | GitHub Actions Artifacts | Temporary metrics storage (90 days) | Free |
| **CI/CD Platform** | GitHub Actions | Automated training pipeline | Free |
| **Container Registry** | Docker Hub | Docker image storage | Free |
| **Container Platform** | Render | Application hosting | Free |
| **Vulnerability Scanning** | GitHub Dependabot | Dependency security scanning | Free |
| **Secrets Management** | GitHub Secrets | CI/CD credential storage | Free |
| **Logging** | GitHub Actions Artifacts | Training logs | Free |
| **Alerting** | GitHub Actions Notifications | Failure notifications | Free |
| **Development** | Local Python environment | Local testing | Free |

**Total Infrastructure Cost**: $0/month (all free tiers)

---

## Infrastructure Topology

### Training Infrastructure Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Platform                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ GitHub Actions Runner (ubuntu-latest)                   │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ ML Pipeline Training (train.py)                   │  │ │
│  │  │                                                    │  │ │
│  │  │  ┌─────────────────────────────────────────────┐ │  │ │
│  │  │  │ Joblib Parallel (4 models)                  │ │  │ │
│  │  │  │  - Random Forest                            │ │  │ │
│  │  │  │  - Gradient Boosting                        │ │  │ │
│  │  │  │  - Logistic Regression                      │ │  │ │
│  │  │  │  - Voting Classifier                        │ │  │ │
│  │  │  └─────────────────────────────────────────────┘ │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                           │                             │ │
│  │                           ↓                             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ Filesystem (runner disk)                          │  │ │
│  │  │  - Models (.pkl)                                  │  │ │
│  │  │  - Logs (.log)                                    │  │ │
│  │  │  - Metrics (.json)                                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Git Repository                                          │ │
│  │  - Commit models (Git LFS)                             │ │
│  │  - Upload artifacts (logs, metrics)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ↓
                   ┌────────────────┐
                   │ Render Platform│
                   │ (auto-deploy)  │
                   └────────────────┘
```

### Inference Infrastructure Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     Render Platform                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Docker Container (skill2hire)                           │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ Backend (Flask)                                   │  │ │
│  │  │                                                    │  │ │
│  │  │  ┌─────────────────────────────────────────────┐ │  │ │
│  │  │  │ MLModelManager (Singleton)                  │ │  │ │
│  │  │  │  - Load models at startup                   │ │  │ │
│  │  │  │  - Serve predictions                        │ │  │ │
│  │  │  └─────────────────────────────────────────────┘ │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                           │                             │ │
│  │                           ↓                             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ Filesystem (container disk)                       │  │ │
│  │  │  - Models (.pkl) from Git LFS                     │  │ │
│  │  │  - Preprocessing artifacts (.pkl)                 │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Decisions Rationale

### Why GitHub Actions?
- **Integrated**: Built into GitHub, no additional setup
- **Free**: Sufficient free tier for project scope
- **Simple**: No infrastructure management required
- **Sufficient**: 2-core runner handles 1000-record training in < 1 minute

### Why Git + Git LFS?
- **Version Control**: Complete audit trail for models and datasets
- **Simple**: No additional storage service needed
- **Sufficient**: 1 GB free storage handles ~20 model versions
- **Rollback**: Easy rollback via Git revert

### Why GitHub Actions Artifacts (not Git)?
- **Logs/Metrics**: Temporary data doesn't need permanent storage
- **Repository Size**: Avoid bloating Git repository with logs
- **Retention**: 90 days sufficient for debugging
- **Cost**: Free (included in GitHub Actions)

### Why Render?
- **Free**: Free tier sufficient for project scope
- **Simple**: No infrastructure management required
- **Auto-Deploy**: Automatic deployments on Git push
- **Zero-Downtime**: Built-in blue-green deployments

### Why Joblib + GitHub Actions Concurrency?
- **Hybrid Scalability**: Parallelization at both model and workflow levels
- **Simple**: No distributed training framework needed
- **Sufficient**: Handles project scope (4 models, < 1 minute training)
- **Cost**: Free (no additional infrastructure)

---

## Infrastructure Limitations

### Current Limitations

1. **Storage Capacity**: Git LFS 1 GB limit (~20 model versions)
   - **Mitigation**: Manual cleanup of old versions if limit reached
   - **Future**: Upgrade to Git LFS data pack ($5/month for 50 GB)

2. **Compute Resources**: GitHub Actions 2-core runner
   - **Limitation**: Cannot scale vertically
   - **Mitigation**: Sufficient for project scope (1000 records)
   - **Future**: Self-hosted runner with more cores if dataset grows

3. **Artifact Retention**: 90-day retention for logs/metrics
   - **Limitation**: Logs deleted after 90 days
   - **Mitigation**: Download important logs before expiration
   - **Future**: Commit critical logs to Git if permanent storage needed

4. **Deployment Time**: 5-10 minutes for full redeploy
   - **Limitation**: Slow model updates
   - **Mitigation**: Acceptable for infrequent updates
   - **Future**: Hot-reload models if frequent updates needed

---

## Infrastructure Compliance

### Security Baseline Compliance

**Applicable Rules**:
- ✅ **SECURITY-03**: Application-level logging (GitHub Actions artifacts)
- ✅ **SECURITY-05**: Input validation (44 business rules enforced)
- ✅ **SECURITY-10**: Software supply chain security (Dependabot scanning, minor version pinning)
- ✅ **SECURITY-13**: Software and data integrity (Git provides audit trail)
- ✅ **SECURITY-15**: Exception handling (fail-closed on critical errors)

**Non-Applicable Rules**: All other security rules (N/A for ML Pipeline)

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC Infrastructure Design
- **Next**: deployment-architecture.md

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial infrastructure design document |
