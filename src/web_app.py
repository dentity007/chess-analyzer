"""Chess Analyzer Web Interface (Flask).

Provides a local web UI to:
- Fetch Chess.com games for a username
- Analyze stored games with Stockfish
- Generate optional AI insights via configured provider

Notes:
- Runs locally; no credentials are transmitted externally
- Uses SQLite for local storage
- Designed for responsiveness with background threads and progress polling
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
import os
import sys
import threading
import time
import configparser
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.client import ChessComClient
from db.database import ChessDatabase
from analysis.analyzer import ChessAnalyzer
from ai.grok_client import GrokClient

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
# Use a secure random secret key for sessions
import secrets
app.secret_key = secrets.token_hex(32)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables for background processing
current_client = None
current_analyzer = None
current_ai = None
analysis_progress = {"status": "idle", "progress": 0, "message": ""}

def initialize_components():
    """Initialize all Chess Analyzer components."""
    global current_client, current_analyzer, current_ai

    try:
        current_client = ChessComClient()
        current_analyzer = ChessAnalyzer()
        current_ai = GrokClient()
        return True
    except Exception as e:
        print(f"Error initializing components: {e}")
        return False

@app.route('/')
def index():
    """Main page with the Chess Analyzer interface.

    This is the primary entry point for the web application. It serves the main
    HTML interface that allows users to:
    - Enter Chess.com usernames
    - Fetch and analyze games
    - View analysis results and AI advice
    - Manage credentials

    Returns:
        Rendered HTML template for the main application interface
    """
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/test')
def test():
    """Simple test endpoint to verify the server is working.

    This endpoint provides a basic health check for the web server.
    It's useful for:
    - Verifying the Flask application is running
    - Testing API connectivity
    - Debugging server startup issues

    Returns:
        JSON response with server status information
    """
    logger.info("Test endpoint called")
    return jsonify({"status": "ok", "message": "Chess Analyzer web server is running"})

def get_demo_games():
    """Generate sample games for demo purposes.
    
    Returns a list of sample game data that can be inserted into the database
    for testing the analysis features when Chess.com API is unavailable.
    """
    import time
    
    # Sample PGN games for demonstration
    demo_games = [
        {
            "game_id": "demo_game_1",
            "pgn": """[Event "Demo Game 1"]
[Site "Chess Analyzer Demo"]
[Date "2025.10.01"]
[Round "1"]
[White "DemoPlayer"]
[Black "Opponent"]
[Result "1-0"]
[WhiteElo "1500"]
[BlackElo "1400"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 
9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 
16. Bh4 c5 17. dxe5 dxe5 18. Qxd8 Raxd8 19. Nxe5 Nxe5 20. Bxe7 Nfg4 21. Bxd8 Rxd8 
22. hxg4 Nxg4 23. f3 Ne5 24. Bxf7+ Kxf7 25. fxg4 Nxg4 26. Rf1+ Ke7 27. Rf3 Rd2 
28. Re3+ Kd6 29. Rd3+ Rxd3 30. Nxd3 Bxg2 31. Kxg2 Nf2 32. Kf3 Nxd3 33. b3 Kd5 
34. Ke3 Nc5 35. Kd2 Kd4 36. Kc2 Ne4 37. Kb2 Kd3 38. Ka3 Kc3 39. Ka4 b3 40. axb3 Kxb3 
41. Kb5 c4 42. Kc5 c3 43. Kd4 c2 44. Ke3 c1=Q+ 45. Kf2 Qc2+ 46. Kg3 Qd3+ 47. Kh4 Qe4+ 
48. Kh5 Qg6# 0-1""",
            "date": int(time.time()) - 86400,  # Yesterday
            "result": "0-1",
            "white_username": "DemoPlayer",
            "black_username": "Opponent"
        },
        {
            "game_id": "demo_game_2", 
            "pgn": """[Event "Demo Game 2"]
[Site "Chess Analyzer Demo"]
[Date "2025.09.30"]
[Round "1"]
[White "DemoPlayer"]
[Black "StrongOpponent"]
[Result "1/2-1/2"]
[WhiteElo "1500"]
[BlackElo "1600"]

1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 dxc4 5. a4 Bf5 6. Ne5 Nbd7 7. Nxc4 Nb6 8. Ne5 a5 
9. f3 Nfd7 10. Nxd7 Qxd7 11. e4 Bg6 12. Be3 e6 13. Be2 Bb4 14. O-O O-O 15. Qb3 Bxc3 
16. bxc3 Qc7 17. Rac1 Rfd8 18. Rfc2 Nd7 19. Rfc1 Rac8 20. Qa3 Qb6 21. Rb1 Qa6 22. Qxa5 
Qxa5 23. Bxa7 Ra8 24. Be3 Rxb4 25. cxb4 Qxb4 26. Rc4 Qb2 27. Bf1 b5 
28. Rc1 Qb4 29. Rc2 Qb2 30. Rc1 Qb4 1/2-1/2""",
            "date": int(time.time()) - 172800,  # 2 days ago
            "result": "1/2-1/2", 
            "white_username": "DemoPlayer",
            "black_username": "StrongOpponent"
        }
    ]
    
    return demo_games

