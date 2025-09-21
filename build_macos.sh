#!/bin/bash
# Chess Analyzer - macOS Build Script
# ===================================
#
# This script builds a standalone macOS application bundle for Chess Analyzer
# using PyInstaller with macOS-specific optimizations.
#
# Requirements:
# - macOS
# - Python 3.8+
# - PyInstaller
# - All project dependencies installed
#
# Output:
# - ChessAnalyzer.app: macOS application bundle
# - dist/ChessAnalyzer: Command-line executable
#
# Usage:
#   ./build_macos.sh
#

set -e  # Exit on any error

echo "🏗️  Building Chess Analyzer for macOS..."
echo "========================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is designed for macOS only"
    echo "   Current OS: $OSTYPE"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(/Users/nmaine/local\ copy\ github/chess\ analyzer/.venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

# Set up paths
PROJECT_ROOT="/Users/nmaine/local copy github/chess analyzer"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
SYSTEM_PYTHON="/usr/local/bin/python3"  # Use system Python for tkinter support
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Distribution directory: $DIST_DIR"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR"
mkdir -p "$DIST_DIR" "$BUILD_DIR"

# Check if system Python is available
# Note: System Python is preferred for tkinter support on macOS
if [ ! -f "$SYSTEM_PYTHON" ]; then
    echo "❌ Error: System Python not found at $SYSTEM_PYTHON"
    echo "   Trying virtual environment Python..."
    PYTHON_CMD="$VENV_PYTHON"
else
    echo "✅ Using system Python for tkinter support"
    PYTHON_CMD="$SYSTEM_PYTHON"
fi

# Check if PyInstaller is available
# PyInstaller is required for creating standalone executables
if ! "$PYTHON_CMD" -c "import PyInstaller" 2>/dev/null; then
    echo "❌ Error: PyInstaller not found"
    echo "   Please run: pip3 install pyinstaller"
    exit 1
fi

# Check if all dependencies are installed
# This ensures the build won't fail due to missing imports
echo "📦 Checking dependencies..."
if ! "$PYTHON_CMD" -c "import chess, requests, click, tkinter" 2>/dev/null; then
    echo "❌ Error: Missing required dependencies"
    echo "   Please run: pip3 install -r requirements.txt"
    exit 1
fi

# Create PyInstaller spec file for macOS
# The spec file contains PyInstaller configuration specific to macOS builds
echo "📝 Creating PyInstaller spec file..."
cat > "$PROJECT_ROOT/ChessAnalyzer_macos.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Add the src directory to the path
project_root = '$PROJECT_ROOT'
sys.path.insert(0, os.path.join(project_root, 'src'))

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'chess',
        'chess.engine',
        'chess.pgn',
        'requests',
        'click',
        'tkinter',
        'configparser',
        'PIL',  # If using PIL/Pillow
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'test',
        'unittest',
        'pdb',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChessAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI-only app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ChessAnalyzer.app',
    icon=None,  # Add icon file path if available
    bundle_identifier='com.chessanalyzer.app',
    version='0.1.0',
    info_plist={
        'CFBundleDisplayName': 'Chess Analyzer',
        'CFBundleName': 'Chess Analyzer',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'CFBundleIdentifier': 'com.chessanalyzer.app',
        'LSMinimumSystemVersion': '10.12.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
EOF

echo "✅ Spec file created: ChessAnalyzer_macos.spec"

# Build the application using PyInstaller
# This is the main build step that creates the macOS app bundle
"$PYTHON_CMD" -m PyInstaller \
    --clean \
    --noconfirm \
    "$PROJECT_ROOT/ChessAnalyzer_macos.spec"

# Check if build was successful
# Verify that the macOS app bundle was created
if [ ! -d "$DIST_DIR/ChessAnalyzer.app" ]; then
    echo "❌ Error: Build failed - ChessAnalyzer.app not found"
    exit 1
fi

# Check for standalone executable (only if console=True in spec)
# Note: For GUI apps, we typically only get the .app bundle, not a separate executable
if [ ! -f "$DIST_DIR/ChessAnalyzer" ]; then
    echo "⚠️  Warning: Standalone executable not found (expected for GUI app)"
    echo "   This is normal when building a GUI application bundle"
fi

# Make the executable inside the app bundle executable
# This ensures the app can be launched properly
# Make executables executable
chmod +x "$DIST_DIR/ChessAnalyzer.app/Contents/MacOS/ChessAnalyzer"

# Fix Info.plist to remove LSBackgroundOnly for GUI app
if [ -f "$DIST_DIR/ChessAnalyzer.app/Contents/Info.plist" ]; then
    echo "🔧 Fixing Info.plist for GUI app..."
    # Remove LSBackgroundOnly entry to make app double-clickable
    plutil -remove LSBackgroundOnly "$DIST_DIR/ChessAnalyzer.app/Contents/Info.plist" 2>/dev/null || true
fi

# Get file sizes for reporting
APP_SIZE=$(du -sh "$DIST_DIR/ChessAnalyzer.app" | cut -f1)
if [ -f "$DIST_DIR/ChessAnalyzer" ]; then
    EXE_SIZE=$(du -sh "$DIST_DIR/ChessAnalyzer" | cut -f1)
    EXE_INFO="💻 Command Line Tool: $DIST_DIR/ChessAnalyzer ($EXE_SIZE)"
else
    EXE_INFO="💻 Command Line Tool: Not built (GUI-only app)"
fi

# Display success message with usage instructions
echo ""
echo "🎉 Build completed successfully!"
echo "================================="
echo "📱 macOS Application: $DIST_DIR/ChessAnalyzer.app ($APP_SIZE)"
echo "$EXE_INFO"
echo ""
echo "🚀 To test the application:"
echo "   GUI:    open $DIST_DIR/ChessAnalyzer.app"
echo "   CLI:    $DIST_DIR/ChessAnalyzer.app/Contents/MacOS/ChessAnalyzer --help"
echo ""
echo "📦 Ready for distribution!"
echo "   - ChessAnalyzer.app can be distributed as a macOS app"
echo "   - No Python installation required on target machines"
echo "   - First run may be slower due to bytecode optimization"