"""Tkinter GUI for Chess Analyzer."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import threading
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.client import ChessComClient
from db.database import ChessDatabase
from analysis.analyzer import ChessAnalyzer
from ai.grok_client import GrokClient

class ChessAnalyzerGUI:
    """Main GUI application for Chess Analyzer."""

    def __init__(self, root):
        self.root = root
        self.root.title("Chess Analyzer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Initialize components
        self.db = ChessDatabase()
        self.analyzer = ChessAnalyzer()
        self.ai_client = GrokClient()

        # Create GUI elements
        self._create_widgets()
        self._layout_widgets()

        # Status tracking
        self.current_games = []

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        # Username input
        ttk.Label(self.main_frame, text="Chess.com Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Action buttons
        self.fetch_button = ttk.Button(self.buttons_frame, text="Fetch Games", command=self._fetch_games)
        self.fetch_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = ttk.Button(self.buttons_frame, text="Analyze Games", command=self._analyze_games, state=tk.DISABLED)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.stats_button = ttk.Button(self.buttons_frame, text="Show Stats", command=self._show_stats)
        self.stats_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(self.buttons_frame, text="Clear", command=self._clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Output area
        ttk.Label(self.main_frame, text="Output:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.main_frame, height=20, wrap=tk.WORD)
        self.output_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def _layout_widgets(self):
        """Configure widget layout and styling."""
        # Configure text tags for output formatting
        self.output_text.tag_configure("header", font=("TkDefaultFont", 10, "bold"))
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("success", foreground="green")
        self.output_text.tag_configure("info", foreground="blue")

    def _fetch_games(self):
        """Fetch games for the entered username."""
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a Chess.com username")
            return

        self._set_status("Fetching games...")
        self.fetch_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

        # Run fetch in background thread
        thread = threading.Thread(target=self._fetch_games_worker, args=(username,))
        thread.daemon = True
        thread.start()

    def _fetch_games_worker(self, username):
        """Worker function to fetch games in background."""
        try:
            client = ChessComClient()
            self._log_output(f"Fetching games for {username}...\n", "info")

            games = client.get_all_games(username)
            if games:
                self.db.insert_games_batch(games)
                self.current_games = games
                self._log_output(f"Successfully fetched {len(games)} games\n", "success")
                self.analyze_button.config(state=tk.NORMAL)
            else:
                self._log_output("No games found or unable to fetch\n", "error")

        except Exception as e:
            self._log_output(f"Error fetching games: {e}\n", "error")
        finally:
            self.fetch_button.config(state=tk.NORMAL)
            self._set_status("Ready")
            self.progress_var.set(100)

    def _analyze_games(self):
        """Analyze the fetched games."""
        if not self.current_games:
            # Try to load from database
            username = self.username_var.get().strip()
            if username:
                self.current_games = self.db.get_games_by_username(username, limit=5)

        if not self.current_games:
            messagebox.showerror("Error", "No games available for analysis")
            return

        self._set_status("Analyzing games...")
        self.analyze_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

        # Run analysis in background thread
        thread = threading.Thread(target=self._analyze_games_worker)
        thread.daemon = True
        thread.start()

    def _analyze_games_worker(self):
        """Worker function to analyze games in background."""
        try:
            total_games = len(self.current_games)
            total_blunders = 0
            total_mistakes = 0

            for i, game in enumerate(self.current_games):
                self._log_output(f"\nAnalyzing game {i+1}/{total_games}: {game['game_id']}\n", "header")

                analysis = self.analyzer.analyze_game(game['pgn'])

                if 'error' in analysis:
                    self._log_output(f"Error: {analysis['error']}\n", "error")
                    continue

                summary = analysis['summary']
                self._log_output(f"Moves: {summary['total_moves']}\n", "info")
                self._log_output(f"Blunders: {summary['blunder_count']}\n", "error")
                self._log_output(f"Mistakes: {summary['mistake_count']}\n", "error")
                self._log_output(f"Accuracy: {summary['accuracy']:.1f}%\n", "info")

                # Show top blunders
                blunders = analysis['blunders'][:3]
                if blunders:
                    self._log_output("Top blunders:\n", "error")
                    for blunder in blunders:
                        self._log_output(f"  Move {blunder['move_number']}: {blunder['move']} "
                                       f"(lost {blunder['score_change']} cp)\n", "error")

                # Get AI advice
                self._log_output("\nAI Analysis:\n", "header")
                advice = self.ai_client.get_chess_advice(game['pgn'], analysis)
                self._log_output(f"{advice}\n", "info")

                total_blunders += summary['blunder_count']
                total_mistakes += summary['mistake_count']

                # Update progress
                self.progress_var.set((i + 1) / total_games * 100)

            self._log_output(f"\nOverall: {total_blunders} blunders, {total_mistakes} mistakes "
                           f"across {total_games} games\n", "success")

        except Exception as e:
            self._log_output(f"Error during analysis: {e}\n", "error")
        finally:
            self.analyze_button.config(state=tk.NORMAL)
            self._set_status("Ready")

    def _show_stats(self):
        """Show player statistics."""
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a Chess.com username")
            return

        self._set_status("Fetching stats...")
        self.stats_button.config(state=tk.DISABLED)

        # Run stats in background thread
        thread = threading.Thread(target=self._show_stats_worker, args=(username,))
        thread.daemon = True
        thread.start()

    def _show_stats_worker(self, username):
        """Worker function to fetch stats in background."""
        try:
            client = ChessComClient()
            self._log_output(f"\nFetching stats for {username}...\n", "header")

            stats_data = client.get_player_stats(username)
            profile = client.get_player_profile(username)

            self._log_output(f"Player: {profile.get('username', username)}\n", "info")
            self._log_output(f"Name: {profile.get('name', 'N/A')}\n", "info")
            self._log_output(f"Country: {profile.get('country', 'N/A')}\n", "info")
            self._log_output(f"Joined: {profile.get('joined', 'N/A')}\n", "info")

            # Display ratings
            if 'chess_rapid' in stats_data:
                rapid = stats_data['chess_rapid']
                self._log_output(f"Rapid Rating: {rapid.get('last', {}).get('rating', 'N/A')}\n", "info")
            if 'chess_blitz' in stats_data:
                blitz = stats_data['chess_blitz']
                self._log_output(f"Blitz Rating: {blitz.get('last', {}).get('rating', 'N/A')}\n", "info")
            if 'chess_bullet' in stats_data:
                bullet = stats_data['chess_bullet']
                self._log_output(f"Bullet Rating: {bullet.get('last', {}).get('rating', 'N/A')}\n", "info")

        except Exception as e:
            self._log_output(f"Error fetching stats: {e}\n", "error")
        finally:
            self.stats_button.config(state=tk.NORMAL)
            self._set_status("Ready")

    def _clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
        self.current_games = []
        self.analyze_button.config(state=tk.DISABLED)

    def _log_output(self, text, tag=None):
        """Add text to the output area with optional formatting."""
        self.output_text.insert(tk.END, text, tag)
        self.output_text.see(tk.END)  # Auto-scroll to bottom

    def _set_status(self, text):
        """Update the status bar."""
        self.status_var.set(text)
        self.root.update_idletasks()

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()
        if hasattr(self, 'analyzer'):
            self.analyzer.close()


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = ChessAnalyzerGUI(root)

    # Handle cleanup on window close
    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    app.run()


if __name__ == "__main__":
    main()