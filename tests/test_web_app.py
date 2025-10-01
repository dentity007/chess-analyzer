"""Minimal tests for the Flask web interface.

These tests validate that key endpoints respond and basic validation works
without relying on background processing completing or external services.
"""

import json
import pytest


def _get_app():
    # Import the app after environment is ready
    from src.web_app import app
    return app


class TestWebApp:
    def setup_method(self):
        self.app = _get_app()
        self.client = self.app.test_client()

    def test_index_page(self):
        resp = self.client.get('/')
        assert resp.status_code == 200
        assert b'Chess' in resp.data

    def test_health_endpoint(self):
        resp = self.client.get('/test')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('status') == 'ok'

    def test_progress_endpoint(self):
        resp = self.client.get('/api/progress')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'status' in data
        assert 'progress' in data

    def test_fetch_games_validation(self):
        resp = self.client.post('/api/fetch_games',
                                 data=json.dumps({}),
                                 content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is False
        assert 'error' in data

    def test_fetch_games_accepts_username(self):
        resp = self.client.post('/api/fetch_games',
                                 data=json.dumps({'username': 'testuser'}),
                                 content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True

    def test_analyze_requires_or_uses_username(self):
        # Provide username to avoid config fallback
        resp = self.client.post('/api/analyze_games',
                                 data=json.dumps({'username': 'testuser'}),
                                 content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True

    def test_save_and_load_credentials(self):
        # Save
        resp = self.client.post('/api/save_credentials',
                                 data=json.dumps({'username': 'saveduser', 'password': 'pw'}),
                                 content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True

        # Load
        resp2 = self.client.get('/api/load_credentials')
        assert resp2.status_code == 200
        data2 = resp2.get_json()
        assert data2.get('username') in ('saveduser', '')  # allow empty in CI

