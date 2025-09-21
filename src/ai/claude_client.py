"""Anthropic Claude AI Client - Natural Language Chess Analysis and Advice.

This module provides integration with Anthropic's Claude models for generating
natural language chess analysis, improvement suggestions, and strategic advice.
"""

import requests
import json
from typing import Dict, Optional
import os
from pathlib import Path

from . import AIClient


class ClaudeClient(AIClient):
    """Client for Anthropic Claude API integration."""

    BASE_URL = "https://api.anthropic.com/v1"

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """Initialize Claude client with API key.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-3-sonnet)
        """
        # Try multiple sources for API key
        final_api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or self._load_api_key_from_config()

        # Initialize parent class
        super().__init__(api_key=final_api_key, name=f"Anthropic {model.split('-')[1] if '-' in model else model}")

        self.model = model

        if not self.api_key:
            print("Warning: No Anthropic API key provided. AI features will be limited.")
        else:
            print("✓ Anthropic API key loaded successfully")

    def get_chess_advice(self, pgn: str, analysis_data: Dict) -> str:
        """Get AI-powered chess advice for a game."""
        if not self.api_key:
            return self._get_fallback_advice(analysis_data)

        prompt = self._build_analysis_prompt(pgn, analysis_data)

        try:
            response = self._call_claude_api(prompt)
            return response.get("advice", "Unable to generate advice at this time.")
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return self._get_fallback_advice(analysis_data)

    def is_available(self) -> bool:
        """Check if Claude client is available."""
        return bool(self.api_key)

    def _call_claude_api(self, prompt: str) -> Dict:
        """Make API call to Claude."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.7,
            "system": "You are a chess grandmaster providing detailed analysis and improvement advice. Be specific, constructive, and encouraging.",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            f"{self.BASE_URL}/messages",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            advice = result["content"][0]["text"].strip()
            return {"advice": advice}
        else:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")

    def _build_analysis_prompt(self, pgn: str, analysis_data: Dict) -> str:
        """Build analysis prompt for Claude."""
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

                if 'ai' in config and 'anthropic_api_key' in config['ai']:
                    api_key = config['ai']['anthropic_api_key'].strip()
                    if api_key:
                        return api_key
            except Exception as e:
                print(f"⚠ Failed to load Anthropic API key from config: {e}")

        return None