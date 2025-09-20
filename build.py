#!/usr/bin/env python3
"""Build script for Chess Analyzer packaging."""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Success")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def build_executable():
    """Build standalone executable using PyInstaller."""
    print("Building Chess Analyzer executable...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single executable file
        "--console",  # Keep console for CLI
        "--name", "ChessAnalyzer",
        "--paths", "src",  # Add src to Python path
        "--hidden-import", "api.client",
        "--hidden-import", "db.database", 
        "--hidden-import", "analysis.analyzer",
        "--hidden-import", "ai.grok_client",
        "--hidden-import", "gui",
        "--hidden-import", "chess",
        "--hidden-import", "chess.com",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "src/main.py"
    ]

    result = run_command(cmd, "PyInstaller build")

    if result:
        print("\n✓ Build completed successfully!")
        print("Executable created at: dist/ChessAnalyzer")

        # Check if executable exists
        exe_path = project_root / "dist" / "ChessAnalyzer"
        if exe_path.exists():
            print(f"File size: {exe_path.stat().st_size} bytes")
        else:
            print("Warning: Executable not found at expected location")

    return result is not None

def build_cli_only():
    """Build CLI-only version without GUI."""
    print("Building CLI-only version...")

    project_root = Path(__file__).parent
    os.chdir(project_root)

    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--console",  # Keep console for CLI
        "--name", "ChessAnalyzer-CLI",
        "--add-data", "src:src",
        "--hidden-import", "chess",
        "--hidden-import", "chess.com",
        "src/main.py"
    ]

    result = run_command(cmd, "CLI-only PyInstaller build")

    if result:
        exe_path = project_root / "dist" / "ChessAnalyzer-CLI"
        if exe_path.exists():
            print(f"CLI executable: {exe_path}")

    return result is not None

def clean_build_artifacts():
    """Clean up build artifacts."""
    print("Cleaning build artifacts...")

    artifacts = [
        "build",
        "dist",
        "*.spec"
    ]

    for artifact in artifacts:
        paths = list(Path(".").glob(artifact))
        for path in paths:
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            else:
                path.unlink()
                print(f"Removed file: {path}")

def main():
    """Main build function."""
    print("Chess Analyzer Build Script")
    print("=" * 40)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller is available")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"], "Install PyInstaller")
        try:
            import PyInstaller
            print("✓ PyInstaller installed")
        except ImportError:
            print("✗ Failed to install PyInstaller")
            return False

    # Clean previous builds
    clean_build_artifacts()

    # Build main executable
    success = build_executable()

    if success:
        # Also build CLI version
        build_cli_only()

        print("\nBuild Summary:")
        print("- Main executable: dist/ChessAnalyzer (GUI + CLI)")
        print("- CLI executable: dist/ChessAnalyzer-CLI (CLI only)")
        print("\nTo run:")
        print("./dist/ChessAnalyzer --gui  # Launch GUI")
        print("./dist/ChessAnalyzer fetch username  # CLI commands")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)