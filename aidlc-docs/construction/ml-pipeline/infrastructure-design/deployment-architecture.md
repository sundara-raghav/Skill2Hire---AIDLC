# Deployment Architecture: ML Pipeline Unit

## Overview

This document defines the deployment architecture for the ML Pipeline unit, including deployment environments, deployment pipelines, and operational procedures.

**Unit**: ml-pipeline  
**Version**: 1.0  
**Date**: 2026-05-05

---

## Deployment Environments

### Environment Strategy

**Single Environment**: Production only (no staging/dev environments)

**Rationale**: 
- Simple project scope
- Synthetic data (no risk of data leakage)
- Git provides rollback capability
- Free tier constraints (Render Free tier = 1 environment)

---

### Production Environment

**Platform**: Render Web Service

**Environment Name**: `skill2hire-production`

**URL**: `https://skill2hire.onrender.com` (Render-provided subdomain)

**Configuration**:
- **Region**: US (default)
- **Instance Type**: Free tier (shared CPU, 512 MB RAM)
- **Auto-Deploy**: Enabled (deploy on push to main branch)
- **Health Check**: `GET /health` (Backend endpoint)
- **Environment Variables**:
  - `PYTHON_VERSION=3.9`
  - `MODEL_DIR=/app/ml-pipeline/models/trained`
  - `LOG_LEVEL=INFO`

**Deployment Source**: GitHub repository (main branch)

---

## Deployment Pipeline

### CI/CD Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository (main branch)               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Push / Daily Schedule / Manual Trigger
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow (ml-pipeline.yml)           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 1: Setup                                              │ │
│  │  - Checkout code (with Git LFS)                            │ │
│  │  - Set up Python 3.9                                       │ │
│  │  - Install dependencies (pip install -r requirements.txt)  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 2: Training                                           │ │
│  │  - Run training script (python ml-pipeline/train.py)       │ │
│  │  - Generate models, logs, metrics                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 3: Artifact Upload                                    │ │
│  │  - Upload logs to GitHub Actions artifacts                 │ │
│  │  - Upload metrics to GitHub Actions artifacts              │ │
│  │  - Upload reports to GitHub Actions artifacts              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 4: Model Commit                                       │ │
│  │  - Commit trained models to Git (with Git LFS)             │ │
│  │  - Push to main branch                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Git push triggers Render deployment
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Render Deployment Pipeline                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 1: Build                                              │ │
│  │  - Clone repository (with Git LFS)                         │ │
│  │  - Build Docker image from Dockerfile                      │ │
│  │  - Include trained models in image                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Stage 2: Deploy                                             │ │
│  │  - Start new container with new image                      │ │
│  │  - Run health check (GET /health)                          │ │
│  │  - Switch traffic to new container (zero-downtime)         │ │
│  │  - Terminate old container                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions Workflow

### Workflow Configuration

**File**: `.github/workflows/ml-pipeline.yml`

```yaml
name: ML Pipeline Training

on:
  push:
    branches:
      - main
    paths:
      - 'ml-pipeline/**'
      - '.github/workflows/ml-pipeline.yml'
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:      # Manual trigger

jobs:
  train:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          lfs: true  # Pull Git LFS files
      
      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('ml-pipeline/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r ml-pipeline/requirements.txt
      
      - name: Run ML Pipeline
        run: python ml-pipeline/train.py
        env:
          PYTHONUNBUFFERED: 1
      
      - name: Upload training logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: training-logs-${{ github.run_number }}
          path: ml-pipeline/logs/
          retention-days: 90
      
      - name: Upload evaluation reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-reports-${{ github.run_number }}
          path: ml-pipeline/reports/
          retention-days: 90
      
      - name: Commit trained models
        if: success()
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add ml-pipeline/models/trained/
          git commit -m "Update trained models (run ${{ github.run_number }}) [skip ci]" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Key Features**:
- **Triggers**: Push to main, daily schedule, manual dispatch
- **Timeout**: 10 minutes (fail if training takes too long)
- **Caching**: Cache pip dependencies for faster runs
- **Artifacts**: Upload logs and reports (90-day retention)
- **Model Commit**: Commit models to Git (skip CI to avoid infinite loop)

---

## Render Deployment Configuration

### Render Service Configuration

**File**: `render.yaml` (Render Blueprint)

```yaml
services:
  - type: web
    name: skill2hire
    env: docker
    repo: https://github.com/<username>/skill2hire
    branch: main
    dockerfilePath: ./Dockerfile
    dockerContext: .
    region: oregon
    plan: free
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
      - key: MODEL_DIR
        value: /app/ml-pipeline/models/trained
      - key: LOG_LEVEL
        value: INFO
    autoDeploy: true
