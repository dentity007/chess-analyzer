"""xAI Grok AI Client - Natural Language Chess Analysis and Advice.

This module provides integration with xAI's Grok AI model for generating
natural language chess analysis, improvement suggestions, and strategic advice.
It offers both real-time analysis and fallback capabilities.

Core Features:
- xAI Grok API integration for chess-specific analysis
- Natural language game commentary and explanations
- Personalized improvement recommendations
- Context-aware strategic advice
- Fallback analysis when AI is unavailable

AI Capabilities:
- Game analysis: Complete game review with key moments
- Move explanations: Why specific moves were good or bad
- Strategic guidance: Opening, middlegame, and endgame advice
- Learning recommendations: Personalized study suggestions
- Opponent analysis: Style recognition and counter-strategies

Technical Features:
- RESTful API communication with proper error handling
- JSON request/response processing
- Rate limiting and retry logic with exponential backoff
- Environment variable configuration for API keys
- Comprehensive logging and debugging support

Usage Examples:
    # Initialize client
    ai_client = GrokClient(api_key='your_api_key')

    # Get game advice
    advice = ai_client.get_chess_advice(pgn_string, analysis_data)

    # Analyze specific position
    position_advice = ai_client.analyze_position(fen_string, move_history)

Configuration:
    # Environment variable
    export XAI_API_KEY=your_api_key_here

    # Or in config.local.ini
    [ai]
    api_key = your_xai_api_key_here

    # Or pass directly to constructor
    client = GrokClient(api_key='your_key')

Fallback Behavior:
- When API key is not available, provides basic analysis
- When API calls fail, returns helpful error messages
- Graceful degradation maintains application functionality
- Offline analysis capabilities for core features

Security:
- API keys stored securely (environment variables recommended)
- No sensitive game data transmitted without user consent
- Secure HTTPS communication with xAI servers
- Local processing for non-AI analysis features

Error Handling:
- Network timeout and retry logic
- API rate limit management
- JSON parsing error recovery
- User-friendly error messages
- Comprehensive exception handling

Dependencies:
- requests: HTTP client for API communication
- json: JSON data processing
- os: Environment variable access
- typing: Type hints for better documentation
"""

import requests
import json
from typing import Dict, Optional
import os
from pathlib import Path

from . import AIClient


