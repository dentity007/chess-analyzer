#!/bin/bash
# Chess Analyzer macOS Installer Creator
# ======================================
#
# This script creates a professional DMG installer for the Chess Analyzer
# macOS application. The installer includes:
# - ChessAnalyzer.app bundle
# - Applications folder shortcut for easy installation
# - Professional DMG appearance with custom background
# - Volume icon and proper metadata

set -e  # Exit on any error

# Configuration
APP_NAME="Chess Analyzer"
APP_BUNDLE="ChessAnalyzer.app"
DMG_NAME="ChessAnalyzer-Installer.dmg"
VOLUME_NAME="Chess Analyzer Installer"
SOURCE_DIR="dist"
OUTPUT_DIR="dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    log_error "This script is designed for macOS only"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    log_error "Please run this script from the chess-analyzer root directory"
    exit 1
fi

log_info "Starting Chess Analyzer macOS Installer creation..."

# Step 1: Build the application if it doesn't exist
if [[ ! -d "$SOURCE_DIR/$APP_BUNDLE" ]]; then
    log_info "Building ChessAnalyzer.app..."
    if [[ -f "build_macos.sh" ]]; then
        ./build_macos.sh
    else
        log_error "build_macos.sh not found. Please build the app first."
        exit 1
    fi
else
    log_info "Using existing ChessAnalyzer.app"
fi

# Step 2: Install create-dmg if not available
if ! command -v create-dmg &> /dev/null; then
    log_info "Installing create-dmg tool..."
    if command -v brew &> /dev/null; then
        brew install create-dmg
    else
        log_error "Homebrew not found. Please install create-dmg manually:"
        log_error "  brew install create-dmg"
        log_error "Or visit: https://github.com/create-dmg/create-dmg"
        exit 1
    fi
fi

# Step 3: Create DMG resources directory and copy README
DMG_RESOURCES_DIR="dmg_resources"
mkdir -p "$DMG_RESOURCES_DIR"

# Copy README to resources
if [[ -f "README-Installer.txt" ]]; then
    cp "README-Installer.txt" "$DMG_RESOURCES_DIR/"
fi

# Step 4: Create the DMG
log_info "Creating DMG installer..."

# Remove existing DMG if it exists
if [[ -f "$OUTPUT_DIR/$DMG_NAME" ]]; then
    rm -f "$OUTPUT_DIR/$DMG_NAME"
fi

# Create DMG with create-dmg
create-dmg \
    --volname "$VOLUME_NAME" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "$APP_BUNDLE" 200 190 \
    --hide-extension "$APP_BUNDLE" \
    --app-drop-link 600 185 \
    --add-file "README.txt" "README-Installer.txt" 400 300 \
    --disk-image-size 100 \
    --no-internet-enable \
    "$OUTPUT_DIR/$DMG_NAME" \
    "$SOURCE_DIR/"

# Check if DMG was created successfully
if [[ -f "$OUTPUT_DIR/$DMG_NAME" ]]; then
    DMG_SIZE=$(du -h "$OUTPUT_DIR/$DMG_NAME" | cut -f1)
    log_success "DMG installer created successfully: $OUTPUT_DIR/$DMG_NAME ($DMG_SIZE)"
    log_info "To distribute the app:"
    log_info "  1. The DMG contains ChessAnalyzer.app and an Applications shortcut"
    log_info "  2. Users can drag ChessAnalyzer.app to their Applications folder"
    log_info "  3. The app is ready to run without installation"
else
    log_error "Failed to create DMG installer"
    exit 1
fi

log_success "Chess Analyzer macOS installer creation completed!"
log_info "Output: $OUTPUT_DIR/$DMG_NAME"
log_info ""
log_info "Installation Instructions for Users:"
log_info "  1. Open the DMG file"
log_info "  2. Drag ChessAnalyzer.app to the Applications shortcut"
log_info "  3. The app is now installed and ready to use"
log_info ""
log_info "The app will appear in Launchpad and can be added to the Dock"