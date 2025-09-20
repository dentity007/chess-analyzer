"""Chess game analysis using python-chess and Stockfish."""

import chess
import chess.engine
import chess.pgn
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import StringIO
import os

class ChessAnalyzer:
    """Analyzes chess games using Stockfish engine."""

    def __init__(self, stockfish_path: Optional[str] = None):
        """Initialize analyzer with Stockfish engine."""
        self.engine = None
        self.stockfish_path = stockfish_path or self._find_stockfish()

        if self.stockfish_path and Path(self.stockfish_path).exists():
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            except Exception as e:
                print(f"Warning: Could not load Stockfish engine: {e}")
        else:
            print("Warning: Stockfish not found. Analysis will be limited.")

    def _find_stockfish(self) -> Optional[str]:
        """Try to find Stockfish binary in common locations."""
        common_paths = [
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "/opt/homebrew/bin/stockfish",  # macOS with Homebrew
            "./engines/stockfish",
            "./stockfish"
        ]

        for path in common_paths:
            if Path(path).exists():
                return path

        # Check if it's in PATH
        import shutil
        stockfish = shutil.which("stockfish")
        if stockfish:
            return stockfish

        return None

    def analyze_game(self, pgn: str, max_depth: int = 15) -> Dict:
        """Analyze a complete game and return analysis results."""
        game = chess.pgn.read_game(StringIO(pgn))
        if not game:
            return {"error": "Invalid PGN"}

        board = game.board()
        analysis = {
            "moves": [],
            "blunders": [],
            "mistakes": [],
            "summary": {}
        }

        prev_score = 0
        move_number = 0

        for move in game.mainline_moves():
            move_number += 1
            move_uci = move.uci()

            # Get evaluation before move
            if self.engine:
                try:
                    info = self.engine.analyse(board, chess.engine.Limit(depth=max_depth))
                    score_before = info["score"].relative.score(mate_score=10000)
                except:
                    score_before = 0
            else:
                score_before = 0

            # Make the move
            board.push(move)

            # Get evaluation after move
            if self.engine:
                try:
                    info = self.engine.analyse(board, chess.engine.Limit(depth=max_depth))
                    score_after = info["score"].relative.score(mate_score=10000)
                    best_move = info.get("pv", [None])[0]
                    best_move_uci = best_move.uci() if best_move else None
                except:
                    score_after = 0
                    best_move_uci = None
            else:
                score_after = 0
                best_move_uci = None

            # Calculate score change
            score_change = abs(score_before - score_after) if score_before and score_after else 0

            move_analysis = {
                "move_number": move_number,
                "move": move_uci,
                "score_before": score_before,
                "score_after": score_after,
                "score_change": score_change,
                "best_move": best_move_uci,
                "fen": board.fen()
            }

            analysis["moves"].append(move_analysis)

            # Detect blunders and mistakes
            if score_change >= 200:  # Blunder: >200 centipawns
                analysis["blunders"].append(move_analysis)
            elif score_change >= 100:  # Mistake: >100 centipawns
                analysis["mistakes"].append(move_analysis)

            prev_score = score_after

        # Generate summary
        analysis["summary"] = {
            "total_moves": move_number,
            "blunder_count": len(analysis["blunders"]),
            "mistake_count": len(analysis["mistakes"]),
            "accuracy": self._calculate_accuracy(analysis["moves"])
        }

        return analysis

    def _calculate_accuracy(self, moves: List[Dict]) -> float:
        """Calculate game accuracy based on move evaluations."""
        if not moves:
            return 0.0

        total_moves = len(moves)
        inaccurate_moves = 0

        for move in moves:
            score_change = move.get("score_change", 0)
            if score_change >= 50:  # Consider moves with >50 cp loss as inaccurate
                inaccurate_moves += 1

        accurate_moves = total_moves - inaccurate_moves
        return (accurate_moves / total_moves) * 100 if total_moves > 0 else 0.0

    def get_position_evaluation(self, fen: str, depth: int = 15) -> Dict:
        """Get evaluation for a specific position."""
        if not self.engine:
            return {"error": "Stockfish engine not available"}

        board = chess.Board(fen)
        try:
            info = self.engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info["score"].relative.score(mate_score=10000)
            best_move = info.get("pv", [None])[0]
            
            return {
                "score": score,
                "best_move": best_move.uci() if best_move else None,
                "depth": depth,
                "fen": fen
            }
        except Exception as e:
            return {"error": str(e)}

    def detect_blunders(self, pgn: str) -> List[Dict]:
        """Detect blunders in a game (moves with >200 cp loss)."""
        analysis = self.analyze_game(pgn)
        return analysis.get("blunders", [])

    def get_opening_classification(self, pgn: str) -> str:
        """Classify the opening phase of the game."""
        game = chess.pgn.read_game(StringIO(pgn))
        if not game:
            return "Unknown"

        moves = list(game.mainline_moves())
        
        if len(moves) <= 10:
            return "Opening"
        elif len(moves) <= 30:
            return "Middlegame"
        else:
            return "Endgame"

    def close(self):
        """Close the engine."""
        if self.engine:
            self.engine.quit()
            self.engine = None

    def __del__(self):
        """Ensure engine is closed on deletion."""
        self.close()