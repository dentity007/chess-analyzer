"""Tests for Chess.com API client."""

import pytest
from unittest.mock import Mock, patch
from src.api.client import ChessComClient


class TestChessComClient:
    """Test cases for ChessComClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ChessComClient()

    def teardown_method(self):
        """Clean up after tests."""
        pass

    @patch('src.api.client.requests.get')
    def test_get_player_profile_success(self, mock_get):
        """Test successful player profile retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'username': 'testuser',
            'name': 'Test User',
            'country': 'US'
        }
        mock_get.return_value = mock_response

        result = self.client.get_player_profile('testuser')

        assert result['username'] == 'testuser'
        assert result['name'] == 'Test User'
        mock_get.assert_called_once_with('https://api.chess.com/pub/player/testuser')

    @patch('src.api.client.requests.get')
    def test_get_player_profile_error(self, mock_get):
        """Test player profile retrieval with error."""
        mock_get.side_effect = Exception('API Error')

        with pytest.raises(Exception):
            self.client.get_player_profile('testuser')

    @patch('src.api.client.requests.get')
    def test_get_game_archives_success(self, mock_get):
        """Test successful game archives retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'archives': [
                'https://api.chess.com/pub/player/testuser/games/2024/01',
                'https://api.chess.com/pub/player/testuser/games/2024/02'
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_game_archives('testuser')

        assert len(result) == 2
        assert '2024/01' in result[0]

    @patch('src.api.client.requests.get')
    def test_get_games_from_archive_success(self, mock_get):
        """Test successful games retrieval from archive."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'games': [
                {'pgn': '1. e4 e5', 'result': '1-0'},
                {'pgn': '1. d4 d5', 'result': '0-1'}
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_games_from_archive('https://api.chess.com/pub/player/testuser/games/2024/01')

        assert len(result) == 2
        assert result[0]['result'] == '1-0'

    @patch('src.api.client.requests.get')
    def test_get_all_games_with_date_filter(self, mock_get):
        """Test getting all games with date filtering."""
        # Mock archives response
        archives_response = Mock()
        archives_response.json.return_value = {
            'archives': ['https://api.chess.com/pub/player/testuser/games/2024/01']
        }

        # Mock games response
        games_response = Mock()
        games_response.json.return_value = {
            'games': [
                {'pgn': '1. e4 e5', 'end_time': 1704067200},  # 2024-01-01
                {'pgn': '1. d4 d5', 'end_time': 1706745600}   # 2024-02-01
            ]
        }

        mock_get.side_effect = [archives_response, games_response]

        from datetime import datetime
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 31)

        result = self.client.get_all_games('testuser', start_date, end_date)

        assert len(result) == 1  # Only the first game should be included
        assert result[0]['end_time'] == 1704067200

    def test_rate_limiting(self):
        """Test that rate limiting is enforced."""
        import time

        start_time = time.time()
        self.client._rate_limit()
        self.client._rate_limit()
        end_time = time.time()

        # Should take at least 1 second due to rate limiting
        assert end_time - start_time >= 1.0