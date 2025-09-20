#!/bin/bash
# Simple macOS Build Script for Chess Analyzer
# ============================================
#
# Quick build script for creating macOS executable
# Usage: ./build_simple.sh

echo "🔨 Building Chess Analyzer (Simple macOS Build)..."

# Use virtual environment Python
PYTHON="/Users/nmaine/local copy github/chess analyzer/.venv/bin/python"

# Clean previous builds
rm -rf dist build

# Build with PyInstaller
"$PYTHON" -m PyInstaller \
    --onefile \
    --windowed \
    --name ChessAnalyzer \
    --add-data "src:src" \
    --hidden-import chess \
    --hidden-import chess.engine \
    --hidden-import requests \
    --hidden-import click \
    --hidden-import configparser \
    src/main.py

echo "✅ Build completed!"
echo "📱 Executable: dist/ChessAnalyzer"
echo "🚀 Run with: ./dist/ChessAnalyzer --gui"