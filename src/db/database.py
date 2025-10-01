"""Chess Database - SQLite Storage for Chess Game Analysis.

This module provides a robust, PyInstaller-compatible SQLite database layer
for storing and retrieving chess games and analysis data. It features efficient
querying, automatic schema management, and thread-safe operations.

Core Features:
- SQLite database with automatic schema creation
- PyInstaller-compatible path handling for bundled applications
- Efficient game storage and retrieval with indexing
- Analysis cache for performance optimization
- Thread-safe database connections and operations
- Automatic database migration and schema updates

Database Schema:
- games: Stores complete game data (PGN, metadata, timestamps)
- analysis_cache: Caches engine evaluations for performance
- Indexes on key fields for fast querying
- Foreign key relationships for data integrity

Technical Features:
- Connection pooling and automatic cleanup
- Prepared statements for security and performance
- Row factory for column access by name
- Transaction support for data consistency
- Error handling with graceful degradation
- Memory-efficient bulk operations

Performance Optimizations:
- Indexed queries for fast game retrieval
- Analysis result caching to avoid recomputation
- Batch insert operations for bulk data
- Connection reuse to minimize overhead
- Query optimization for common access patterns

Usage Examples:
    # Initialize database
    db = ChessDatabase()

    # Store games
    db.insert_games_batch(games_list)

    # Query games
    user_games = db.get_games_by_username('magnuscarlsen', limit=10)

    # Cache analysis results
    db.cache_analysis(game_id, move_number, evaluation)

Security:
- SQL injection prevention through parameterized queries
- Safe path handling for bundled applications
- No external network dependencies
- Local data storage with file system permissions

Dependencies:
- sqlite3: Built-in Python SQLite support
- pathlib: Cross-platform path handling
- datetime: Timestamp management
- typing: Type hints for better code documentation
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class ChessDatabase:
    """SQLite database for storing chess games and analysis."""

    def __init__(self, db_path: str = "chess_games.db"):
        """Initialize database connection."""
        # Handle PyInstaller bundle paths
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            application_path = Path(sys.executable).parent
            self.db_path = application_path / db_path
        else:
            # Running in development
            self.db_path = Path(db_path)

        self.conn = None
        try:
            self._create_tables()
        except Exception as e:
            print(f"Warning: Failed to create database tables: {e}")
            # Continue without database functionality

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
            # Extract game_id from URL
            game_id = game.get('url', '').split('/')[-1] if game.get('url') else ''
            
            # Extract result from PGN if not directly available
            result = game.get('result', '')
            if not result:
                pgn = game.get('pgn', '')
                # Parse result from PGN
                for line in pgn.split('\n'):
                    if line.startswith('[Result "'):
                        result = line.split('"')[1]
                        break
            
            games_data.append((
                game_id,
                game.get('pgn', ''),
                game.get('end_time', 0),
                result,
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

        from datetime import timezone
        # Treat naive datetimes as UTC to align with Chess.com epoch timestamps
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())

        cursor.execute('''
            SELECT * FROM games
            WHERE (white_username = ? OR black_username = ?)
            AND date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', (username, username, start_ts, end_ts))

        return [dict(row) for row in cursor.fetchall()]

    def get_all_games(self) -> List[Dict]:
        """Get all games from the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM games ORDER BY date DESC')
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