@app.route('/api/fetch_games', methods=['POST'])
def fetch_games():
    """Fetch games for a Chess.com username via AJAX.

    This API endpoint handles game fetching requests from the web interface.
    It supports different fetching modes: last game only, date range, or recent days.

    Request Body (JSON):
        {"username": "chesscom_username", "mode": "last|range|days", ...}

    Response (JSON):
        {"success": true} or {"success": false, "error": "error_message"}
    """
    # Parse JSON request data
    data = request.get_json()
    username = data.get('username', '').strip()
    fetch_mode = data.get('mode', 'last')  # Default to last game only

    # Validate input - username required unless demo mode
    if not username and fetch_mode != 'demo':
        return jsonify({"success": False, "error": "Please enter a username"})

    # Background worker function for non-blocking game fetching
    def fetch_worker():
        global analysis_progress
        try:
            # Initialize progress tracking
            analysis_progress = {"status": "fetching", "progress": 0, "message": f"Checking for existing games for {username}..."}

            # Create thread-safe database connection
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Check if games already exist for this username (skip if in "last" mode and games exist)
            existing_games = db.get_games_by_username(username)
            if existing_games and fetch_mode == 'last':
                db.close()
                analysis_progress = {"status": "completed", "progress": 100, "message": f"Found {len(existing_games)} existing games for {username} (skipping fetch)"}
                return

            # Determine what to fetch based on mode
            if fetch_mode == 'last':
                # Fetch only the most recent game
                analysis_progress = {"status": "fetching", "progress": 10, "message": f"Fetching most recent game for {username}..."}

                try:
                    # Get the most recent archive
                    archives = current_client.get_game_archives(username)
                    if not archives:
                        analysis_progress = {"status": "error", "progress": 0, "message": "No game archives found"}
                        db.close()
                        return

                    # Get the most recent archive (last in the list)
                    recent_archive_url = archives[-1]
                    games = current_client.get_games_from_archive(recent_archive_url)

                    if games:
                        # Sort by end_time and take the most recent game
                        games.sort(key=lambda x: x.get('end_time', 0), reverse=True)
                        most_recent_game = games[0]

                        # Store only this game
                        db.insert_games_batch([most_recent_game])
                        stored_count = 1
                    else:
                        stored_count = 0

                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Chess.com API blocked the request (403 Forbidden). Try using Demo Mode instead to test analysis features."}
                    else:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Failed to fetch recent game: {error_msg}"}
                    db.close()
                    return

            elif fetch_mode == 'range':
                # Fetch games within date range
                start_date_str = data.get('startDate')
                end_date_str = data.get('endDate')

                if not start_date_str or not end_date_str:
                    analysis_progress = {"status": "error", "progress": 0, "message": "Start and end dates are required"}
                    db.close()
                    return

                analysis_progress = {"status": "fetching", "progress": 10, "message": f"Fetching games from {start_date_str} to {end_date_str}..."}

                try:
                    from datetime import datetime
                    start_date = datetime.fromisoformat(start_date_str)
                    end_date = datetime.fromisoformat(end_date_str)

                    games_data = current_client.get_all_games(username, start_date=start_date, end_date=end_date)
                    stored_count = len(games_data) if games_data else 0

                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Chess.com API blocked the request (403 Forbidden). Try using Demo Mode instead to test analysis features."}
                    else:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Failed to fetch games by date range: {error_msg}"}
                    db.close()
                    return

            elif fetch_mode == 'days':
                # Fetch games from last X days
                days = int(data.get('days', 5))
                end_time = int(time.time())
                start_time = end_time - (days * 24 * 60 * 60)
                
                try:
                    games_data = current_client.fetch_games_by_date_range(username, start_time, end_time)
                    stored_count = len(games_data) if games_data else 0
                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Chess.com API blocked the request (403 Forbidden). Try using Demo Mode instead to test analysis features."}
                    else:
                        analysis_progress = {"status": "error", "progress": 0, "message": f"Failed to fetch recent games: {error_msg}"}
                    db.close()
                    return
                
            elif fetch_mode == 'demo':
                # Demo mode - add sample games for testing
                games_data = get_demo_games()
                stored_count = len(games_data) if games_data else 0

            else:
                analysis_progress = {"status": "error", "progress": 0, "message": "Invalid fetch mode"}
                db.close()
                return

            # Store games in database
            if 'games_data' in locals() and games_data:
                try:
                    db.insert_games_batch(games_data)
                finally:
                    db.close()

            if stored_count > 0:
                analysis_progress = {"status": "completed", "progress": 100, "message": f"Stored {stored_count} games for {username}"}
            else:
                analysis_progress = {"status": "completed", "progress": 100, "message": f"No new games found for {username}"}

        except Exception as e:
            analysis_progress = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}

    thread = threading.Thread(target=fetch_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "Fetching games..."})

