"""Tests for main CLI application."""

import pytest
from click.testing import CliRunner
from src.main import cli


class TestMainCLI:
    """Test cases for main CLI application."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Chess Analyzer" in result.output
        assert "Analyze your chess games" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_fetch_command_requires_username(self):
        """Test that fetch command requires username."""
        result = self.runner.invoke(cli, ['fetch'])
        assert result.exit_code == 2  # Click error for missing argument
        assert "Missing argument" in result.output

    def test_analyze_command_requires_username(self):
        """Test that analyze command requires username."""
        result = self.runner.invoke(cli, ['analyze'])
        assert result.exit_code == 2  # Click error for missing option
        assert "Missing option" in result.output
        assert "--username" in result.output

    def test_stats_command_requires_username(self):
        """Test that stats command requires username."""
        result = self.runner.invoke(cli, ['stats'])
        assert result.exit_code == 2  # Click error for missing option
        assert "Missing option" in result.output
        assert "--username" in result.output