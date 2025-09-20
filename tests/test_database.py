"""Tests for database operations."""

import pytest
import os
import tempfile
from src.db.database import ChessDatabase


class TestChessDatabase:
    """Test cases for ChessDatabase."""

    def setup_method(self):
        """Set up test database."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        self.db = ChessDatabase(self.db_file.name)

    def teardown_method(self):
        """Clean up test database."""
        if hasattr(self, 'db'):
            self.db.close()
        if os.path.exists(self.db_file.name):
            os.unlink(self.db_file.name)

    def test_insert_game(self):
        """Test inserting a single game."""
        game_data = {
            'url': 'https://www.chess.com/game/live/12345',
            'pgn': '1. e4 e5 2. Nf3 Nc6',
            'end_time': 1704067200,
            'result': '1-0',
            'white': {'username': 'white_player'},
            'black': {'username': 'black_player'},
            'time_control': '600',
            'end_time': 1704067200
        }

        self.db.insert_game(game_data)

        # Verify game was inserted
        game = self.db.get_game_by_id('12345')
        assert game is not None
        assert game['pgn'] == game_data['pgn']
        assert game['result'] == '1-0'

    def test_insert_games_batch(self):
        """Test inserting multiple games."""
        games_data = [
            {
                'url': 'https://www.chess.com/game/live/1',
                'pgn': '1. e4 e5',
                'end_time': 1704067200,
                'result': '1-0',
                'white': {'username': 'player1'},
                'black': {'username': 'player2'},
                'time_control': '600',
                'end_time': 1704067200
            },
            {
                'url': 'https://www.chess.com/game/live/2',
                'pgn': '1. d4 d5',
                'end_time': 1704153600,
                'result': '0-1',
                'white': {'username': 'player1'},
                'black': {'username': 'player3'},
                'time_control': '600',
                'end_time': 1704153600
            }
        ]

        self.db.insert_games_batch(games_data)

        # Verify games were inserted
        games = self.db.get_games_by_username('player1')
        assert len(games) == 2

    def test_get_games_by_username(self):
        """Test retrieving games by username."""
        # Insert test games
        games_data = [
            {
                'url': 'https://www.chess.com/game/live/1',
                'pgn': '1. e4 e5',
                'end_time': 1704067200,
                'result': '1-0',
                'white': {'username': 'testuser'},
                'black': {'username': 'opponent1'},
                'time_control': '600',
                'end_time': 1704067200
            },
            {
                'url': 'https://www.chess.com/game/live/2',
                'pgn': '1. d4 d5',
                'end_time': 1704153600,
                'result': '0-1',
                'white': {'username': 'opponent2'},
                'black': {'username': 'testuser'},
                'time_control': '600',
                'end_time': 1704153600
            }
        ]

        self.db.insert_games_batch(games_data)

        # Test retrieval
        games = self.db.get_games_by_username('testuser')
        assert len(games) == 2

        # Test limit
        games_limited = self.db.get_games_by_username('testuser', limit=1)
        assert len(games_limited) == 1

    def test_get_games_by_date_range(self):
        """Test retrieving games by date range."""
        from datetime import datetime

        # Insert test games
        games_data = [
            {
                'url': 'https://www.chess.com/game/live/1',
                'pgn': '1. e4 e5',
                'end_time': 1704067200,  # 2024-01-01
                'result': '1-0',
                'white': {'username': 'testuser'},
                'black': {'username': 'opponent'},
                'time_control': '600',
                'end_time': 1704067200
            },
            {
                'url': 'https://www.chess.com/game/live/2',
                'pgn': '1. d4 d5',
                'end_time': 1706745600,  # 2024-02-01
                'result': '0-1',
                'white': {'username': 'testuser'},
                'black': {'username': 'opponent'},
                'time_control': '600',
                'end_time': 1706745600
            }
        ]

        self.db.insert_games_batch(games_data)

        # Test date range
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 31)

        games = self.db.get_games_by_date_range('testuser', start_date, end_date)
        assert len(games) == 0  # No games in this range

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        games = self.db.get_games_by_date_range('testuser', start_date, end_date)
        assert len(games) == 1  # Only the first game

    def test_get_game_by_id(self):
        """Test retrieving a specific game by ID."""
        game_data = {
            'url': 'https://www.chess.com/game/live/12345',
            'pgn': '1. e4 e5 2. Nf3 Nc6',
            'end_time': 1704067200,
            'result': '1-0',
            'white': {'username': 'white_player'},
            'black': {'username': 'black_player'},
            'time_control': '600',
            'end_time': 1704067200
        }

        self.db.insert_game(game_data)

        # Test retrieval
        game = self.db.get_game_by_id('12345')
        assert game is not None
        assert game['game_id'] == '12345'

        # Test non-existent game
        game = self.db.get_game_by_id('99999')
        assert game is None

    def test_cache_analysis(self):
        """Test caching analysis results."""
        game_id = '12345'
        move_number = 5
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        evaluation = -50
        best_move = 'e2e4'

        self.db.cache_analysis(game_id, move_number, fen, evaluation, best_move)

        # Test retrieval
        cached = self.db.get_cached_analysis(game_id, move_number)
        assert cached is not None
        assert cached['evaluation'] == evaluation
        assert cached['best_move'] == best_move

        # Test non-existent cache
        cached = self.db.get_cached_analysis(game_id, 999)
        assert cached is None