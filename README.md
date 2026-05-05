# Skill2Hire---AIDLC

# Skill2Hire — AI Placement Prediction

Full-stack AI web app that predicts student placement probability using ensemble ML models, provides skill gap analysis, shows college-wide insights, and logs all predictions to **Supabase**.

## Stack

- **Frontend**: HTML5, CSS3, Vanilla JS, Chart.js
- **Backend**: Python Flask REST API
- **ML**: scikit-learn (Random Forest, Gradient Boosting, Logistic Regression, Voting Classifier)
- **Database**: Supabase (PostgreSQL) — prediction & job analysis logging
- **Deploy**: Docker + Render + GitHub Actions CI/CD

## Project Structure

```
Skill2Hire/
├── ml-pipeline/          # ML training pipeline
│   ├── data/             # Dataset generation, preprocessing, feature engineering
│   ├── models/           # Training, evaluation, saving, reporting
│   ├── utils/            # Logger, validation, skill dictionary
│   ├── tests/            # Unit + integration tests
│   ├── config.py         # All hyperparameters and paths
│   └── train.py          # Main training script
├── backend/              # Flask web application
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/index.html
│   ├── app.py            # Flask app + API endpoints + Supabase logging
│   ├── wsgi.py           # Gunicorn entry point
│   └── requirements.txt
├── .github/
│   └── workflows/ml-pipeline.yml   # CI/CD
├── .env.example          # Environment variable template
├── Dockerfile
├── pytest.ini
└── conftest.py
```

## Quick Start

### 1. Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r ml-pipeline/requirements.txt
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Supabase credentials
```

### 3. Train Models

```bash
python ml-pipeline/train.py
# Custom params:
python ml-pipeline/train.py --size 1000 --seed 42
```

Outputs to `ml-pipeline/models/trained/` and `ml-pipeline/reports/`.

### 4. Run Web App

```bash
cd backend
python app.py
# Open http://localhost:5000
```

### 5. Run Tests

```bash
pytest
# With coverage:
pytest --cov=ml-pipeline --cov=backend
```

### 6. Docker

```bash
# Build
docker build -t skill2hire .

# Run (models must be trained first)
docker run --env-file .env -p 5000:5000 skill2hire
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/publishable key |
| `FLASK_ENV` | `development` or `production` |
| `PORT` | Server port (default: 5000) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Placement prediction + skill gap + Supabase log |
| POST | `/api/analyze-job` | Extract skills from job description + Supabase log |
| GET | `/api/insights` | College-wide analytics |

### POST /api/predict

```json
{
  "cgpa": 7.5,
  "aptitude_score": 75,
  "programming_skills": 7,
  "communication_skills": 6,
  "num_projects": 3,
  "internship_experience": 1,
  "certifications_count": 2,
  "branch": "CS",
  "job_description": "Python, SQL, Machine Learning..."
}
```

## Supabase Schema

```sql
-- Run in Supabase SQL Editor
create table predictions (
  id                    bigserial primary key,
  name                  text,
  cgpa                  numeric,
  aptitude_score        int,
  programming_skills    int,
  communication_skills  int,
  num_projects          int,
  internship_experience int,
  certifications_count  int,
  branch                text,
  placement_probability numeric,
  confidence            numeric,
  model_predictions     jsonb,
  job_skills_found      jsonb,
  skill_gap_suggestions jsonb,
  created_at            timestamptz default now()
);

create table job_analyses (
  id                       bigserial primary key,
  job_description_snippet  text,
  skills_found             jsonb,
  total_skills             int,
  created_at               timestamptz default now()
);
```

## Deployment (Render)

1. Push to GitHub
2. Create a Web Service on Render pointing to this repo
3. Set build command: `pip install -r ml-pipeline/requirements.txt -r backend/requirements.txt`
4. Set start command: `gunicorn --bind 0.0.0.0:$PORT backend.wsgi:app`
5. Add environment variables: `SUPABASE_URL`, `SUPABASE_KEY`
6. Add `RENDER_DEPLOY_HOOK_URL` secret to GitHub for auto-deploy

## CI/CD

GitHub Actions runs on every push to `main`:
1. Lint (flake8)
2. Run all tests
3. Train ML models
4. Upload logs/reports as artifacts
5. Commit trained models back to repo
6. Trigger Render deploy

## License

MIT