@app.route('/api/analyze_games', methods=['POST'])
def analyze_games():
    """Analyze stored games for the provided username, or all games if no username specified."""

    # Try to get username from request (optional)
    req_data = request.get_json(silent=True) or {}
    requested_username = (req_data.get('username') or "").strip()

    def analyze_worker():
        global analysis_progress
        try:
            analysis_progress = {"status": "analyzing", "progress": 0, "message": "Starting analysis..."}

            # Create a new database connection for this thread
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Get games: either for specific username or all games
            if requested_username:
                games = db.get_games_by_username(requested_username)
                if not games:
                    analysis_progress = {"status": "error", "progress": 0, "message": f"No games found for username {requested_username}"}
                    db.close()
                    return
            else:
                # Get all games in database
                games = db.get_all_games()
                if not games:
                    analysis_progress = {"status": "error", "progress": 0, "message": "No games found in database"}
                    db.close()
                    return

            total_games = len(games)
            analyzed_games = []

            for i, game in enumerate(games):
                try:
                    analysis_progress = {
                        "status": "analyzing",
                        "progress": int((i / total_games) * 100),
                        "message": f"Analyzing game {i+1}/{total_games}..."
                    }

                    # Analyze the game
                    analysis = current_analyzer.analyze_game(game['pgn'])

                    # Get AI insights if available
                    ai_insights = ""
                    if current_ai:
                        try:
                            ai_insights = current_ai.get_chess_advice(game['pgn'], analysis)
                        except Exception as e:
                            ai_insights = f"AI analysis not available: {str(e)}"

                    analyzed_games.append({
                        "game_id": game['game_id'],
                        "result": game['result'],
                        "white_username": game['white_username'],
                        "black_username": game['black_username'],
                        "analysis": analysis,
                        "ai_insights": ai_insights
                    })

                except Exception as e:
                    print(f"Error analyzing game {game['game_id']}: {e}")

            analysis_progress = {
                "status": "completed",
                "progress": 100,
                "message": f"Analysis complete! Analyzed {len(analyzed_games)} games",
                "results": analyzed_games
            }

        except Exception as e:
            analysis_progress = {"status": "error", "progress": 0, "message": f"Analysis error: {str(e)}"}

    thread = threading.Thread(target=analyze_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "Starting analysis..."})

@app.route('/api/analyze_single_game', methods=['POST'])
def analyze_single_game():
    """Analyze a single game by game_id."""
    req_data = request.get_json(silent=True) or {}
    game_id = req_data.get('game_id', '').strip()

    if not game_id:
        return jsonify({"success": False, "error": "Game ID is required"})

    def analyze_single_worker():
        global analysis_progress
        try:
            analysis_progress = {"status": "analyzing", "progress": 0, "message": "Starting single game analysis..."}

            # Create a new database connection for this thread
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Get the specific game from database
            game = db.get_game_by_id(game_id)
            if not game:
                analysis_progress = {"status": "error", "progress": 0, "message": f"Game {game_id} not found"}
                db.close()
                return

            analysis_progress = {"status": "analyzing", "progress": 50, "message": "Analyzing game..."}

            # Analyze the game
            analysis = current_analyzer.analyze_game(game['pgn'])

            # Get AI insights if available
            ai_insights = ""
            if current_ai:
                try:
                    ai_insights = current_ai.get_chess_advice(game['pgn'], analysis)
                except Exception as e:
                    ai_insights = f"AI analysis not available: {str(e)}"

            analysis_progress = {
                "status": "completed",
                "progress": 100,
                "message": f"Analysis complete for game {game_id}",
                "result": {
                    "game_id": game['game_id'],
                    "result": game['result'],
                    "white_username": game['white_username'],
                    "black_username": game['black_username'],
                    "analysis": analysis,
                    "ai_insights": ai_insights
                }
            }

            db.close()

        except Exception as e:
            analysis_progress = {"status": "error", "progress": 0, "message": f"Analysis error: {str(e)}"}

    thread = threading.Thread(target=analyze_single_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "Starting single game analysis..."})

@app.route('/api/progress')
def get_progress():
    """Get current analysis progress."""
    return jsonify(analysis_progress)

