"""
Flask Application — Skill2Hire Placement Prediction API
"""

import os
import sys
import pickle
import json
import re
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except ImportError:
    supabase = None

# Add ml-pipeline to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ml-pipeline'))

from utils.skill_dictionary import SKILL_CATEGORIES, get_all_skills

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


# Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response


# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ── Model Loading ──────────────────────────────────────────────────────────────

MODELS = {}
SCALER = None
ENCODER = None
ALL_SKILLS = get_all_skills()

VALID_BRANCHES = ['CS', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Chemical', 'Other']
NUMERIC_FEATURES = ['cgpa', 'aptitude_score', 'programming_skills',
                    'communication_skills', 'num_projects', 'certifications_count']
CATEGORICAL_FEATURES = ['branch']


def load_models():
    """Load latest trained models and preprocessing artifacts."""
    global SCALER, ENCODER

    model_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'ml-pipeline', 'models', 'trained'
    )

    if not os.path.exists(model_dir):
        logger.warning(f"Model directory not found: {model_dir}")
        return

    # Find latest version
    pkl_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
    if not pkl_files:
        logger.warning("No model files found. Run train.py first.")
        return

    versions = set()
    for f in pkl_files:
        parts = f.rsplit('_', 1)
        if len(parts) == 2:
            versions.add(parts[1].replace('.pkl', ''))
    latest = sorted(versions, key=lambda v: int(v[1:]))[-1] if versions else 'v1'

    model_names = ['random_forest', 'gradient_boosting', 'logistic_regression', 'voting_classifier']
    for name in model_names:
        path = os.path.join(model_dir, f'{name}_{latest}.pkl')
        if os.path.exists(path):
            with open(path, 'rb') as f:
                MODELS[name] = pickle.load(f)
            logger.info(f"Loaded {name} ({latest})")

    scaler_path = os.path.join(model_dir, f'scaler_{latest}.pkl')
    encoder_path = os.path.join(model_dir, f'encoder_{latest}.pkl')

    if os.path.exists(scaler_path):
        with open(scaler_path, 'rb') as f:
            SCALER = pickle.load(f)
        logger.info(f"Loaded scaler ({latest})")

    if os.path.exists(encoder_path):
        with open(encoder_path, 'rb') as f:
            ENCODER = pickle.load(f)
        logger.info(f"Loaded encoder ({latest})")


# ── Input Validation ───────────────────────────────────────────────────────────

def validate_input(data):
    """Validate and sanitize prediction input."""
    errors = []

    try:
        cgpa = float(data.get('cgpa', -1))
        if not (0.0 <= cgpa <= 10.0):
            errors.append("CGPA must be between 0.0 and 10.0")
    except (TypeError, ValueError):
        errors.append("CGPA must be a number")
        cgpa = None

    try:
        aptitude = int(float(data.get('aptitude_score', -1)))
        if not (0 <= aptitude <= 100):
            errors.append("Aptitude score must be between 0 and 100")
    except (TypeError, ValueError):
        errors.append("Aptitude score must be a number")
        aptitude = None

    try:
        prog = int(float(data.get('programming_skills', 0)))
        if not (1 <= prog <= 10):
            errors.append("Programming skills must be between 1 and 10")
    except (TypeError, ValueError):
        errors.append("Programming skills must be a number")
        prog = None

    try:
        comm = int(float(data.get('communication_skills', 0)))
        if not (1 <= comm <= 10):
            errors.append("Communication skills must be between 1 and 10")
    except (TypeError, ValueError):
        errors.append("Communication skills must be a number")
        comm = None

    try:
        projects = int(float(data.get('num_projects', -1)))
        if not (0 <= projects <= 10):
            errors.append("Number of projects must be between 0 and 10")
    except (TypeError, ValueError):
        errors.append("Number of projects must be a number")
        projects = None

    internship = 1 if str(data.get('internship_experience', '0')).lower() in ('1', 'true', 'yes') else 0

    try:
        certs = int(float(data.get('certifications_count', -1)))
        if not (0 <= certs <= 10):
            errors.append("Certifications count must be between 0 and 10")
    except (TypeError, ValueError):
        errors.append("Certifications count must be a number")
        certs = None

    branch = str(data.get('branch', '')).strip()
    if branch not in VALID_BRANCHES:
        errors.append(f"Branch must be one of {VALID_BRANCHES}")

    return errors, {
        'cgpa': cgpa, 'aptitude_score': aptitude,
        'programming_skills': prog, 'communication_skills': comm,
        'num_projects': projects, 'internship_experience': internship,
        'certifications_count': certs, 'branch': branch
    }


