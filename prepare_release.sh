#!/bin/bash
# Chess Analyzer - Release Preparation Script
# ===========================================
#
# This script prepares the macOS application bundle for GitHub release
# and provides instructions for uploading to GitHub Releases.
#
# Usage:
#   ./prepare_release.sh
#

set -e

echo "🎯 Chess Analyzer - Release Preparation"
echo "======================================"

PROJECT_ROOT="/Users/nmaine/local copy github/chess analyzer"
DIST_DIR="$PROJECT_ROOT/dist"
APP_PATH="$DIST_DIR/ChessAnalyzer.app"

# Check if app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: ChessAnalyzer.app not found in $DIST_DIR"
    echo "   Please run ./build_macos.sh first"
    exit 1
fi

# Get app size
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo "📱 macOS Application: $APP_PATH ($APP_SIZE)"

# Create release archive (optional, for easier upload)
echo ""
echo "📦 Creating release archive..."
cd "$DIST_DIR"
tar -czf ChessAnalyzer-v0.1.0-macos.tar.gz ChessAnalyzer.app
ARCHIVE_SIZE=$(du -sh ChessAnalyzer-v0.1.0-macos.tar.gz | cut -f1)
echo "✅ Release archive created: ChessAnalyzer-v0.1.0-macos.tar.gz ($ARCHIVE_SIZE)"

echo ""
echo "🚀 GitHub Release Instructions:"
echo "=============================="
echo ""
echo "1. Go to: https://github.com/dentity007/chess-analyzer/releases"
echo "2. Click 'Create a new release'"
echo "3. Choose tag: v0.1.0-macos"
echo "4. Title: Chess Analyzer v0.1.0 - macOS"
echo "5. Description:"
echo "   This release includes the ChessAnalyzer.app - a fully functional"
echo "   macOS application bundle (35MB) with all dependencies bundled."
echo ""
echo "   Features:"
echo "   - Chess.com API integration"
echo "   - Stockfish engine analysis"
echo "   - xAI Grok AI improvement suggestions"
echo "   - SQLite local database"
echo "   - Tkinter GUI interface"
echo "   - No Python installation required"
echo ""
echo "   Installation:"
echo "   1. Download ChessAnalyzer.app"
echo "   2. Double-click to launch"
echo "   3. Or use: ./ChessAnalyzer.app/Contents/MacOS/ChessAnalyzer --help"
echo ""
echo "6. Upload files:"
echo "   - ChessAnalyzer.app (drag and drop)"
echo "   - OR ChessAnalyzer-v0.1.0-macos.tar.gz (smaller, compressed)"
echo ""
echo "7. Click 'Publish release'"
echo ""
echo "📋 Alternative: Upload to feature/mac-executable branch"
echo "======================================================"
echo "If you prefer to upload to the branch instead of a release:"
echo ""
echo "1. Copy ChessAnalyzer.app to a separate location"
echo "2. Create a new branch from feature/mac-executable:"
echo "   git checkout -b releases/macos-v0.1.0"
echo "3. Add the app bundle:"
echo "   git add ChessAnalyzer.app"
echo "   git commit -m 'Add macOS application bundle v0.1.0'"
echo "   git push origin releases/macos-v0.1.0"
echo ""
echo "⚠️  Note: Adding large binaries to git will bloat the repository."
echo "   GitHub Releases is the recommended approach for distribution."