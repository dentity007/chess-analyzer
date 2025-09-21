#!/usr/bin/env python3
"""Chess Analyzer Web Interface Launcher.

This script provides a cross-platform way to start the Chess Analyzer web interface.
It handles dependency installation and launches the Flask web application.

Usage:
    python start_web.py

Or on Unix systems:
    ./start_web.py

Features:
- Automatic dependency installation
- Cross-platform compatibility
- Web browser auto-launch
- Error handling and user feedback
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def install_dependencies():
    """Install required Python dependencies."""
    print("📦 Installing/updating dependencies...")

    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        print("✅ Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_web_app():
    """Start the Flask web application."""
    print("🌐 Starting Chess Analyzer Web Interface...")
    print("📱 The application will be available at: http://localhost:5000 (or next available port)")
    print("🛑 Press Ctrl+C to stop the server")
    print("")

    try:
        # Import and run the web app directly (it will block)
        from src.web_app import main
        main()

    except ImportError as e:
        print(f"❌ Error importing web app: {e}")
        print("💡 Make sure all dependencies are installed")
        return False

    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
        return True

    except Exception as e:
        print(f"❌ Error starting web app: {e}")
        return False

def open_browser(port):
    """Open the web interface in the default browser."""
    try:
        # Wait a moment for the server to start
        time.sleep(3)
        webbrowser.open(f'http://localhost:{port}')
        print(f"🌐 Opened web interface in browser at http://localhost:{port}")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"📱 Please open http://localhost:{port} in your web browser")

def main():
    """Main launcher function."""
    print("🚀 Chess Analyzer Web Interface Launcher")
    print("========================================")

    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found.")
        print("💡 Please run this script from the chess-analyzer root directory.")
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    # Open browser first
    import tempfile
    import time

    # Wait for the port file to be created (in case it exists from previous run)
    port_file = Path(tempfile.gettempdir()) / "chess_analyzer_port.txt"
    port = 5000  # default fallback

    # Start the web application (this will block)
    return start_web_app()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)