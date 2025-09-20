"""Chess.com API client for fetching player games and data.

This module provides a comprehensive client for interacting with the Chess.com Public API.
It supports both anonymous access (for public data) and authenticated access (for future premium features).

Key Features:
- Rate limiting to respect API guidelines
- Local credential storage for authentication
- Comprehensive error handling
- Support for both public and authenticated endpoints

Security Note:
- Credentials are stored locally in config.local.ini (excluded from Git)
- Never commit credential files to version control
- Authentication is optional and mainly for future premium features
"""

import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
import configparser
import os

class ChessComClient:
    """Client for interacting with Chess.com Public API.

    This class handles all communication with Chess.com's public API endpoints.
    It includes built-in rate limiting, credential management, and error handling.

    Attributes:
        BASE_URL (str): Base URL for Chess.com public API
        REQUEST_DELAY (float): Delay between requests in seconds
        username (str): Chess.com username from local config (if available)
        password (str): Chess.com password from local config (if available)
        session (requests.Session): HTTP session for API requests
    """

    BASE_URL = "https://api.chess.com/pub"
    REQUEST_DELAY = 1.0  # Delay between requests to avoid rate limiting

    def __init__(self):
        """Initialize the Chess.com API client.

        Sets up the HTTP session, loads local credentials if available,
        and configures authentication for future premium features.
        """
        self.last_request_time = 0
        self.session = requests.Session()
        self._load_credentials()

    def _load_credentials(self):
        """Load Chess.com credentials from local config file.

        Attempts to read credentials from config.local.ini in the project root.
        This file is automatically excluded from Git commits for security.

        Expected config format:
            [chess_com]
            username = your_username
            password = your_password

        Note: Chess.com's public API doesn't require authentication for most operations.
        Credentials are stored for future premium features and testing purposes.
        """
        self.username = None
        self.password = None

        # Look for config file in project root (two levels up from this module)
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.local.ini')

        if os.path.exists(config_path):
            try:
                config = configparser.ConfigParser()
                config.read(config_path)

                if 'chess_com' in config:
                    self.username = config['chess_com'].get('username')
                    self.password = config['chess_com'].get('password')

                    if self.username and self.password:
                        print(f"✓ Loaded Chess.com credentials for user: {self.username}")
                        # Set up authenticated session if credentials are available
                        self._setup_authenticated_session()
                    else:
                        print("⚠ Chess.com credentials found but incomplete")
            except Exception as e:
                print(f"⚠ Failed to load Chess.com credentials: {e}")
        else:
            print("ℹ No local config file found. Using public API only.")

    def _setup_authenticated_session(self):
        """Set up authenticated session for premium features.

        Note: Chess.com Public API doesn't typically require authentication for basic operations.
        This method prepares the client for future premium features that may require authentication.

        Current Status: Authentication setup is prepared but not actively used since
        the public API endpoints work without authentication.
        """
        if not self.username or not self.password:
            return

        try:
            # Note: Chess.com Public API doesn't typically require authentication
            # This is mainly for future-proofing if premium features are added
            print("ℹ Chess.com credentials loaded (public API doesn't require auth)")
        except Exception as e:
            print(f"⚠ Failed to set up authenticated session: {e}")

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get(self, endpoint: str, use_auth: bool = False) -> Dict:
        """Make a GET request to the Chess.com API."""
        self._rate_limit()

        session = self.session if use_auth and self.username else requests
        url = f"{self.BASE_URL}{endpoint}"

        response = session.get(url)
        response.raise_for_status()
        return response.json()

    def get_player_profile(self, username: str, use_auth: bool = False) -> Dict:
        """Get player profile information."""
        return self._get(f"/player/{username}", use_auth=use_auth)

    def get_player_stats(self, username: str, use_auth: bool = False) -> Dict:
        """Get player statistics."""
        return self._get(f"/player/{username}/stats", use_auth=use_auth)

    def get_my_profile(self) -> Optional[Dict]:
        """Get authenticated user's profile (requires authentication)."""
        if not self.username:
            print("⚠ Authentication required for this feature")
            return None

        try:
            # Chess.com public API doesn't have /player/me endpoint
            # For now, just return profile for the configured username
            print("ℹ Using public API - returning profile for configured username")
            return self._get(f"/player/{self.username}")
        except Exception as e:
            print(f"⚠ Failed to get profile: {e}")
            return None

    def test_authentication(self) -> bool:
        """Test if credentials are configured and API is accessible.

        This method validates the credential setup by attempting to access
        the Chess.com profile for the configured username. Since Chess.com's
        public API doesn't require authentication for most operations, this
        mainly tests that:
        1. Credentials are properly loaded from config.local.ini
        2. The configured username exists and is accessible
        3. The API is responding correctly

        Returns:
            bool: True if credentials are configured and profile is accessible,
                  False otherwise (with detailed error messages)

        Note: A False return doesn't necessarily mean authentication failed -
        it could indicate the username doesn't exist or has access restrictions.
        """
        if not self.username:
            return False

        try:
            # Test by fetching the configured user's profile
            # This validates both credential loading and API access
            profile = self._get(f"/player/{self.username}")
            if profile and 'username' in profile:
                print(f"✓ Successfully accessed profile for: {profile.get('username')}")
                return True
            else:
                print("⚠ Profile data incomplete")
                return False
        except Exception as e:
            print(f"⚠ Could not access Chess.com profile for '{self.username}': {e}")
            print("ℹ This could mean:")
            print("  - The username doesn't exist")
            print("  - The account is private")
            print("  - There are API access restrictions")
            print("  - The credentials are for future premium features")
            return False

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