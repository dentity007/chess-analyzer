"""AI Module - Multi-Provider AI Integration for Chess Analysis.

This module provides a unified interface for multiple AI providers to offer
chess analysis and improvement suggestions. Currently supports:

- xAI Grok (default)
- OpenAI GPT models
- Anthropic Claude models
- Local models (future)

The system automatically detects available providers and falls back gracefully
when API keys are not configured.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import os
from pathlib import Path

class AIClient(ABC):
    """Abstract base class for AI provider clients.

    This class defines the common interface that all AI providers must implement,
    allowing the chess analyzer to work with different AI services seamlessly.
    """

    def __init__(self, api_key: Optional[str] = None, name: str = "Unknown"):
        """Initialize AI client.

        Args:
            api_key: API key for the AI provider
            name: Human-readable name of the AI provider
        """
        self.api_key = api_key
        self.name = name
        self.available = bool(api_key)

    @abstractmethod
    def get_chess_advice(self, pgn: str, analysis_data: Dict) -> str:
        """Get AI-powered chess advice for a game.

        Args:
            pgn: Portable Game Notation string of the chess game
            analysis_data: Dictionary containing analysis results from Stockfish

        Returns:
            String containing AI-generated advice and analysis
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this AI provider is available for use.

        Returns:
            True if the provider can be used, False otherwise
        """
        return self.available

    def _get_fallback_advice(self, analysis_data: Dict) -> str:
        """Provide basic analysis when AI is not available.

        Args:
            analysis_data: Analysis data from Stockfish

        Returns:
            Basic analysis summary without AI enhancement
        """
        summary = analysis_data.get('summary', {})
        blunders = analysis_data.get('blunders', [])

        advice = f"Basic Analysis (AI not configured):\n"
        advice += f"• Total moves: {summary.get('total_moves', 'N/A')}\n"
        advice += f"• Accuracy: {summary.get('accuracy', 'N/A'):.1f}%\n"
        advice += f"• Blunders: {summary.get('blunder_count', 0)}\n"
        advice += f"• Mistakes: {summary.get('mistake_count', 0)}\n"

        if blunders:
            advice += f"\nTop blunder: {blunders[0].get('move', 'N/A')} (lost {blunders[0].get('score_change', 0)} cp)"

        advice += f"\n\n💡 Configure an AI API key for personalized advice!"
        return advice

def get_available_providers() -> List[str]:
    """Get list of available AI providers based on configuration.

    Returns:
        List of provider names that are configured and available
    """
    providers = []

    # Check for xAI Grok
    if os.getenv("XAI_API_KEY") or _load_api_key_from_config("xai"):
        providers.append("xai")

    # Check for OpenAI
    if os.getenv("OPENAI_API_KEY") or _load_api_key_from_config("openai"):
        providers.append("openai")

    # Check for Anthropic Claude
    if os.getenv("ANTHROPIC_API_KEY") or _load_api_key_from_config("anthropic"):
        providers.append("anthropic")

    return providers

def create_ai_client(provider: str = "auto") -> AIClient:
    """Create an AI client instance for the specified provider.

    Args:
        provider: AI provider to use ("xai", "openai", "anthropic", or "auto")

    Returns:
        AIClient instance for the requested provider
    """
    if provider == "auto":
        # Auto-select the first available provider
        available = get_available_providers()
        if available:
            provider = available[0]
        else:
            # Return a dummy client if no providers are available
            from .grok_client import GrokClient
            return GrokClient()

    if provider == "xai":
        from .grok_client import GrokClient
        return GrokClient()
    elif provider == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient()
    elif provider == "anthropic":
        from .claude_client import ClaudeClient
        return ClaudeClient()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

def _load_api_key_from_config(provider: str) -> Optional[str]:
    """Load API key for a specific provider from config file.

    Args:
        provider: Provider name ("xai", "openai", "anthropic")

    Returns:
        API key string if found, None otherwise
    """
    config_path = Path(__file__).parent.parent.parent / "config.local.ini"

    if config_path.exists():
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)

            if 'ai' in config and f'{provider}_api_key' in config['ai']:
                api_key = config['ai'][f'{provider}_api_key'].strip()
                if api_key:
                    return api_key
        except Exception:
            pass

    return None

# Import concrete implementations for easy access
from .grok_client import GrokClient
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient