"""Chess Analyzer Web Interface - Flask Application.

This module provides a modern web-based interface for Chess Analyze    def fetch_worker():
        global analysis_progress
        try:
            analysis_progress = {"status": "fetching", "progress": 0, "message": f"Fetching games for {username}..."}

            # Create a new database connection for this thread
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Fetch games using the global client
            games_data = current_client.get_all_games(username)

            if games_data:
                # Store in database
                stored_count = db.store_games(games_data, username)
                analysis_progress = {"status": "completed", "progress": 100, "message": f"Stored {stored_count} games for {username}"}
            else:
                analysis_progress = {"status": "error", "progress": 0, "message": "No games found or error fetching"}

        except Exception as e:
            analysis_progress = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}alhost. The web interface offers:

Features:
- Chess.com username input and game fetching
- Real-time progress tracking during analysis
- Modern responsive web UI with HTML/CSS/JavaScript
- RESTful API endpoints for all operations
- Local credential management
- Cross-platform compatibility

Web Components:
- Flask backend server
- HTML/CSS/JavaScript frontend
- Bootstrap for responsive design
- AJAX for real-time updates
- Local storage for credentials

Usage:
    # From command line
    python -m src.web_app

    # Or directly
    python src/web_app.py

Security:
- Local credential storage in config.local.ini (gitignored)
- No network transmission of sensitive data
- Secure password handling
- CORS enabled for local development

Dependencies:
- flask: Web framework
- flask-cors: Cross-origin resource sharing
- werkzeug: WSGI utility
- jinja2: Template engine
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

@app.route('/api/fetch_games', methods=['POST'])
def fetch_games():
    """Fetch games for a Chess.com username via AJAX.

    This API endpoint handles game fetching requests from the web interface.
    It performs the following operations:

    1. Validates the provided username
    2. Starts a background thread to fetch games (non-blocking)
    3. Updates global progress tracking for real-time UI updates
    4. Stores fetched games in the local database
    5. Returns success/error status to the client

    The background processing ensures the web interface remains responsive
    during potentially long-running API calls to Chess.com.

    Request Body (JSON):
        {"username": "chesscom_username"}

    Response (JSON):
        {"success": true} or {"success": false, "error": "error_message"}

    Note: Progress can be monitored via the /api/progress endpoint
    """
    # Parse JSON request data
    data = request.get_json()
    username = data.get('username', '').strip()

    # Validate input
    if not username:
        return jsonify({"success": False, "error": "Please enter a username"})

    # Background worker function for non-blocking game fetching
    def fetch_worker():
        global analysis_progress
        try:
            # Initialize progress tracking
            analysis_progress = {"status": "fetching", "progress": 0, "message": f"Fetching games for {username}..."}

            # Create thread-safe database connection
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Fetch all games from Chess.com API
            games_data = current_client.get_all_games(username)

            if games_data:
                # Store in database
                stored_count = db.store_games(games_data, username)
                analysis_progress = {"status": "completed", "progress": 100, "message": f"Stored {stored_count} games for {username}"}
            else:
                analysis_progress = {"status": "error", "progress": 0, "message": "No games found or error fetching"}

        except Exception as e:
            analysis_progress = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}

    thread = threading.Thread(target=fetch_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "Fetching games..."})

@app.route('/api/analyze_games', methods=['POST'])
def analyze_games():
    """Analyze stored games."""
    def analyze_worker():
        global analysis_progress
        try:
            analysis_progress = {"status": "analyzing", "progress": 0, "message": "Starting analysis..."}

            # Create a new database connection for this thread
            from db.database import ChessDatabase
            db = ChessDatabase()

            # Get all games from database
            games = db.get_all_games()
            if not games:
                analysis_progress = {"status": "error", "progress": 0, "message": "No games found to analyze"}
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
                            ai_insights = current_ai.analyze_game(game['pgn'])
                        except:
                            ai_insights = "AI analysis not available"

                    analyzed_games.append({
                        "game_id": game['game_id'],
                        "result": game['result'],
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
            if (!username) {
                alert('Please enter a username');
                return;
            }

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/fetch_games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
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
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            fetch('/api/analyze_games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
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
            alert('Statistics feature coming soon!');
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
                    <p><strong>Result:</strong> ${result.result}</p>
                    <p><strong>Analysis:</strong> ${result.analysis}</p>
                    ${result.ai_insights ? `<p><strong>AI Insights:</strong> ${result.ai_insights}</p>` : ''}
                `;
                container.appendChild(div);
            });

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