```

**Key Features**:
- **Auto-Deploy**: Deploy on push to main branch
- **Health Check**: Validate deployment with `/health` endpoint
- **Environment Variables**: Configure runtime behavior
- **Free Plan**: Use Render Free tier

---

### Dockerfile

**File**: `Dockerfile`

```dockerfile
# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Initialize Git LFS
RUN git lfs install

# Copy requirements files
COPY ml-pipeline/requirements.txt ml-pipeline/requirements.txt
COPY backend/requirements.txt backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ml-pipeline/requirements.txt && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/app/ml-pipeline/models/trained

# Run Backend (Flask)
CMD ["python", "backend/wsgi.py"]
```

**Key Features**:
- **Git LFS**: Install Git LFS to pull model files
- **Multi-Stage**: Install dependencies before copying code (layer caching)
- **Models Included**: Models copied from repository into image
- **Backend Startup**: Backend loads models at startup

---

## Deployment Strategies

### Current Strategy: Full Redeploy

**Process**:
1. New models committed to Git
2. Git push triggers Render deployment
3. Render builds new Docker image (includes new models)
4. Render deploys new container
5. Render performs health check
6. Render switches traffic to new container (zero-downtime)
7. Old container terminated

**Deployment Time**: 5-10 minutes

**Downtime**: Zero (Render handles blue-green deployment)

**Rollback**: Git revert + redeploy (~5-10 minutes)

**Pros**:
- Simple (no additional infrastructure)
- Zero-downtime (Render handles blue-green)
- Complete deployment (code + models)

**Cons**:
- Slow (5-10 minutes)
- Full redeploy for model-only changes

---

### Alternative Strategy: Hot-Reload (Future)

**Process**:
1. New models committed to Git
2. Backend detects new models (file watcher or API endpoint)
3. Backend reloads models without restarting
4. New models available for inference

**Deployment Time**: < 1 minute

**Downtime**: Zero (in-process reload)

**Rollback**: Reload previous models

**Pros**:
- Fast (< 1 minute)
- No full redeploy needed
- Zero-downtime

**Cons**:
- More complex (requires file watcher or API endpoint)
- Potential memory issues (old models not garbage collected)
- Not implemented in current design

**When to Implement**: If model updates become frequent (> 1/day)

---

## Deployment Procedures

### Standard Deployment (Automatic)

**Trigger**: Push to main branch or daily schedule

**Process**:
1. Developer pushes code to main branch (or scheduled trigger fires)
2. GitHub Actions workflow starts automatically
3. Training runs and models are generated
4. Models committed to Git
5. Render detects Git push and starts deployment
6. Render builds Docker image and deploys
7. Health check validates deployment
8. Traffic switched to new container

**Duration**: ~10-15 minutes (training + deployment)

**Monitoring**: GitHub Actions UI + Render dashboard

**Notifications**: Email on failure (GitHub Actions)

---

### Manual Deployment

**Trigger**: Manual workflow dispatch

**Process**:
1. Navigate to GitHub Actions → ML Pipeline Training workflow
2. Click "Run workflow" button
3. Select branch (main)
4. Click "Run workflow"
5. Follow standard deployment process

**Use Case**: On-demand training (e.g., after manual data changes)

---

### Rollback Procedure

**Scenario**: New deployment causes issues

**Process**:
1. Identify problematic commit (Git log)
2. Revert commit: `git revert <commit-hash>`
3. Push revert: `git push origin main`
4. Render auto-deploys reverted version
5. Validate rollback with health check

**Duration**: ~5-10 minutes

**Alternative**: Render dashboard → Rollback to previous deployment

---

### Emergency Rollback

**Scenario**: Production is down, need immediate rollback

**Process**:
1. Navigate to Render dashboard
2. Select skill2hire service
3. Click "Manual Deploy" → Select previous deployment
4. Click "Deploy"
5. Render redeploys previous version

**Duration**: ~2-3 minutes (no build, just redeploy)

---

## Deployment Validation

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "models": [
    "random_forest",
    "gradient_boosting",
    "logistic_regression",
    "voting_classifier"
  ],
  "version": "v1"
}
```

**Validation Criteria**:
- HTTP 200 status code
- `status: "healthy"`
- `models_loaded: true`
- All 4 models present

**Failure Action**: Render aborts deployment, keeps old container running

---

### Smoke Tests

**Manual Smoke Tests** (after deployment):

1. **Health Check**: `curl https://skill2hire.onrender.com/health`
2. **Prediction Test**: Submit test prediction request
3. **Model Version Check**: Verify new model version is loaded
4. **Frontend Test**: Load frontend and verify UI renders

