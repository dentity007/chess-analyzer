"""Chess.com API client for fetching player games and data."""

import time
import requests
from typing import List, Dict, Optional
from datetime import datetime

class ChessComClient:
    """Client for interacting with Chess.com Public API."""

    BASE_URL = "https://api.chess.com/pub"
    REQUEST_DELAY = 1.0  # Delay between requests to avoid rate limiting

    def __init__(self):
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get(self, endpoint: str) -> Dict:
        """Make a GET request to the Chess.com API."""
        self._rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_player_profile(self, username: str) -> Dict:
        """Get player profile information."""
        return self._get(f"/player/{username}")

    def get_player_stats(self, username: str) -> Dict:
        """Get player statistics."""
        return self._get(f"/player/{username}/stats")

    def get_game_archives(self, username: str) -> List[str]:
        """Get list of monthly game archive URLs for a player."""
        data = self._get(f"/player/{username}/games/archives")
        return data['archives']

    def get_games_from_archive(self, archive_url: str) -> List[Dict]:
        """Get all games from a specific monthly archive."""
        self._rate_limit()
        response = requests.get(archive_url)
        response.raise_for_status()
        return response.json()['games']

    def get_all_games(self, username: str, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Dict]:
        """Get all games for a player, optionally filtered by date range."""
        archives = self.get_game_archives(username)
        all_games = []

        for archive_url in archives:
            try:
                games = self.get_games_from_archive(archive_url)
                all_games.extend(games)
            except Exception as e:
                print(f"Warning: Failed to fetch from {archive_url}: {e}")
                continue

        # Filter by date range if provided
        if start_date or end_date:
            filtered_games = []
            for game in all_games:
                game_date = datetime.fromtimestamp(game.get('end_time', 0))
                if start_date and game_date < start_date:
                    continue
                if end_date and game_date > end_date:
                    continue
                filtered_games.append(game)
            return filtered_games

        return all_games

    def get_game_by_id(self, game_id: str) -> Optional[Dict]:
        """Get a specific game by ID."""
        # Chess.com API doesn't have direct game ID lookup in public API
        # This would require parsing from archives or using web scraping
        # For now, return None and implement later if needed
        return None