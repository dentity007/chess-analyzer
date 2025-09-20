"""Database models and operations for Chess Analyzer."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class ChessDatabase:
    """SQLite database for storing chess games and analysis."""

    def __init__(self, db_path: str = "chess_games.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.conn = None
        self._create_tables()

    def _get_connection(self):
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self.conn

    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                pgn TEXT NOT NULL,
                date INTEGER,  -- Unix timestamp
                result TEXT,   -- e.g., "1-0", "0-1", "1/2-1/2"
                white_username TEXT,
                black_username TEXT,
                time_control TEXT,
                end_time INTEGER,
                created_at REAL DEFAULT (datetime('now'))
            )
        ''')

        # Analysis cache table for storing engine evaluations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                game_id TEXT,
                move_number INTEGER,
                fen TEXT,
                evaluation REAL,  -- Centipawn score
                best_move TEXT,
                created_at REAL DEFAULT (datetime('now')),
                PRIMARY KEY (game_id, move_number)
            )
        ''')

        conn.commit()

    def insert_game(self, game_data: Dict):
        """Insert a game into the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO games
            (game_id, pgn, date, result, white_username, black_username, time_control, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_data.get('url', '').split('/')[-1],  # Extract game ID from URL
            game_data.get('pgn', ''),
            game_data.get('end_time', 0),
            game_data.get('result', ''),
            game_data.get('white', {}).get('username', ''),
            game_data.get('black', {}).get('username', ''),
            game_data.get('time_control', ''),
            game_data.get('end_time', 0)
        ))

        conn.commit()

    def insert_games_batch(self, games: List[Dict]):
        """Insert multiple games into the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        games_data = []
        for game in games:
            games_data.append((
                game.get('url', '').split('/')[-1],
                game.get('pgn', ''),
                game.get('end_time', 0),
                game.get('result', ''),
                game.get('white', {}).get('username', ''),
                game.get('black', {}).get('username', ''),
                game.get('time_control', ''),
                game.get('end_time', 0)
            ))

        cursor.executemany('''
            INSERT OR REPLACE INTO games
            (game_id, pgn, date, result, white_username, black_username, time_control, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', games_data)

        conn.commit()

    def get_games_by_username(self, username: str, limit: Optional[int] = None) -> List[Dict]:
        """Get games for a specific username."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT * FROM games
            WHERE white_username = ? OR black_username = ?
            ORDER BY date DESC
        '''
        params = [username, username]

        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_game_by_id(self, game_id: str) -> Optional[Dict]:
        """Get a specific game by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM games WHERE game_id = ?', (game_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_games_by_date_range(self, username: str, start_date: datetime,
                               end_date: datetime) -> List[Dict]:
        """Get games within a date range for a username."""
        conn = self._get_connection()
        cursor = conn.cursor()

        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())

        cursor.execute('''
            SELECT * FROM games
            WHERE (white_username = ? OR black_username = ?)
            AND date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', (username, username, start_ts, end_ts))

        return [dict(row) for row in cursor.fetchall()]

    def cache_analysis(self, game_id: str, move_number: int, fen: str,
                      evaluation: float, best_move: str):
        """Cache analysis results for a position."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO analysis_cache
            (game_id, move_number, fen, evaluation, best_move)
            VALUES (?, ?, ?, ?, ?)
        ''', (game_id, move_number, fen, evaluation, best_move))

        conn.commit()

    def get_cached_analysis(self, game_id: str, move_number: int) -> Optional[Dict]:
        """Get cached analysis for a position."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM analysis_cache
            WHERE game_id = ? AND move_number = ?
        ''', (game_id, move_number))

        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Ensure connection is closed on deletion."""
        self.close()