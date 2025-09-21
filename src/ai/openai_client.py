"""OpenAI GPT AI Client - Natural Language Chess Analysis and Advice.

This module provides integration with OpenAI's GPT models for generating
natural language chess analysis, improvement suggestions, and strategic advice.
"""

import requests
import json
from typing import Dict, Optional
import os
from pathlib import Path

from . import AIClient


class OpenAIClient(AIClient):
    """Client for OpenAI GPT API integration."""

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize OpenAI client with API key.

        Args:
            api_key: OpenAI API key
            model: GPT model to use (default: gpt-4)
        """
        # Try multiple sources for API key
        final_api_key = api_key or os.getenv("OPENAI_API_KEY") or self._load_api_key_from_config()

        # Initialize parent class
        super().__init__(api_key=final_api_key, name=f"OpenAI {model}")

        self.model = model

        if not self.api_key:
            print("Warning: No OpenAI API key provided. AI features will be limited.")
        else:
            print("✓ OpenAI API key loaded successfully")

    def get_chess_advice(self, pgn: str, analysis_data: Dict) -> str:
        """Get AI-powered chess advice for a game."""
        if not self.api_key:
            return self._get_fallback_advice(analysis_data)

        prompt = self._build_analysis_prompt(pgn, analysis_data)

        try:
            response = self._call_openai_api(prompt)
            return response.get("advice", "Unable to generate advice at this time.")
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_fallback_advice(analysis_data)

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return bool(self.api_key)

    def _call_openai_api(self, prompt: str) -> Dict:
        """Make API call to OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a chess grandmaster providing detailed analysis and improvement advice. Be specific, constructive, and encouraging."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            advice = result["choices"][0]["message"]["content"].strip()
            return {"advice": advice}
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    def _build_analysis_prompt(self, pgn: str, analysis_data: Dict) -> str:
        """Build analysis prompt for OpenAI."""
        summary = analysis_data.get('summary', {})
        blunders = analysis_data.get('blunders', [])

        prompt = f"""Please analyze this chess game and provide specific improvement advice:

GAME PGN:
{pgn}

STOCKFISH ANALYSIS SUMMARY:
- Total moves: {summary.get('total_moves', 'N/A')}
- Accuracy: {summary.get('accuracy', 'N/A')}%
- Blunders: {summary.get('blunder_count', 0)}
- Mistakes: {summary.get('mistake_count', 0)}

{f"TOP BLUNDERS: {blunders[:3]}" if blunders else ""}

Please provide:
1. Overall assessment of the player's strength
2. Key mistakes and what should have been played instead
3. Specific areas for improvement (opening, middlegame, endgame)
4. Tactical/positional concepts to study
5. Encouraging advice for continued improvement

Be specific, constructive, and encouraging. Focus on learning opportunities."""

        return prompt

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

                if 'ai' in config and 'openai_api_key' in config['ai']:
                    api_key = config['ai']['openai_api_key'].strip()
                    if api_key:
                        return api_key
            except Exception as e:
                print(f"⚠ Failed to load OpenAI API key from config: {e}")

        return None