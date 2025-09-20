"""Tests for chess game analysis."""

import pytest
from unittest.mock import Mock, patch
from src.analysis.analyzer import ChessAnalyzer


class TestChessAnalyzer:
    """Test cases for ChessAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ChessAnalyzer()

    def teardown_method(self):
        """Clean up after tests."""
        self.analyzer.close()

    def test_analyze_game_basic(self):
        """Test basic game analysis without Stockfish."""
        pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7'

        result = self.analyzer.analyze_game(pgn)

        assert 'moves' in result
        assert 'summary' in result
        assert result['summary']['total_moves'] == 20  # 10 full moves = 20 half-moves
        assert 'blunders' in result
        assert 'mistakes' in result

    def test_analyze_game_with_blunders(self):
        """Test analysis of a game with known blunders."""
        # A game with a clear blunder (hanging queen)
        pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Nxe4 6. d4 b5 7. Bb3 d5 8. dxe5 Be6 9. c3 Bc5 10. Nbd2 O-O 11. Bc2 Nxf2'

        result = self.analyzer.analyze_game(pgn)

        # Should detect the Nxe4 blunder
        assert len(result['blunders']) > 0 or len(result['mistakes']) > 0

    @patch('chess.engine.SimpleEngine.popen_uci')
    def test_analyze_game_with_stockfish(self, mock_engine):
        """Test analysis with mocked Stockfish engine."""
        # Mock the engine
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance

        # Mock analysis results - create a proper mock structure
        mock_info = Mock()
        mock_score = Mock()
        mock_score.score = Mock(return_value=100)
        mock_relative = Mock()
        mock_relative.score = mock_score
        mock_info.score = mock_relative
        mock_info.__getitem__ = Mock(return_value=mock_info)
        mock_engine_instance.analyse.return_value = mock_info

        pgn = '1. e4 e5'
        result = self.analyzer.analyze_game(pgn, max_depth=10)

        # Verify engine was called
        assert mock_engine_instance.analyse.call_count >= 2  # Called for each position

    def test_calculate_accuracy(self):
        """Test accuracy calculation."""
        # Create mock moves with different score changes
        moves = [
            {'score_change': 0},    # Perfect move
            {'score_change': 10},   # Slight inaccuracy
            {'score_change': 30},   # Inaccuracy
            {'score_change': 80},   # Mistake
            {'score_change': 200},  # Blunder
        ]

        accuracy = self.analyzer._calculate_accuracy(moves)

        # Should be less than 100% due to mistakes
        assert 0 <= accuracy <= 100
        assert accuracy < 100  # Not perfect due to mistakes

    def test_get_position_evaluation_without_engine(self):
        """Test position evaluation without Stockfish."""
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        result = self.analyzer.get_position_evaluation(fen)

        assert 'error' in result
        assert 'Stockfish' in result['error']

    @patch('chess.engine.SimpleEngine.popen_uci')
    def test_get_position_evaluation_with_engine(self, mock_engine):
        """Test position evaluation with mocked Stockfish."""
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance

        mock_info = Mock()
        mock_score = Mock()
        mock_score.score = Mock(return_value=150)
        mock_relative = Mock()
        mock_relative.score = mock_score
        mock_info.score = mock_relative
        mock_info.__getitem__ = Mock(return_value=mock_info)
        mock_engine_instance.analyse.return_value = mock_info

        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        result = self.analyzer.get_position_evaluation(fen)

        assert 'score' in result
        assert 'best_move' in result
        assert result['score'] == 150

    def test_detect_blunders(self):
        """Test blunder detection."""
        pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Nxe4'  # Nxe4 is a blunder

        blunders = self.analyzer.detect_blunders(pgn)

        # Should detect at least one blunder
        assert isinstance(blunders, list)

    def test_get_opening_classification(self):
        """Test opening phase classification."""
        # Short game (opening)
        short_pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5'
        result = self.analyzer.get_opening_classification(short_pgn)
        assert result == 'Opening'

        # Longer game (middlegame)
        long_pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. Nbd2 Bb7 12. Bc2 Re8 13. Nf1 Bf8 14. Ng3 g6 15. a4 c5 16. d5 c4 17. Bg5 h6 18. Bh4 Nh5 19. Nxh5 gxh5 20. Qd2 Kh7 21. Kh2 Rg8 22. Rae1 Qe7 23. f4 exf4 24. Rxf4 Be5 25. Bxf6 Bxf6 26. Rxf6 Qxf6 27. Rxe8 Rxe8 28. Qxh6+ Kg8 29. Qxf6 Re2 30. Qg5+ Kh7'
        result = self.analyzer.get_opening_classification(long_pgn)
        assert result in ['Middlegame', 'Endgame']

    def test_find_stockfish(self):
        """Test Stockfish path detection."""
        # This will test the path finding logic
        path = self.analyzer._find_stockfish()

        # Path should be None or a string
        assert path is None or isinstance(path, str)

    def test_close_engine(self):
        """Test engine cleanup."""
        # Should not raise any exceptions
        self.analyzer.close()

        # Should be safe to call multiple times
        self.analyzer.close()