@app.route('/api/save_credentials', methods=['POST'])
def save_credentials():
    """Save Chess.com credentials."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username:
        return jsonify({"success": False, "error": "Username is required"})

    try:
        # Save to config file
        import configparser
        config_path = Path(__file__).parent.parent / 'config.local.ini'

        config = configparser.ConfigParser()
        if config_path.exists():
            config.read(config_path)

        if 'chess_com' not in config:
            config.add_section('chess_com')

        config['chess_com']['username'] = username
        config['chess_com']['password'] = password

        with open(config_path, 'w') as f:
            config.write(f)

        # Update client with new credentials
        if current_client:
            current_client.username = username
            if password:
                current_client.password = password
                current_client._setup_authenticated_session()

        return jsonify({"success": True, "message": f"Credentials saved for {username}"})

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to save credentials: {str(e)}"})

@app.route('/api/load_credentials')
def load_credentials():
    """Load saved credentials."""
    try:
        config_path = Path(__file__).parent.parent / 'config.local.ini'

        if not config_path.exists():
            return jsonify({"username": "", "password": ""})

        config = configparser.ConfigParser()
        config.read(config_path)

        if 'chess_com' in config:
            username = config['chess_com'].get('username', '')
            password = config['chess_com'].get('password', '')
            return jsonify({"username": username, "password": password})

        return jsonify({"username": "", "password": ""})

    except Exception as e:
        return jsonify({"username": "", "password": "", "error": str(e)})

@app.route('/api/test_auth')
def test_auth():
    """Test Chess.com authentication."""
    if not current_client:
        return jsonify({"success": False, "message": "Client not initialized"})

    try:
        success = current_client.test_authentication()
        if success:
            return jsonify({"success": True, "message": "Authentication successful!"})
        else:
            return jsonify({"success": False, "message": "Authentication failed"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Test failed: {str(e)}"})

@app.route('/api/get_games')
def get_games():
    """Get all stored games from the database."""
    try:
        # Create thread-safe database connection
        from db.database import ChessDatabase
        db = ChessDatabase()
        
        # Get all games from database
        games = db.get_all_games()
        return jsonify({
            "success": True,
            "games": games,
            "count": len(games)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to retrieve games: {str(e)}"})

def create_templates():
    """Create the HTML templates directory and files."""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)

    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Analyzer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.95);
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 25px;
            padding: 10px 30px;
            font-weight: 600;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .progress {
            border-radius: 10px;
            height: 8px;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 12px 20px;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .analysis-result {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chess-king me-2"></i>
                Chess Analyzer
            </a>
            <button class="btn btn-outline-light" onclick="showCredentialsModal()">
                <i class="fas fa-key me-1"></i>Credentials
            </button>
        </div>
    </nav>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-body p-5">
                        <h2 class="card-title text-center mb-4">
                            <i class="fas fa-chess-board me-2"></i>
                            Chess Game Analyzer
                        </h2>

                        <!-- Username Input -->
                        <div class="mb-4">
                            <label for="username" class="form-label">
                                <i class="fas fa-user me-1"></i>Chess.com Username
                            </label>
                            <input type="text" class="form-control" id="username" placeholder="Enter Chess.com username">
                        </div>

                        <!-- Game Fetching Options -->
                        <div class="mb-4">
                            <label class="form-label">
                                <i class="fas fa-cogs me-1"></i>Game Fetching Options
                            </label>
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fetchMode" id="lastGameOnly" value="last" checked>
                                        <label class="form-check-label" for="lastGameOnly">
                                            Last Game Only
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fetchMode" id="dateRange" value="range">
                                        <label class="form-check-label" for="dateRange">
                                            Date Range
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fetchMode" id="recentDays" value="days">
                                        <label class="form-check-label" for="recentDays">
                                            Last X Days
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fetchMode" id="demoMode" value="demo">
                                        <label class="form-check-label" for="demoMode">
                                            <i class="fas fa-flask me-1"></i>Demo Mode
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <!-- Date Range Inputs (hidden by default) -->
                            <div id="dateRangeInputs" style="display: none; margin-top: 15px;">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label for="startDate" class="form-label">Start Date</label>
                                        <input type="date" class="form-control" id="startDate">
                                    </div>
                                    <div class="col-md-6">
                                        <label for="endDate" class="form-label">End Date</label>
                                        <input type="date" class="form-control" id="endDate">
                                    </div>
                                </div>
                            </div>

                            <!-- Days Input (hidden by default) -->
                            <div id="daysInput" style="display: none; margin-top: 15px;">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label for="daysCount" class="form-label">Number of Days</label>
                                        <input type="number" class="form-control" id="daysCount" value="5" min="1" max="365">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="d-grid gap-3 mb-4">
                            <button class="btn btn-primary btn-lg" onclick="fetchGames()">
                                <i class="fas fa-download me-2"></i>Fetch Games
                            </button>
                            <button class="btn btn-success btn-lg" onclick="analyzeGames()">
                                <i class="fas fa-search me-2"></i>Analyze Games
                            </button>
                            <button class="btn btn-info btn-lg" onclick="showStats()">
                                <i class="fas fa-chart-bar me-2"></i>Show Statistics
                            </button>
                        </div>

                        <!-- Progress Bar -->
                        <div id="progressSection" style="display: none;">
                            <div class="mb-3">
                                <div class="progress">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated"
                                         role="progressbar" style="width: 0%" id="progressBar"></div>
                                </div>
                            </div>
                            <p class="text-center mb-0" id="progressText">Initializing...</p>
                        </div>

                        <!-- Results Section -->
                        <div id="resultsSection" style="display: none;">
                            <h4 class="mb-3"><i class="fas fa-list me-2"></i>Analysis Results</h4>
                            <div id="resultsContainer"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Credentials Modal -->
    <div class="modal fade" id="credentialsModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-key me-2"></i>Chess.com Credentials
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="credUsername" class="form-label">Username</label>
                        <input type="text" class="form-control" id="credUsername" placeholder="Chess.com username">
                    </div>
                    <div class="mb-3">
                        <label for="credPassword" class="form-label">Password</label>
                        <input type="password" class="form-control" id="credPassword" placeholder="Password (optional)">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="testCredentials()">Test</button>
                    <button type="button" class="btn btn-success" onclick="saveCredentials()">Save</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let progressInterval;

        // Handle fetch mode changes
        document.addEventListener('DOMContentLoaded', function() {
            const fetchModeRadios = document.querySelectorAll('input[name="fetchMode"]');
            fetchModeRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    updateFetchModeUI();
                });
            });
            updateFetchModeUI(); // Initial state
        });

        function updateFetchModeUI() {
            const fetchMode = document.querySelector('input[name="fetchMode"]:checked').value;
            const dateRangeInputs = document.getElementById('dateRangeInputs');
            const daysInput = document.getElementById('daysInput');

            // Hide all inputs first
            dateRangeInputs.style.display = 'none';
            daysInput.style.display = 'none';

            // Show relevant inputs
            if (fetchMode === 'range') {
                dateRangeInputs.style.display = 'block';
            } else if (fetchMode === 'days') {
                daysInput.style.display = 'block';
            }
        }

        function showCredentialsModal() {
            // Load saved credentials
            fetch('/api/load_credentials')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('credUsername').value = data.username || '';
                    document.getElementById('credPassword').value = data.password || '';
                    new bootstrap.Modal(document.getElementById('credentialsModal')).show();
                });
        }

        function saveCredentials() {
            const username = document.getElementById('credUsername').value;
            const password = document.getElementById('credPassword').value;

            fetch('/api/save_credentials', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Credentials saved successfully!');
                    bootstrap.Modal.getInstance(document.getElementById('credentialsModal')).hide();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        function testCredentials() {
            fetch('/api/test_auth')
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                });
        }

        function fetchGames() {
            const username = document.getElementById('username').value;
            const fetchMode = document.querySelector('input[name="fetchMode"]:checked').value;
            
            // Demo mode doesn't require username
            if (!username && fetchMode !== 'demo') {
                alert('Please enter a username');
                return;
            }

            // Get fetch mode and parameters
            let fetchParams = { mode: fetchMode };
            
            // Only add username if not demo mode
            if (fetchMode !== 'demo') {
                fetchParams.username = username;
            }

            if (fetchMode === 'range') {
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                if (!startDate || !endDate) {
                    alert('Please select both start and end dates');
                    return;
                }
                fetchParams.startDate = startDate;
                fetchParams.endDate = endDate;
            } else if (fetchMode === 'days') {
                const daysCount = document.getElementById('daysCount').value;
                if (!daysCount || daysCount < 1) {
                    alert('Please enter a valid number of days');
                    return;
                }
                fetchParams.days = parseInt(daysCount);
            }

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/fetch_games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fetchParams)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startProgressTracking();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        function analyzeGames() {
            // Get username if provided, but don't require it
            const username = document.getElementById('username').value.trim();

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/analyze_games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username || null })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startProgressTracking();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        function analyzeSingleGame(gameId) {
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/analyze_single_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ game_id: gameId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startProgressTracking();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        function showStats() {
            // Show loading state
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('progressText').textContent = 'Loading games...';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/get_games')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('progressSection').style.display = 'none';
                    
                    if (data.success) {
                        displayGames(data.games);
                    } else {
                        alert('Error loading games: ' + data.message);
                    }
                })
                .catch(error => {
                    document.getElementById('progressSection').style.display = 'none';
                    alert('Error: ' + error.message);
                });
        }

        function startProgressTracking() {
            if (progressInterval) clearInterval(progressInterval);

            progressInterval = setInterval(() => {
                fetch('/api/progress')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('progressBar').style.width = data.progress + '%';
                        document.getElementById('progressText').textContent = data.message;

                        if (data.status === 'completed') {
                            clearInterval(progressInterval);
                            document.getElementById('progressSection').style.display = 'none';

                            if (data.results) {
                                displayResults(data.results);
                            } else if (data.result) {
                                displayResults([data.result]);
                            }
                        } else if (data.status === 'error') {
                            clearInterval(progressInterval);
                            document.getElementById('progressSection').style.display = 'none';
                            alert('Error: ' + data.message);
                        }
                    });
            }, 1000);
        }

        function displayResults(results) {
            const container = document.getElementById('resultsContainer');
            container.innerHTML = '';

            results.forEach(result => {
                const div = document.createElement('div');
                div.className = 'analysis-result';
                div.innerHTML = `
                    <h6>Game ${result.game_id}</h6>
                    ${result.white_username && result.black_username ? `<p><strong>Players:</strong> ${result.white_username} (White) vs ${result.black_username} (Black)</p>` : ''}
                    <p><strong>Result:</strong> ${result.result}</p>
                    <p><strong>Analysis:</strong> ${result.analysis}</p>
                    ${result.ai_insights ? `<p><strong>AI Insights:</strong> ${result.ai_insights}</p>` : ''}
                `;
                container.appendChild(div);
            });

            document.getElementById('resultsSection').style.display = 'block';
        }

        function displayGames(games) {
            const container = document.getElementById('resultsContainer');
            container.innerHTML = '';

            if (games.length === 0) {
                container.innerHTML = '<div class="alert alert-info">No games found in database. Try fetching some games first.</div>';
            } else {
                // Add summary
                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'alert alert-success mb-3';
                summaryDiv.innerHTML = `<strong>${games.length}</strong> games found in database`;
                container.appendChild(summaryDiv);

                // Display games
                games.forEach(game => {
                    const div = document.createElement('div');
                    div.className = 'analysis-result';
                    
                    // Format date
                    const date = new Date(game.date * 1000);
                    const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                    
                    div.innerHTML = `
                        <h6>Game ${game.game_id}</h6>
                        <p><strong>Players:</strong> ${game.white_username} (White) vs ${game.black_username} (Black)</p>
                        <p><strong>Result:</strong> ${game.result || 'Unknown'}</p>
                        <p><strong>Time Control:</strong> ${game.time_control || 'Unknown'}</p>
                        <p><strong>Date:</strong> ${dateStr}</p>
                        <div class="mb-2">
                            <button class="btn btn-primary btn-sm me-2" onclick="analyzeSingleGame('${game.game_id}')">
                                <i class="fas fa-brain"></i> Analyze This Game
                            </button>
                        </div>
                        <details>
                            <summary>View PGN</summary>
                            <pre style="white-space: pre-wrap; font-size: 12px; margin-top: 10px;">${game.pgn}</pre>
                        </details>
                    `;
                    container.appendChild(div);
                });
            }

            document.getElementById('resultsSection').style.display = 'block';
        }

        // Load saved credentials on page load
        window.onload = function() {
            fetch('/api/load_credentials')
                .then(response => response.json())
                .then(data => {
                    if (data.username) {
                        document.getElementById('username').value = data.username;
                    }
                });
        };
    </script>
</body>
</html>"""

    with open(templates_dir / 'index.html', 'w') as f:
        f.write(index_html)

