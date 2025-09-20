# Contributing to Chess Analyzer

Thank you for your interest in contributing to Chess Analyzer! We welcome contributions from the community.

## 🚀 Ways to Contribute

- **🐛 Bug Reports**: Found a bug? [Open an issue](https://github.com/yourusername/chess-analyzer/issues)
- **💡 Feature Requests**: Have an idea? [Start a discussion](https://github.com/yourusername/chess-analyzer/discussions)
- **📝 Documentation**: Help improve our docs
- **🧪 Testing**: Write or improve tests
- **💻 Code**: Submit pull requests

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- (Optional) Stockfish chess engine

### Setup Steps

```bash
# Fork the repository
git clone https://github.com/yourusername/chess-analyzer.git
cd chess-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests to ensure everything works
pytest tests/

# Start developing
python -m src.main --gui
```

## 📋 Development Workflow

### 1. Choose an Issue
- Check [open issues](https://github.com/yourusername/chess-analyzer/issues)
- Look for issues labeled `good first issue` or `help wanted`

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Follow our [Code Style Guidelines](#code-style)
- Write tests for new features
- Update documentation as needed
- Test your changes thoroughly

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring

### 5. Push and Create PR
```bash
git push origin your-branch-name
```
Then create a pull request on GitHub.

## 🎯 Code Style Guidelines

### Python Style
- Follow [PEP 8](https://pep8.org/) guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters
- Use type hints for function parameters and return values

### Example
```python
from typing import List, Optional

def analyze_games(games: List[dict], username: str) -> Optional[dict]:
    """
    Analyze a list of chess games for a specific user.

    Args:
        games: List of game dictionaries
        username: Chess.com username

    Returns:
        Analysis results or None if no games
    """
    if not games:
        return None

    # Implementation here
    pass
```

### Documentation
- Use Google-style docstrings
- Document all public functions and classes
- Include type hints
- Provide usage examples where helpful

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `ChessAnalyzer`)
- **Functions/Methods**: `snake_case` (e.g., `analyze_game`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_DEPTH`)
- **Private**: Prefix with `_` (e.g., `_helper_function`)

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific tests
pytest tests/test_api_client.py -v

# Run tests matching pattern
pytest -k "test_analyze" -v
```

### Writing Tests
- Use `pytest` framework
- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names: `test_should_do_something`
- Mock external dependencies (APIs, databases, etc.)

### Test Structure
```python
import pytest
from src.api.client import ChessComClient

class TestChessComClient:
    def setup_method(self):
        """Set up test fixtures."""
        self.client = ChessComClient()

    def test_get_player_profile_success(self):
        """Test successful player profile retrieval."""
        # Test implementation
        pass

    def test_get_player_profile_error(self):
        """Test error handling for profile retrieval."""
        # Test implementation
        pass
```

## 📚 Documentation

### Updating Documentation
- Keep README.md up to date
- Update docstrings when changing function signatures
- Add examples for new features
- Update changelog for significant changes

### Documentation Files
- `README.md`: Main project documentation
- `docs/`: Detailed documentation
- `CHANGELOG.md`: Version history
- `CONTRIBUTING.md`: This file

## 🔧 Tools and Dependencies

### Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Code Quality Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Pre-commit Hooks (Recommended)
```bash
pip install pre-commit
pre-commit install
```

## 🚨 Issue Reporting

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Logs/Screenshots**: If applicable

### Feature Requests
For feature requests, please include:
- **Description**: What feature you'd like
- **Use case**: Why this feature would be useful
- **Alternatives**: Any alternative solutions you've considered

## 📝 Pull Request Guidelines

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Changelog updated (if needed)
- [ ] Self-review completed

### PR Description
A good PR description includes:
- **What**: What changes were made
- **Why**: Why these changes were needed
- **How**: How the changes work
- **Testing**: How the changes were tested

### Example PR Description
```
## What
Added support for analyzing games by date range in the GUI.

## Why
Users wanted to analyze specific time periods of their games.

## How
- Modified GUI to include date picker widgets
- Updated database queries to support date filtering
- Added validation for date range inputs

## Testing
- Added unit tests for date filtering logic
- Tested GUI date selection manually
- Verified database queries work correctly
```

## 🎉 Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Recognized in the project's hall of fame

## 📞 Getting Help

- **Discussions**: [GitHub Discussions](https://github.com/yourusername/chess-analyzer/discussions)
- **Issues**: [GitHub Issues](https://github.com/yourusername/chess-analyzer/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/chess-analyzer/wiki)

## 📋 Code of Conduct

Please be respectful and constructive in all interactions. We follow a code of conduct to ensure a positive community experience.

---

Thank you for contributing to Chess Analyzer! Your help makes the project better for everyone. 🎯