"""Tests for AI client."""

import pytest
from unittest.mock import Mock, patch
from src.ai.grok_client import GrokClient


class TestGrokClient:
    """Test cases for GrokClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = GrokClient()

    def teardown_method(self):
        """Clean up after tests."""
        pass

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        client = GrokClient()
        assert client.api_key is None

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = GrokClient(api_key="test_key")
        assert client.api_key == "test_key"

    @patch.dict('os.environ', {'XAI_API_KEY': 'env_test_key'})
    def test_init_with_env_api_key(self):
        """Test initialization with API key from environment."""
        client = GrokClient()
        assert client.api_key == "env_test_key"

    def test_get_chess_advice_without_api_key(self):
        """Test getting advice without API key."""
        analysis_data = {
            'summary': {
                'total_moves': 20,
                'blunder_count': 1,
                'mistake_count': 2,
                'accuracy': 85.0
            },
            'blunders': [{'move_number': 10, 'move': 'e4e5', 'score_change': 300}],
            'mistakes': []
        }

        result = self.client.get_chess_advice("1. e4 e5", analysis_data)

        # Should return fallback advice
        assert isinstance(result, str)
        assert len(result) > 0
        assert "blunder" in result.lower() or "mistake" in result.lower()

    @patch('src.ai.grok_client.requests.post')
    def test_get_chess_advice_with_api_key(self, mock_post):
        """Test getting advice with API key."""
        # Set up client with API key
        self.client.api_key = "test_key"

        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Great game! Keep practicing.'}}]
        }
        mock_post.return_value = mock_response

        analysis_data = {
            'summary': {'total_moves': 20, 'blunder_count': 0, 'mistake_count': 0, 'accuracy': 95.0},
            'blunders': [],
            'mistakes': []
        }

        result = self.client.get_chess_advice("1. e4 e5", analysis_data)

        assert result == "Great game! Keep practicing."
        mock_post.assert_called_once()

    @patch('src.ai.grok_client.requests.post')
    def test_get_chess_advice_api_error(self, mock_post):
        """Test handling API errors."""
        self.client.api_key = "test_key"
        mock_post.side_effect = Exception("API Error")

        analysis_data = {'summary': {'total_moves': 10, 'blunder_count': 0, 'mistake_count': 0, 'accuracy': 90.0}}

        result = self.client.get_chess_advice("1. e4 e5", analysis_data)

        # Should return fallback advice
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_analysis_prompt(self):
        """Test prompt building for analysis."""
        analysis_data = {
            'summary': {
                'total_moves': 20,
                'blunder_count': 1,
                'mistake_count': 2,
                'accuracy': 85.0
            },
            'blunders': [
                {'move_number': 10, 'move': 'e4e5', 'score_change': 300}
            ],
            'mistakes': [
                {'move_number': 15, 'move': 'd5c4', 'score_change': 150}
            ]
        }

        prompt = self.client._build_analysis_prompt("1. e4 e5 2. Nf3", analysis_data)

        assert "PGN:" in prompt
        assert "Game Statistics:" in prompt
        assert "Key Blunders:" in prompt
        assert "Key Mistakes:" in prompt
        assert "Move 10:" in prompt
        assert "move 15:" in prompt

    def test_get_fallback_advice(self):
        """Test fallback advice generation."""
        analysis_data = {
            'summary': {
                'total_moves': 20,
                'blunder_count': 1,
                'mistake_count': 2,
                'accuracy': 85.0
            }
        }

        result = self.client._get_fallback_advice(analysis_data)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "1 blunders" in result
        assert "2 mistakes" in result

    def test_get_position_advice_without_api_key(self):
        """Test position advice without API key."""
        result = self.client.get_position_advice("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        assert isinstance(result, str)
        assert "API" in result or "available" in result

    @patch('src.ai.grok_client.requests.post')
    def test_get_position_advice_with_api_key(self, mock_post):
        """Test position advice with API key."""
        self.client.api_key = "test_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Consider e4 for central control.'}}]
        }
        mock_post.return_value = mock_response

        result = self.client.get_position_advice("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        assert result == "Consider e4 for central control."
        mock_post.assert_called_once()

    @patch('src.ai.grok_client.requests.post')
    def test_get_position_advice_api_error(self, mock_post):
        """Test position advice with API error."""
        self.client.api_key = "test_key"
        mock_post.side_effect = Exception("API Error")

        result = self.client.get_position_advice("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        assert "Error" in result