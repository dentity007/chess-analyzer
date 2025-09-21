#!/bin/bash

# Chess Analyzer Web Interface Launcher
# This script installs dependencies and starts the web interface

echo "🚀 Chess Analyzer Web Interface Launcher"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the chess-analyzer root directory."
    exit 1
fi

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Start the web application
echo "🌐 Starting Chess Analyzer Web Interface..."
echo "📱 The application will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python -m src.web_app