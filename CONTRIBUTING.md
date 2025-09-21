# Contributing to Chess Analyzer

Thank you for your interest in contributing to Chess Analyzer! 🎉

Chess Analyzer is a professional chess analysis application that welcomes contributions from developers, chess enthusiasts, and the open-source community. Whether you're fixing bugs, adding features, improving documentation, or helping with testing, your contributions are valuable and appreciated.

## 🚀 Ways to Contribute

### 🐛 Bug Reports & Issues
- **Found a bug?** [Open an issue](https://github.com/dentity007/chess-analyzer/issues) with detailed steps to reproduce
- **Unexpected behavior?** Include error messages, screenshots, and system information
- **Performance issues?** Provide benchmarks and system specifications

### 💡 Feature Requests & Ideas
- **New features?** [Start a discussion](https://github.com/dentity007/chess-analyzer/discussions) to share your ideas
- **UI improvements?** Mockups and user experience suggestions welcome
- **Integration ideas?** Chess platform integrations, AI providers, etc.

### 📝 Documentation Improvements
- **README updates**: Keep user guides current and comprehensive
- **Code comments**: Improve inline documentation and docstrings
- **API documentation**: Document new features and modules
- **Tutorials**: Create usage examples and guides

### 🧪 Testing & Quality Assurance
- **Write tests**: Unit tests, integration tests, and end-to-end tests
- **Test coverage**: Improve test coverage for new features
- **Bug reproduction**: Create test cases for reported issues
- **Cross-platform testing**: Test on different operating systems

### 💻 Code Contributions
- **Bug fixes**: Submit pull requests for issue resolutions
- **New features**: Implement features from the roadmap
- **Performance improvements**: Optimize analysis speed and memory usage
- **Code refactoring**: Improve code organization and maintainability

## 🛠️ Development Environment Setup

### Prerequisites
- **Python 3.8+** (required for all development)
- **Git** (version control)
- **Virtual Environment** (recommended for dependency management)
- **Stockfish** (optional, for testing analysis features)
- **GitHub Account** (for pull requests and issues)

### Quick Setup (macOS/Linux)
```bash
# 1. Fork and clone the repository
git clone https://github.com/dentity007/chess-analyzer.git
cd chess-analyzer

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set up development tools
pip install -r requirements-dev.txt

# 5. Test the installation
python3 -m src.main --version
python3 -m src.main --help
```

### Windows Setup
```powershell
# 1. Fork and clone
git clone https://github.com/dentity007/chess-analyzer.git
cd chess-analyzer

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test installation
python -m src.main --version
```

### Configuration for Development
```bash
# Create local configuration (optional, for testing)
cp config.local.ini.example config.local.ini
# Edit config.local.ini with your test credentials
# Note: This file is gitignored for security

# Set up environment variables (optional)
export XAI_API_KEY=your_test_key_here
```

## 📋 Development Workflow

### 1. Choose an Issue or Feature
- Check [existing issues](https://github.com/dentity007/chess-analyzer/issues) for bugs to fix
- Review the [ROADMAP.md](ROADMAP.md) for planned features
- Look for issues labeled `good first issue` or `help wanted`

### 2. Create a Branch
```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Your Changes
- **Follow the existing code style** (PEP 8, type hints, docstrings)
- **Add tests** for new functionality
- **Update documentation** if needed
- **Test your changes** thoroughly

### 4. Test Your Changes
```bash
# Run the test suite
pytest tests/

# Test specific functionality
python3 -m src.main --gui  # Test GUI
python3 -m src.main auth-test  # Test authentication
python3 -m src.main fetch testuser  # Test API integration

# Build and test executable (macOS)
./build_macos.sh
open dist/ChessAnalyzer.app
```

### 5. Commit and Push
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature description

- What was changed
- Why it was changed
- Any breaking changes"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create a Pull Request
- Go to the [repository](https://github.com/dentity007/chess-analyzer)
- Click "New Pull Request"
- Select your branch and provide a clear description
- Reference any related issues
- Wait for review and address feedback

## 🎯 Coding Standards

### Python Style
- **PEP 8** compliance for code formatting
- **Type hints** for function parameters and return values
- **Docstrings** for all public functions and classes
- **Descriptive variable names** (avoid single letters except loops)

### Code Structure
```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised
    """
    # Implementation here
    pass
```

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

**Examples:**
```
feat(auth): add OAuth2 support for Chess.com
fix(gui): resolve crash on double-click for macOS
docs(readme): update installation instructions
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run tests matching pattern
pytest -k "test_auth"
```

### Writing Tests
```python
import pytest
from src.api.client import ChessComClient

class TestChessComClient:
    def test_get_player_profile(self):
        """Test fetching player profile from Chess.com API."""
        client = ChessComClient()
        profile = client.get_player_profile("magnuscarlsen")

        assert profile is not None
        assert "username" in profile
        assert profile["username"] == "magnuscarlsen"
```

### Test Coverage Goals
- **Unit Tests**: 80%+ coverage for core modules
- **Integration Tests**: API and database interactions
- **End-to-End Tests**: Complete user workflows
- **Cross-Platform Tests**: Windows, macOS, Linux compatibility

## 📚 Documentation Standards

### README Updates
- Keep installation instructions current
- Update feature lists as new features are added
- Maintain accurate prerequisites and system requirements
- Update screenshots and examples regularly

### Code Documentation
- **Module docstrings**: Overview of module purpose and contents
- **Class docstrings**: Class purpose, attributes, and usage
- **Function docstrings**: Parameters, return values, exceptions
- **Inline comments**: Complex logic explanations

### API Documentation
```python
class ChessComClient:
    """Client for Chess.com Public API integration.

    This class provides methods to interact with Chess.com's public API
    for fetching player data, games, and statistics.

    Attributes:
        BASE_URL: Chess.com API base URL
        REQUEST_DELAY: Rate limiting delay between requests
    """
```

## 🚨 Issue Reporting Guidelines

### Bug Reports
**Please include:**
- **Steps to reproduce**: Detailed step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, application version
- **Error messages**: Full error output and stack traces
- **Screenshots**: If applicable, especially for GUI issues

### Feature Requests
**Please include:**
- **Use case**: Why do you need this feature?
- **Current workaround**: How do you currently handle this?
- **Proposed solution**: Your suggested implementation
- **Alternatives considered**: Other approaches you've thought of

## 🎉 Recognition

Contributors will be:
- **Acknowledged** in release notes and documentation
- **Listed** in CONTRIBUTORS.md file
- **Featured** in the project's hall of fame
- **Invited** to join the core development team for significant contributions

## 📞 Getting Help

- **📧 Questions**: Open a [GitHub Discussion](https://github.com/dentity007/chess-analyzer/discussions)
- **🐛 Bugs**: [Create an Issue](https://github.com/dentity007/chess-analyzer/issues)
- **💡 Ideas**: [Start a Discussion](https://github.com/dentity007/chess-analyzer/discussions)
- **💬 Chat**: Join our community discussions

## 📋 Checklist for Contributions

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format
- [ ] No sensitive information committed
- [ ] Tested on target platforms

### Pull Request Requirements
- [ ] Clear description of changes
- [ ] References related issues
- [ ] Includes tests for new functionality
- [ ] Updates documentation
- [ ] No merge conflicts
- [ ] Ready for review

Thank you for contributing to Chess Analyzer! Your efforts help make chess analysis more accessible and powerful for players worldwide. ♟️🤖

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

- Update changelog for significant changes

## 🔒 Security Considerations

### Credential Management
- **Never commit credentials** to version control
- Use `config.local.ini` for local development credentials
- This file is automatically excluded by `.gitignore`
- For testing, use test accounts with minimal privileges

### API Security
- Respect rate limits when working with Chess.com API
- Handle API errors gracefully
- Don't expose sensitive information in logs
- Use HTTPS for all external communications

### Code Security
- Validate all user inputs
- Use parameterized queries for database operations
- Avoid hardcoding sensitive information
- Follow principle of least privilege

### Reporting Security Issues
- Report security vulnerabilities to: security@chess-analyzer.dev
- Don't create public issues for security problems
- Allow time for fixes before public disclosure

## 🔧 Tools and Dependencies

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