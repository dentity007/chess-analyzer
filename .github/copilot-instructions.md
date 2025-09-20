# Chess Analyzer - AI Coding Guidelines

## Architecture Overview

This is a cross-platform Python desktop application for analyzing chess games from Chess.com. The app follows a modular 5-layer architecture:

- **Data Fetching Layer**: Chess.com public API integration with local credential storage
- **Storage Layer**: SQLite database for caching games locally with efficient querying
- **Analysis Layer**: python-chess + Stockfish engine for move evaluation and blunder detection
- **AI Guidance Layer**: xAI Grok LLM integration for personalized chess improvement advice
- **UI Layer**: CLI first (click framework), GUI support (Tkinter), standalone executables (PyInstaller)

## Current Implementation Status (v0.1.0)

### ✅ Completed Features
- **macOS Application Bundle**: ChessAnalyzer.app (35MB) - fully functional standalone executable
- **Cross-Platform CLI**: Complete command-line interface with all core features
- **Chess.com API Integration**: Public API access with rate limiting and error handling
- **Local Database**: SQLite storage with efficient game caching and querying
- **Stockfish Integration**: Chess engine for move evaluation and blunder detection
- **xAI Grok Integration**: AI-powered chess improvement suggestions
- **Build System**: Automated macOS executable creation with build_macos.sh
- **Security**: Local credential storage in config.local.ini (gitignored)

### 🚧 Development Branch (feature/mac-executable)
- Windows executable build preparation
- Linux executable build preparation
- Enhanced GUI features
- Performance optimizations
- Extended testing coverage

## Key Components & Patterns

### Chess.com API Integration
- Use `chess.com` Python package or `requests` for API calls
- Base URL: `https://api.chess.com/pub`
- Key endpoints: `/player/{username}/games/archives` for monthly archives, `/player/{username}/games/{YYYY}/{MM}` for games
- Rate limiting: Add delays between requests to avoid API throttling
- Filter games by `start_time`/`end_time` Unix timestamps for date ranges

### Database Schema
```sql
-- Games table structure
CREATE TABLE games (
    game_id TEXT PRIMARY KEY,
    pgn TEXT NOT NULL,
    date INTEGER,  -- Unix timestamp
    result TEXT,   -- e.g., "1-0", "0-1", "1/2-1/2"
    white_username TEXT,
    black_username TEXT
);
```

### Chess Analysis Patterns
- Parse PGN using `python-chess` library: `chess.pgn.read_game(io.StringIO(pgn_string))`
- Evaluate positions with Stockfish: Use centipawn scores, detect blunders (>200 cp drop)
- Categorize by game phase: Opening (first 10-15 moves), middlegame, endgame
- Position representation: FEN strings for vector embeddings

### AI Integration
- **LLM**: xAI Grok API for natural language chess advice
- **Current Implementation**: Direct API calls without RAG (simplified for v0.1.0)
- **Future RAG Setup**: Use `chromadb` or `faiss` with `sentence-transformers` for FEN position embeddings
- **Prompt Pattern**: "Analyze this PGN [insert PGN]. Highlight mistakes in [opening/endgame]. Suggest improvements with examples."
- **Context Retrieval**: Future implementation will query vector DB for similar positions from user's game history

## Development Workflows

### Game Fetching & Storage
```python
# Fetch all game archives
archives = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives").json()
for archive_url in archives["archives"]:
    games = requests.get(archive_url).json()["games"]
    # Insert into SQLite with upsert logic
```

### Analysis Pipeline
```python
import chess
import chess.engine

# Load game from PGN
game = chess.pgn.read_game(io.StringIO(pgn))
board = game.board()

# Evaluate with Stockfish
engine = chess.engine.SimpleEngine.popen_uci("path/to/stockfish")
for move in game.mainline_moves():
    # Get evaluation before move
    info = engine.analyse(board, chess.engine.Limit(time=0.1))
    score_before = info["score"].relative.score()
    board.push(move)
    # Get evaluation after move
    info = engine.analyse(board, chess.engine.Limit(time=0.1))
    score_after = info["score"].relative.score()
    # Detect blunders: score_before - score_after > 200
```

### Packaging
- Use PyInstaller: `pyinstaller --onefile app.py` or automated scripts
- Bundle all dependencies including python-chess, tkinter, and requests
- Handle cross-platform paths for engine binary
- macOS: Use `build_macos.sh` for automated .app bundle creation (35MB)
- Windows/Linux: Use `build.py` for cross-platform executables
- Output: Standalone executables that work without Python installation

## Project Conventions

### Dependencies
- `requests` for HTTP calls
- `python-chess` for PGN parsing and board manipulation
- `chess.com` for API wrappers
- `chromadb` or `faiss` for vector storage
- `sentence-transformers` for embeddings
- `click` or `argparse` for CLI
- `pyqt5` or `tkinter` for GUI

### Error Handling
- Chess.com API: Handle rate limits with exponential backoff
- Stockfish: Check if binary exists, prompt user to download if missing
- LLM API: Handle rate limits and token limits, implement retry logic

### Testing
- Mock Chess.com API responses for unit tests
- Use test PGNs for analysis validation
- Test blunder detection with known problematic positions

## Integration Points

- **Chess.com API**: Public data only, no authentication
- **xAI Grok**: Requires API key, check https://x.ai/api for access
- **Stockfish**: ~10MB binary, user downloads separately, app configures path
- **Vector DB**: Local instance for RAG, populated with user's game positions

## File Organization
```
chess-analyzer/
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   └── ISSUE_TEMPLATE/     # GitHub issue templates
├── src/
│   ├── api/               # Chess.com API integration
│   │   └── client.py      # API client with rate limiting
│   ├── db/                # SQLite database layer
│   ├── analysis/          # Chess engine integration
│   ├── ai/                # AI/LLM clients (Grok integration)
│   ├── gui.py            # Tkinter GUI application
│   └── main.py           # CLI entry point with click framework
├── tests/                 # Unit and integration tests
├── dist/                  # Built executables (generated)
│   └── ChessAnalyzer.app  # macOS application bundle (35MB)
├── build/                 # Build artifacts (generated)
├── requirements.txt       # Python dependencies
├── build.py              # Cross-platform packaging script
├── build_macos.sh        # macOS-specific build script (automated)
├── build_simple.sh       # Simple build script
├── ChessAnalyzer.spec    # PyInstaller configuration (cross-platform)
├── ChessAnalyzer_macos.spec  # macOS-specific PyInstaller config
├── config.local.ini.example  # Example configuration file
├── .gitignore           # Excludes config.local.ini and build artifacts
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Development guidelines
├── ROADMAP.md          # Future development plans
├── SECURITY.md          # Security policy
├── CODE_OF_CONDUCT.md   # Community guidelines
├── LICENSE             # MIT License
├── project_plan.md     # Implementation plan and status
└── README.md           # User documentation
```</content>
<parameter name="filePath">/Users/nmaine/local copy github/chess analyzer/.github/copilot-instructions.md