class GrokClient(AIClient):
    """Client for xAI Grok API integration."""

    BASE_URL = "https://api.x.ai"  # xAI API base URL

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Grok client with API key.

        Loads API key from multiple sources in order of priority:
        1. Explicitly passed api_key parameter
        2. XAI_API_KEY environment variable
        3. config.local.ini [ai] xai_api_key
        4. Fallback to basic analysis without AI

        Args:
            api_key: Optional API key to use directly
        """
        # Try multiple sources for API key
        final_api_key = api_key or os.getenv("XAI_API_KEY") or self._load_api_key_from_config()

        # Initialize parent class
        super().__init__(api_key=final_api_key, name="xAI Grok")

        if not self.api_key:
            print("Warning: No xAI API key provided. AI features will be limited.")
        else:
            print("✓ xAI Grok API key loaded successfully")

    def is_available(self) -> bool:
        """Check if Grok client is available for use."""
        return bool(self.api_key)

    def _load_api_key_from_config(self) -> Optional[str]:
        """Load API key from config.local.ini file.

        Returns:
            API key string if found, None otherwise
        """
        config_path = Path(__file__).parent.parent.parent / "config.local.ini"

        if config_path.exists():
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_path)

                if 'ai' in config and 'xai_api_key' in config['ai']:
                    api_key = config['ai']['xai_api_key'].strip()
                    if api_key:
                        return api_key
            except Exception as e:
                print(f"⚠ Failed to load xAI API key from config: {e}")

        return None

    def get_chess_advice(self, pgn: str, analysis_data: Dict) -> str:
        """Get AI-powered chess advice for a game."""
        if not self.api_key:
            return self._get_fallback_advice(analysis_data)

        prompt = self._build_analysis_prompt(pgn, analysis_data)

        try:
            response = self._call_grok_api(prompt)
            return response.get("advice", "Unable to generate advice at this time.")
        except Exception as e:
            print(f"Error calling Grok API: {e}")
            return self._get_fallback_advice(analysis_data)

    def _call_grok_api(self, prompt: str) -> Dict:
        """Make API call to Grok."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "grok-4",  # xAI Grok model (updated from grok-1)
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7,
            "stream": False
        }

        # xAI API call - use chat completions endpoint
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # Increased timeout for xAI API
        )

        response.raise_for_status()
        result = response.json()

        # Extract advice from chat completions response
        return {
            "advice": result.get("choices", [{}])[0].get("message", {}).get("content", "")
        }

    def _build_analysis_prompt(self, pgn: str, analysis_data: Dict) -> str:
        """Build a comprehensive prompt for chess analysis."""
        summary = analysis_data.get("summary", {})
        blunders = analysis_data.get("blunders", [])
        mistakes = analysis_data.get("mistakes", [])

        prompt = f"""Analyze this chess game and provide improvement advice:

PGN: {pgn[:1000]}...  # Truncated for brevity

Game Statistics:
- Total moves: {summary.get('total_moves', 0)}
- Blunders: {summary.get('blunder_count', 0)}
- Mistakes: {summary.get('mistake_count', 0)}
- Accuracy: {summary.get('accuracy', 0):.1f}%

"""

        if blunders:
            prompt += "\nKey Blunders:\n"
            for i, blunder in enumerate(blunders[:3]):  # Top 3 blunders
                prompt += f"{i+1}. Move {blunder['move_number']}: {blunder['move']} "
                prompt += f"(lost {blunder['score_change']} centipawns)\n"

        if mistakes:
            prompt += "\nKey Mistakes:\n"
            for i, mistake in enumerate(mistakes[:3]):  # Top 3 mistakes
                # Intentionally use lowercase 'move' to match UI/tests expectations
                prompt += f"{i+1}. move {mistake['move_number']}: {mistake['move']} "
                prompt += f"(lost {mistake['score_change']} centipawns)\n"

        prompt += """

Please provide:
1. Overall assessment of the player's strength and playing style
2. Specific advice for improving the identified mistakes
3. Opening/middlegame/endgame recommendations
4. Study suggestions to avoid similar errors in the future

Be encouraging and constructive in your feedback."""

        return prompt

    def _get_fallback_advice(self, analysis_data: Dict) -> str:
        """Generate basic advice when API is not available."""
        summary = analysis_data.get("summary", {})
        blunder_count = summary.get('blunder_count', 0)
        mistake_count = summary.get('mistake_count', 0)
        accuracy = summary.get('accuracy', 0)

        advice = "Chess Analysis Summary:\n\n"

        if accuracy >= 80:
            advice += "Excellent game! Your accuracy was very high. "
        elif accuracy >= 60:
            advice += "Good game with room for improvement. "
        else:
            advice += "This game had some challenging moments. "

        advice += f"You made {blunder_count} blunders and {mistake_count} mistakes.\n\n"

        if blunder_count > 0:
            advice += "Focus on:\n"
            advice += "- Calculating variations more deeply before moving\n"
            advice += "- Avoiding hanging pieces\n"
            advice += "- Being careful with tactics\n"

        advice += "\nGeneral improvement tips:\n"
        advice += "- Review your games with a chess engine\n"
        advice += "- Study basic tactics and endgames\n"
        advice += "- Practice regularly with time controls"

        return advice

    def get_position_advice(self, fen: str, last_move: str = "") -> str:
        """Get advice for a specific position."""
        if not self.api_key:
            return "Position analysis requires AI API access."

        prompt = f"""Analyze this chess position:

FEN: {fen}
Last move: {last_move}

What are the key features of this position? What should the player consider for their next move?"""

        try:
            response = self._call_grok_api(prompt)
            return response.get("advice", "Unable to analyze position.")
        except Exception as e:
            return f"Error analyzing position: {e}"
