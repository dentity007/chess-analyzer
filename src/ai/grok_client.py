"""xAI Grok API client for chess analysis and advice."""

import requests
import json
from typing import Dict, Optional
import os

class GrokClient:
    """Client for xAI Grok API integration."""

    BASE_URL = "https://api.x.ai/v1"  # Placeholder - check actual xAI API endpoint

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Grok client with API key."""
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            print("Warning: No xAI API key provided. AI features will be limited.")

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
            "model": "grok-beta",  # Placeholder - check actual model name
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Note: This is a placeholder implementation
        # Actual xAI API endpoint and parameters need to be verified
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",  # Placeholder endpoint
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        # Extract advice from response
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
                prompt += f"{i+1}. Move {mistake['move_number']}: {mistake['move']} "
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