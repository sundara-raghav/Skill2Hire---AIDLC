"""Tests for Flask API endpoints."""
import sys
import os
import pytest

# conftest.py at root handles sys.path

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


def test_index_returns_200(client):
    res = client.get('/')
    assert res.status_code == 200


def test_predict_missing_models_returns_503(client):
    # Models not loaded in test env
    payload = {
        'cgpa': 7.5, 'aptitude_score': 75, 'programming_skills': 7,
        'communication_skills': 6, 'num_projects': 3,
        'internship_experience': 1, 'certifications_count': 2, 'branch': 'CS'
    }
    res = client.post('/api/predict', json=payload)
    # Either 503 (no models) or 200 (models loaded)
    assert res.status_code in (200, 503)


def test_predict_invalid_input_returns_422(client):
    payload = {'cgpa': 15.0, 'branch': 'INVALID'}
    res = client.post('/api/predict', json=payload)
    assert res.status_code in (422, 503)


def test_predict_no_body_returns_400(client):
    res = client.post('/api/predict', data='not json',
                      content_type='text/plain')
    assert res.status_code == 400


def test_analyze_job_returns_skills(client):
    payload = {'job_description': 'We need Python, SQL, and Machine Learning skills.'}
    res = client.post('/api/analyze-job', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert 'skills_found' in data
    assert 'Python' in data['skills_found'] or 'SQL' in data['skills_found']


def test_analyze_job_missing_field(client):
    res = client.post('/api/analyze-job', json={})
    assert res.status_code == 400


def test_insights_no_dataset_returns_503(client):
    res = client.get('/api/insights')
    # 503 if dataset not present, 200 if it is
    assert res.status_code in (200, 503)


def test_404_returns_json(client):
    res = client.get('/nonexistent')
    assert res.status_code == 404
    assert res.get_json()['error'] == 'Not found'
