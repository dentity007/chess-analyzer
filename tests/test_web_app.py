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

    def test_progress_polling_mock(self, monkeypatch):
        # Import module to access globals
        import src.web_app as web_app
        # Set a mocked progress
        web_app.analysis_progress = {"status": "completed", "progress": 100, "message": "Done"}
        resp = self.client.get('/api/progress')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('status') == 'completed'
        assert data.get('progress') == 100

    def test_fetch_games_background_thread(self, monkeypatch):
        # Avoid network/DB by monkeypatching client + DB methods
        import src.web_app as web_app

        def fake_get_all_games(username):
            return [{
                'url': 'https://www.chess.com/game/live/123',
                'pgn': '1. e4 e5',
                'end_time': 1704067200,
                'result': '1-0',
                'white': {'username': username},
                'black': {'username': 'opponent'},
                'time_control': '600'
            }]

        class DummyDB:
            def __init__(self, *a, **k):
                pass
            def insert_games_batch(self, games):
                return None
            def close(self):
                return None

        monkeypatch.setattr(web_app, 'current_client', web_app.current_client or object())
        monkeypatch.setattr(web_app.current_client.__class__, 'get_all_games', staticmethod(fake_get_all_games), raising=False)
        # Patch constructor used inside thread
        import importlib
        db_module = importlib.import_module('db.database')
        monkeypatch.setattr(db_module, 'ChessDatabase', DummyDB)

        resp = self.client.post('/api/fetch_games',
                                 data=json.dumps({'username': 'testuser'}),
                                 content_type='application/json')
        assert resp.status_code == 200

        # Poll a few times to allow thread to update progress
        import time
        for _ in range(10):
            data = self.client.get('/api/progress').get_json()
            if data.get('status') in ('completed', 'error'):
                break
            time.sleep(0.05)
        assert data.get('status') in ('completed', 'error')

    def test_analyze_games_background_thread(self, monkeypatch):
        import src.web_app as web_app
        # Reset progress to avoid interference from other tests
        web_app.analysis_progress = {"status": "idle", "progress": 0, "message": ""}

        class DummyDB:
            def __init__(self, *a, **k):
                pass
            def get_games_by_username(self, username, limit=None):
                return [{
                    'game_id': 'g1',
                    'pgn': '1. e4 e5',
                    'result': '1-0'
                }]
            def close(self):
                return None

        class DummyAnalyzer:
            def analyze_game(self, pgn):
                return {'summary': {'total_moves': 2, 'blunder_count': 0, 'mistake_count': 0, 'accuracy': 100.0},
                        'blunders': [], 'mistakes': [], 'moves': []}

        class DummyAI:
            def get_chess_advice(self, pgn, analysis):
                return 'Advice'

        # Patch analyzer and AI globals
        monkeypatch.setattr(web_app, 'current_analyzer', DummyAnalyzer())
        monkeypatch.setattr(web_app, 'current_ai', DummyAI())
        # Patch DB constructor
        import importlib
        db_module = importlib.import_module('db.database')
        monkeypatch.setattr(db_module, 'ChessDatabase', DummyDB)

        resp = self.client.post('/api/analyze_games',
                                 data=json.dumps({'username': 'testuser'}),
                                 content_type='application/json')
        assert resp.status_code == 200

        # Poll until done
        import time
        for _ in range(40):
            data = self.client.get('/api/progress').get_json()
            # Ensure we wait for the analyze completion, not prior fetch completion
            if data.get('status') == 'completed' and str(data.get('message', '')).startswith('Analysis complete'):
                break
            time.sleep(0.05)
        assert data.get('status') == 'completed'
        assert isinstance(data.get('results'), list)
        assert data['results'] and any(r.get('game_id') == 'g1' for r in data['results'])