def main():
    """Main entry point for the web application."""
    print("🚀 Starting Chess Analyzer Web Interface...")
    print("📱 Initializing components...")

    if not initialize_components():
        print("❌ Failed to initialize components")
        return

    print("✅ Components initialized successfully")

    # Try different ports if 5000 is in use
    ports_to_try = [5000, 5001, 5002, 8080, 8000, 3000, 3001, 4000, 4001, 9000]
    port = None

    for try_port in ports_to_try:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', try_port))
            port = try_port
            break
        except OSError:
            continue

    if port is None:
        print("❌ Error: Could not find an available port")
        return

    print(f"🌐 Starting web server on http://localhost:{port}")
    print("📝 Open your browser and navigate to the URL above")
    print("🛑 Press Ctrl+C to stop the server")

    # Create templates if they don't exist
    create_templates()

    # Write the port to a temp file for the launcher
    import tempfile
    port_file = Path(tempfile.gettempdir()) / "chess_analyzer_port.txt"
    port_file.write_text(str(port))

    # Open browser
    import webbrowser
    import time
    time.sleep(1)  # Give server a moment to start
    webbrowser.open(f'http://localhost:{port}')
    print(f"🌐 Opened web interface in browser at http://localhost:{port}")

    app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)

# Initialize components when the module is imported
initialize_components()

if __name__ == '__main__':
    main()