**Automated Smoke Tests** (future):
- Add smoke test step to GitHub Actions workflow
- Run after Render deployment completes
- Fail workflow if smoke tests fail

---

## Deployment Monitoring

### GitHub Actions Monitoring

**Metrics**:
- Workflow success/failure rate
- Training duration
- Model performance metrics (from artifacts)

**Monitoring Tools**:
- GitHub Actions UI (workflow runs)
- GitHub Actions API (programmatic access)
- Email notifications (on failure)

**Alerts**:
- Workflow failure (email)
- Workflow timeout (> 10 minutes)

---

### Render Monitoring

**Metrics**:
- Deployment success/failure rate
- Deployment duration
- Container health status
- Container resource usage (CPU, RAM)

**Monitoring Tools**:
- Render dashboard (web UI)
- Render API (programmatic access)
- Render logs (container logs)

**Alerts**:
- Deployment failure (email)
- Health check failure (email)
- Container crash (email)

---

## Deployment Security

### Secrets Management

**GitHub Secrets**:
- `DOCKER_HUB_USERNAME`: Docker Hub username
- `DOCKER_HUB_TOKEN`: Docker Hub access token
- `RENDER_API_KEY`: Render API key (if needed)

**Access Control**: Repository secrets accessible only to GitHub Actions workflows

**Rotation**: Manual rotation (no automatic rotation)

---

### Deployment Authorization

**GitHub Actions**:
- Only main branch triggers deployment
- Only repository collaborators can push to main
- Branch protection rules enforce code review (optional)

**Render**:
- Only authorized GitHub repository can trigger deployment
- Render API key required for programmatic deployments

---

## Deployment Troubleshooting

### Common Issues

#### Issue 1: Training Failure

**Symptoms**: GitHub Actions workflow fails during training

**Causes**:
- Data generation failure
- Model training failure
- Dependency issues

**Resolution**:
1. Check GitHub Actions logs
2. Identify error message
3. Fix code issue
4. Push fix to main branch
5. Workflow re-runs automatically

---

#### Issue 2: Model Commit Failure

**Symptoms**: Models not committed to Git

**Causes**:
- Git LFS quota exceeded
- Git authentication failure
- No changes to commit

**Resolution**:
1. Check GitHub Actions logs for Git errors
2. Verify Git LFS quota (GitHub settings)
3. Verify GITHUB_TOKEN permissions
4. Manually commit models if needed

---

#### Issue 3: Render Deployment Failure

**Symptoms**: Render deployment fails

**Causes**:
- Docker build failure
- Health check failure
- Resource limits exceeded

**Resolution**:
1. Check Render logs for error message
2. Verify Dockerfile syntax
3. Verify health check endpoint
4. Check resource usage (RAM, CPU)
5. Rollback to previous deployment if needed

---

#### Issue 4: Models Not Loaded

**Symptoms**: Backend reports models not loaded

**Causes**:
- Git LFS files not pulled
- Model files corrupted
- Incorrect MODEL_DIR path

**Resolution**:
1. Check Render logs for model loading errors
2. Verify Git LFS is installed in Dockerfile
3. Verify MODEL_DIR environment variable
4. Manually verify model files exist in container

---

## Deployment Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | Current |
|--------|--------|---------|
| Training Duration | < 1 minute | ~45 seconds |
| Deployment Duration | < 10 minutes | ~7 minutes |
| Deployment Success Rate | > 95% | TBD |
| Rollback Time | < 5 minutes | ~3 minutes |
| Zero-Downtime Deployments | 100% | 100% (Render) |

---

## Deployment Roadmap

### Current State (v1.0)

- ✅ Automatic training on push + daily schedule
- ✅ Model commit to Git
- ✅ Automatic Render deployment
- ✅ Zero-downtime deployments
- ✅ Health check validation
- ✅ Artifact storage (logs, metrics)

### Future Enhancements

**Phase 2** (if needed):
- [ ] Hot-reload models (no full redeploy)
- [ ] Automated smoke tests
- [ ] Deployment notifications (Slack, Teams)
- [ ] Model performance monitoring (drift detection)

**Phase 3** (if needed):
- [ ] Staging environment
- [ ] Canary deployments
- [ ] A/B testing (multiple model versions)
- [ ] Model registry (MLflow)

---

## Document Control

- **Version**: 1.0
- **Date**: 2026-05-05
- **Status**: Draft
- **Created By**: AI-DLC Infrastructure Design

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-05 | AI-DLC | Initial deployment architecture document |