# ── Feature Preparation ────────────────────────────────────────────────────────

def prepare_features(profile):
    """Preprocess and engineer features for inference."""
    df = pd.DataFrame([profile])

    # Scale numeric features
    df[NUMERIC_FEATURES] = SCALER.transform(df[NUMERIC_FEATURES])

    # Encode branch
    branch_encoded = ENCODER.transform(df[CATEGORICAL_FEATURES])
    branch_cols = [f'branch_{c}' for c in ENCODER.categories_[0]]
    df_encoded = pd.concat([
        df.drop(CATEGORICAL_FEATURES, axis=1).reset_index(drop=True),
        pd.DataFrame(branch_encoded, columns=branch_cols)
    ], axis=1)

    # Feature engineering
    df_encoded['Total_Skills_Score'] = (
        df_encoded['programming_skills'] + df_encoded['communication_skills']
    )
    df_encoded['Experience_Score'] = (
        df_encoded['num_projects'] * 0.4 + df_encoded['internship_experience'] * 0.6
    )
    df_encoded['CGPA_Project_Score'] = (
        df_encoded['cgpa'] * df_encoded['num_projects']
    )

    return df_encoded


# ── NLP Skill Extraction ───────────────────────────────────────────────────────

def extract_skills_from_text(text):
    """Extract skills from job description using keyword matching."""
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def generate_skill_gap(user_profile, job_skills):
    """Generate skill gap suggestions."""
    suggestions = []
    user_prog = user_profile.get('programming_skills', 5)
    user_comm = user_profile.get('communication_skills', 5)
    user_projects = user_profile.get('num_projects', 0)
    user_internship = user_profile.get('internship_experience', 0)
    user_certs = user_profile.get('certifications_count', 0)

    tech_skills_in_jd = [s for s in job_skills if s in SKILL_CATEGORIES.get('technical', [])]
    if tech_skills_in_jd and user_prog < 7:
        suggestions.append(f"Improve technical skills: {', '.join(tech_skills_in_jd[:3])}")

    if user_comm < 6:
        suggestions.append("Enhance communication and presentation skills")

    if user_projects < 2:
        suggestions.append("Build more projects to strengthen your portfolio")

    if not user_internship:
        suggestions.append("Gain internship experience for practical exposure")

    if user_certs < 2 and tech_skills_in_jd:
        suggestions.append(f"Get certified in: {', '.join(tech_skills_in_jd[:2])}")

    if not suggestions:
        suggestions.append("Strong profile! Keep updating your skills regularly.")

    return suggestions


# ── Supabase Helpers ───────────────────────────────────────────────────────────

def log_prediction(payload: dict, result: dict):
    """Log a prediction to Supabase (non-blocking, best-effort)."""
    if supabase is None:
        return
    try:
        record = {
            'name': payload.get('name', ''),
            'cgpa': payload.get('cgpa'),
            'aptitude_score': payload.get('aptitude_score'),
            'programming_skills': payload.get('programming_skills'),
            'communication_skills': payload.get('communication_skills'),
            'num_projects': payload.get('num_projects'),
            'internship_experience': payload.get('internship_experience'),
            'certifications_count': payload.get('certifications_count'),
            'branch': payload.get('branch', ''),
            'placement_probability': result.get('placement_probability'),
            'confidence': result.get('confidence'),
            'model_predictions': json.dumps(result.get('model_predictions', {})),
            'job_skills_found': json.dumps(result.get('job_skills_found', [])),
            'skill_gap_suggestions': json.dumps(result.get('skill_gap_suggestions', [])),
            'created_at': datetime.utcnow().isoformat(),
        }
        supabase.table('predictions').insert(record).execute()
    except Exception as e:
        logger.warning(f"Supabase log_prediction failed (non-critical): {e}")


def log_job_analysis(job_desc_snippet: str, result: dict):
    """Log a job analysis to Supabase (non-blocking, best-effort)."""
    if supabase is None:
        return
    try:
        record = {
            'job_description_snippet': job_desc_snippet[:500],
            'skills_found': json.dumps(result.get('skills_found', [])),
            'total_skills': result.get('total_skills', 0),
            'created_at': datetime.utcnow().isoformat(),
        }
        supabase.table('job_analyses').insert(record).execute()
    except Exception as e:
        logger.warning(f"Supabase log_job_analysis failed (non-critical): {e}")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    supabase_status = 'connected' if supabase else 'offline'
    return render_template('index.html', supabase_status=supabase_status)


