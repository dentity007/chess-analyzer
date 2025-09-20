# Chess Analyzer - AI Coding Guidelines

## Architecture Overview

This is a cross-platform Python desktop application for analyzing chess games from Chess.com. The app follows a modular 5-layer architecture:

- **Data Fetching Layer**: Chess.com public API integration (no authentication required)
- **Storage Layer**: SQLite database for caching games locally
- **Analysis Layer**: python-chess + Stockfish engine for move evaluation and blunder detection
- **AI Guidance Layer**: xAI Grok LLM with RAG (Retrieval-Augmented Generation) using vector database
- **UI Layer**: CLI first (click/argparse), then GUI (Tkinter/PyQt)

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
- **RAG Setup**: Use `chromadb` or `faiss` with `sentence-transformers` for FEN position embeddings
- **Prompt Pattern**: "Analyze this PGN [insert PGN]. Highlight mistakes in [opening/endgame]. Suggest improvements with examples."
- **Context Retrieval**: Query vector DB for similar positions from user's game history

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
- Use PyInstaller: `pyinstaller --onefile app.py`
- Bundle Stockfish binary with the executable
- Handle cross-platform paths for engine binary

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
chess_analyzer/
├── data/           # SQLite database files
├── engines/        # Stockfish binaries
├── src/
│   ├── api/        # Chess.com API clients
│   ├── db/         # Database models and queries
│   ├── analysis/   # Chess engine integration
│   ├── ai/         # LLM and RAG components
│   └── ui/         # CLI/GUI interfaces
├── tests/          # Unit and integration tests
└── requirements.txt
```</content>
<parameter name="filePath">/Users/nmaine/local copy github/chess analyzer/.github/copilot-instructions.md