@app.route('/api/predict', methods=['POST'])
@limiter.limit("30 per minute")
def predict():
    """Generate placement prediction from student profile."""
    if not MODELS or SCALER is None or ENCODER is None:
        return jsonify({'error': 'Models not loaded. Run train.py first.'}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    errors, profile = validate_input(data)
    if errors:
        return jsonify({'errors': errors}), 422

    try:
        features = prepare_features(profile)
        predictions = {}
        probabilities = {}

        model_order = ['random_forest', 'gradient_boosting', 'logistic_regression', 'voting_classifier']
        for name in model_order:
            if name in MODELS:
                prob = float(MODELS[name].predict_proba(features)[0][1])
                predictions[name] = round(prob * 100, 1)
                probabilities[name] = prob

        ensemble_prob = probabilities.get(
            'voting_classifier',
            np.mean(list(probabilities.values())) if probabilities else 0.5
        )
        placement_probability = round(float(ensemble_prob) * 100, 1)

        # Skill gap analysis
        job_description = str(data.get('job_description', ''))
        job_skills = extract_skills_from_text(job_description) if job_description else []
        suggestions = generate_skill_gap(profile, job_skills)

        result = {
            'placement_probability': placement_probability,
            'confidence': round(abs(ensemble_prob - 0.5) * 200, 1),
            'model_predictions': predictions,
            'job_skills_found': job_skills,
            'skill_gap_suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }

        # Log to Supabase (best-effort)
        log_prediction(data, result)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({'error': 'Prediction failed. Please try again.'}), 500


@app.route('/api/analyze-job', methods=['POST'])
@limiter.limit("30 per minute")
def analyze_job():
    """Extract skills from a job description."""
    data = request.get_json(silent=True)
    if not data or 'job_description' not in data:
        return jsonify({'error': 'job_description is required'}), 400

    text = str(data['job_description'])[:5000]  # cap input length
    skills = extract_skills_from_text(text)

    categorized = {}
    for skill in skills:
        for cat, cat_skills in SKILL_CATEGORIES.items():
            if skill in cat_skills:
                categorized.setdefault(cat, []).append(skill)

    result = {
        'skills_found': skills,
        'categorized_skills': categorized,
        'total_skills': len(skills)
    }

    # Log to Supabase (best-effort)
    log_job_analysis(text[:200], result)

    return jsonify(result)


@app.route('/api/insights', methods=['GET'])
@limiter.limit("60 per minute")
def insights():
    """Return college-wide analytics from training dataset."""
    dataset_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'ml-pipeline', 'data', 'training_dataset.csv'
    )

    if not os.path.exists(dataset_path):
        # Try alternate path (when running from repo root)
        alt_path = os.path.join('ml-pipeline', 'data', 'training_dataset.csv')
        if os.path.exists(alt_path):
            dataset_path = alt_path
        else:
            return jsonify({'error': 'Dataset not found. Run train.py first.'}), 503

    try:
        df = pd.read_csv(dataset_path)
        branch_filter = request.args.get('branch')
        if branch_filter and branch_filter in VALID_BRANCHES:
            df = df[df['branch'] == branch_filter]

        placement_by_branch = (
            df.groupby('branch')['placement_status']
            .agg(['mean', 'count'])
            .reset_index()
            .rename(columns={'mean': 'placement_rate', 'count': 'total'})
        )
        placement_by_branch['placement_rate'] = (
            placement_by_branch['placement_rate'] * 100
        ).round(1)

        return jsonify({
            'total_students': len(df),
            'overall_placement_rate': round(df['placement_status'].mean() * 100, 1),
            'avg_cgpa': round(df['cgpa'].mean(), 2),
            'placement_by_branch': placement_by_branch.to_dict(orient='records'),
            'avg_cgpa_placed': round(df[df['placement_status'] == 1]['cgpa'].mean(), 2),
            'avg_cgpa_not_placed': round(df[df['placement_status'] == 0]['cgpa'].mean(), 2),
            'avg_programming_skills': round(df['programming_skills'].mean(), 2),
            'internship_placement_rate': round(
                df[df['internship_experience'] == 1]['placement_status'].mean() * 100, 1
            ),
        })

    except Exception as e:
        logger.error(f"Insights error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load insights.'}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(429)
def rate_limited(e):
    return jsonify({'error': 'Rate limit exceeded. Please slow down.'}), 429


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    load_models()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
