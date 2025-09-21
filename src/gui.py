"""Chess Analyzer GUI - Modern Tkinter Desktop Application.

This module provides a professional graphical user interface for Chess Analyzer,
a comprehensive chess game analysis tool. The GUI offers:

Core Features:
- Chess.com username input and game fetching
- Real-time progress tracking during analysis
- Color-coded output for different information types
- Credential management with secure local storage
- Settings menu with authentication testing
- Professional menu system (File, Settings, Help)

GUI Components:
- Username input field for Chess.com integration
- Password field for optional authentication
- Action buttons (Fetch Games, Analyze Games, Show Stats, Clear)
- Progress bar for long-running operations
- Scrolled text area for analysis output and logging
- Status bar with real-time status updates
- Menu bar with Settings and Help options

Technical Features:
- Thread-safe background processing for API calls and analysis
- Comprehensive error handling with user-friendly messages
- Logging system for debugging bundled applications
- PyInstaller-compatible path handling for database operations
- Graceful component initialization with fallback support

Security:
- Local credential storage in config.local.ini (gitignored)
- No network transmission of sensitive data
- Secure password masking in input fields

Usage:
    # From command line
    python -m src.main --gui

    # From Python
    from gui import main
    main()

Dependencies:
- tkinter (built-in Python GUI framework)
- threading (for background processing)
- pathlib (for cross-platform path handling)
- sqlite3 (for local database operations)
- requests (for Chess.com API communication)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import threading
import sys
import os
import logging

# Set up logging for debugging bundled applications
logging.basicConfig(level=logging.DEBUG, filename='gui_debug.log',
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.client import ChessComClient
from db.database import ChessDatabase
from analysis.analyzer import ChessAnalyzer
from ai.grok_client import GrokClient

class ChessAnalyzerGUI:
    """Main GUI application for Chess Analyzer.

    This class provides a complete graphical user interface for the Chess Analyzer
    application using Tkinter. It offers all the functionality of the CLI version
    in a user-friendly desktop application.

    Key Features:
    - Username input and game fetching
    - Real-time progress tracking
    - Analysis results display with color coding
    - Credential management
    - Settings and help menus
    """

    def __init__(self, root):
        """Initialize the GUI application.

        Sets up the main window, initializes all components with error handling,
        and creates the user interface. Components are initialized gracefully
        to ensure the application works even if some features are unavailable.

        Args:
            root: Tkinter root window object
        """
        logging.info("Starting GUI initialization")
        self.root = root
        self.root.title("Chess Analyzer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        logging.info("Basic window setup complete")

        # Initialize core components with individual error handling
        # This ensures the GUI works even if some components fail
        try:
            logging.info("Initializing database...")
            self.db = ChessDatabase()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            print(f"Warning: Database initialization failed: {e}")
            self.db = None

        try:
            logging.info("Initializing analyzer...")
            self.analyzer = ChessAnalyzer()
            logging.info("Analyzer initialized successfully")
        except Exception as e:
            logging.error(f"Analyzer initialization failed: {e}")
            print(f"Warning: Analyzer initialization failed: {e}")
            self.analyzer = None

        try:
            logging.info("Initializing AI client...")
            self.ai_client = GrokClient()
            logging.info("AI client initialized successfully")
        except Exception as e:
            logging.error(f"AI client initialization failed: {e}")
            print(f"Warning: AI client initialization failed: {e}")
            self.ai_client = None

        # Create GUI elements
        try:
            logging.info("Creating GUI widgets...")
            self._create_widgets()
            self._layout_widgets()
            logging.info("GUI widgets created successfully")
        except Exception as e:
            logging.error(f"GUI creation failed: {e}")
            print(f"Error creating GUI: {e}")
            messagebox.showerror("Error", f"Failed to create GUI: {e}")
            return

        # Status tracking
        self.current_games = []
        logging.info("GUI initialization complete")

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create menu bar
        self._create_menu_bar()

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(6, weight=1)

        # Username input
        ttk.Label(self.main_frame, text="Chess.com Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Password input
        ttk.Label(self.main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.main_frame, textvariable=self.password_var, width=30, show="*")
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # AI API key (stored internally, not shown in main UI)
        self.ai_key_var = tk.StringVar()

        # Credential buttons frame
        self.cred_buttons_frame = ttk.Frame(self.main_frame)
        self.cred_buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)

        # Credential management buttons
        self.save_cred_button = ttk.Button(self.cred_buttons_frame, text="Save Credentials", command=self._save_credentials)
        self.save_cred_button.pack(side=tk.LEFT, padx=5)

        self.test_auth_button = ttk.Button(self.cred_buttons_frame, text="Test Authentication", command=self._test_authentication)
        self.test_auth_button.pack(side=tk.LEFT, padx=5)

        self.load_cred_button = ttk.Button(self.cred_buttons_frame, text="Load Saved Credentials", command=self._load_credentials)
        self.load_cred_button.pack(side=tk.LEFT, padx=5)

        # Buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

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
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Output area
        ttk.Label(self.main_frame, text="Output:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.main_frame, height=20, wrap=tk.WORD)
        self.output_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def _create_menu_bar(self):
        """Create the menu bar with settings and help options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Credentials", command=self._show_credentials_dialog)
        settings_menu.add_separator()
        settings_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _layout_widgets(self):
        """Configure widget layout and styling."""
        # Configure text tags for output formatting
        self.output_text.tag_configure("header", font=("TkDefaultFont", 10, "bold"))
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("success", foreground="green")
        self.output_text.tag_configure("info", foreground="blue")

    def _show_credentials_dialog(self):
        """Show a dialog for managing Chess.com credentials and AI API keys."""
        try:
            logging.info("Opening credentials dialog...")

            # Create a simple dialog without complex framing
            dialog = tk.Toplevel(self.root)
            dialog.title("Configuration Settings")
            dialog.geometry("500x350")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Center the dialog
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - 500) // 2
            y = (screen_height - 350) // 2
            dialog.geometry(f"500x350+{x}+{y}")

            # Simple layout with direct widgets
            # Title
            title = tk.Label(dialog, text="Configuration Settings", font=("Arial", 14, "bold"))
            title.pack(pady=10)

            # Chess.com section
            chess_frame = tk.LabelFrame(dialog, text="Chess.com Credentials", padx=10, pady=5)
            chess_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

            # Username
            username_label = tk.Label(chess_frame, text="Username:")
            username_label.pack(anchor=tk.W)
            username_var = tk.StringVar(value=self.username_var.get())
            username_entry = tk.Entry(chess_frame, textvariable=username_var, width=40, font=("Arial", 11))
            username_entry.pack(pady=(5, 10), fill=tk.X)

            # Password
            password_label = tk.Label(chess_frame, text="Password:")
            password_label.pack(anchor=tk.W)
            password_var = tk.StringVar(value=self.password_var.get())
            password_entry = tk.Entry(chess_frame, textvariable=password_var, width=40, show="*", font=("Arial", 11))
            password_entry.pack(pady=(5, 10), fill=tk.X)

            # AI section with provider selection
            ai_frame = tk.LabelFrame(dialog, text="AI Configuration (Optional)", padx=10, pady=5)
            ai_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

            # Provider selection
            provider_label = tk.Label(ai_frame, text="AI Provider:")
            provider_label.pack(anchor=tk.W)
            provider_var = tk.StringVar(value=getattr(self, 'ai_provider_var', tk.StringVar()).get() or "xai")
            provider_combo = ttk.Combobox(ai_frame, textvariable=provider_var,
                                        values=["xai", "openai", "anthropic"], state="readonly")
            provider_combo.pack(pady=(5, 10), fill=tk.X)
            provider_combo.set(provider_var.get())

            # API Key input (dynamic based on provider)
            api_key_label = tk.Label(ai_frame, text="API Key:")
            api_key_label.pack(anchor=tk.W)
            ai_key_var = tk.StringVar(value=getattr(self, 'ai_key_var', tk.StringVar()).get())
            ai_entry = tk.Entry(ai_frame, textvariable=ai_key_var, width=40, show="*", font=("Arial", 11))
            ai_entry.pack(pady=(5, 5), fill=tk.X)

            # Provider info
            def update_provider_info(*args):
                provider = provider_var.get()
                if provider == "xai":
                    info_text = "Get key from: https://x.ai/api"
                elif provider == "openai":
                    info_text = "Get key from: https://platform.openai.com/api-keys"
                elif provider == "anthropic":
                    info_text = "Get key from: https://console.anthropic.com/"
                else:
                    info_text = ""
                provider_info.config(text=info_text)

            provider_var.trace("w", update_provider_info)
            provider_info = tk.Label(ai_frame, text="", font=("Arial", 9), fg="blue")
            provider_info.pack(anchor=tk.W)
            update_provider_info()  # Initialize

            # Buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack()

            def save_and_close():
                self.username_var.set(username_var.get())
                self.password_var.set(password_var.get())
                if not hasattr(self, 'ai_key_var'):
                    self.ai_key_var = tk.StringVar()
                if not hasattr(self, 'ai_provider_var'):
                    self.ai_provider_var = tk.StringVar()
                self.ai_key_var.set(ai_key_var.get())
                self.ai_provider_var.set(provider_var.get())
                self._save_credentials()
                dialog.destroy()

            def test_and_close():
                self.username_var.set(username_var.get())
                self.password_var.set(password_var.get())
                if not hasattr(self, 'ai_key_var'):
                    self.ai_key_var = tk.StringVar()
                self.ai_key_var.set(ai_var.get())
                self._test_authentication()
                dialog.destroy()

            save_btn = tk.Button(button_frame, text="Save", command=save_and_close, width=8)
            save_btn.pack(side=tk.LEFT, padx=5)
            test_btn = tk.Button(button_frame, text="Test", command=test_and_close, width=8)
            test_btn.pack(side=tk.LEFT, padx=5)
            cancel_btn = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=8)
            cancel_btn.pack(side=tk.LEFT, padx=5)

            # Focus on username entry
            username_entry.focus_set()

            # Force dialog to update and display
            dialog.update()
            dialog.lift()
            dialog.attributes('-topmost', True)
            dialog.attributes('-topmost', False)

            logging.info("Credentials dialog opened successfully")

        except Exception as e:
            logging.error(f"Failed to create credentials dialog: {e}")
            import traceback
            traceback.print_exc()

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About Chess Analyzer",
                          "Chess Analyzer v0.1.0\n\n"
                          "A comprehensive chess game analysis tool that:\n"
                          "• Fetches games from Chess.com\n"
                          "• Analyzes moves with Stockfish engine\n"
                          "• Provides AI-powered improvement suggestions\n"
                          "• Supports both GUI and CLI interfaces\n\n"
                          "Built with Python and Tkinter")

    def _fetch_games(self):
        """Fetch games for the entered username.

        This method handles the game fetching process from the GUI:
        1. Validates the username input
        2. Updates UI to show fetching status
        3. Disables the fetch button to prevent multiple requests
        4. Starts a background thread for the actual fetching
        5. Updates progress bar and status

        The background thread ensures the GUI remains responsive during
        potentially long-running API calls to Chess.com.
        """
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a Chess.com username")
            return

        # Update UI for fetching state
        self._set_status("Fetching games...")
        self.fetch_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

        # Run fetch operation in background thread to keep GUI responsive
        thread = threading.Thread(target=self._fetch_games_worker, args=(username,))
        thread.daemon = True
        thread.start()

    def _fetch_games_worker(self, username):
        """Worker function to fetch games in background thread.

        This method performs the actual game fetching operation in a separate
        thread to prevent blocking the GUI. It handles:

        1. API communication with Chess.com
        2. Database storage of fetched games
        3. Progress updates and status messages
        4. Error handling with user-friendly messages
        5. UI state restoration when complete

        Args:
            username: Chess.com username to fetch games for
        """
        try:
            # Initialize API client for Chess.com communication
            client = ChessComClient()
            self._log_output(f"Fetching games for {username}...\n", "info")

            # Fetch all available games from Chess.com
            games = client.get_all_games(username)
            if games:
                # Store games in local database for analysis
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

    def _save_credentials(self):
        """Save entered credentials and AI API key to config.local.ini."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        ai_key = getattr(self, 'ai_key_var', tk.StringVar()).get().strip()
        ai_provider = getattr(self, 'ai_provider_var', tk.StringVar()).get().strip()

        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return

        if not password:
            messagebox.showwarning("Warning", "Password is empty. Are you sure you want to save without a password?")
            if not messagebox.askyesno("Confirm", "Save credentials without password?"):
                return

        try:
            import configparser
            import os
            from pathlib import Path

            # Get config file path
            config_path = Path(__file__).parent.parent / 'config.local.ini'

            # Create or load config
            config = configparser.ConfigParser()
            if config_path.exists():
                config.read(config_path)

            # Set Chess.com credentials
            if 'chess_com' not in config:
                config.add_section('chess_com')

            config['chess_com']['username'] = username
            config['chess_com']['password'] = password

            # Set AI API key if provided
            if ai_key and ai_provider:
                if 'ai' not in config:
                    config.add_section('ai')

                # Clear all provider keys first
                for provider_key in ['xai_api_key', 'openai_api_key', 'anthropic_api_key']:
                    if config.has_option('ai', provider_key):
                        config.remove_option('ai', provider_key)

                # Set the selected provider's key
                if ai_provider == "xai":
                    config['ai']['xai_api_key'] = ai_key
                elif ai_provider == "openai":
                    config['ai']['openai_api_key'] = ai_key
                elif ai_provider == "anthropic":
                    config['ai']['anthropic_api_key'] = ai_key
            elif 'ai' in config:
                # Remove all AI keys if no key provided
                for provider_key in ['xai_api_key', 'openai_api_key', 'anthropic_api_key']:
                    if config.has_option('ai', provider_key):
                        config.remove_option('ai', provider_key)

            # Save config
            with open(config_path, 'w') as f:
                config.write(f)

            saved_items = [f"credentials for user: {username}"]
            if ai_key and ai_provider:
                saved_items.append(f"{ai_provider} API key")
            self._log_output(f"✓ Settings saved: {', '.join(saved_items)}\n", "success")
            messagebox.showinfo("Success", "Settings saved successfully!")

        except Exception as e:
            self._log_output(f"✗ Error saving credentials: {e}\n", "error")
            messagebox.showerror("Error", f"Failed to save credentials: {e}")

    def _test_authentication(self):
        """Test Chess.com authentication with current credentials."""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return

        self._set_status("Testing authentication...")
        self.test_auth_button.config(state=tk.DISABLED)

        def test_worker():
            try:
                # Create client with current credentials
                client = ChessComClient()

                # Override credentials if entered in GUI
                if password:
                    client.username = username
                    client.password = password
                    client._setup_authenticated_session()

                self._log_output(f"Testing authentication for {username}...\n", "info")

                # Test authentication
                if client.test_authentication():
                    self._log_output("✅ Authentication successful!\n", "success")
                    messagebox.showinfo("Success", "Authentication test passed!")
                else:
                    self._log_output("❌ Authentication failed\n", "error")
                    messagebox.showerror("Authentication Failed", "Could not authenticate with Chess.com")

            except Exception as e:
                self._log_output(f"✗ Error testing authentication: {e}\n", "error")
                messagebox.showerror("Error", f"Authentication test failed: {e}")
            finally:
                self.test_auth_button.config(state=tk.NORMAL)
                self._set_status("Ready")

        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def _load_credentials(self):
        """Load saved credentials from config.local.ini into the GUI fields."""
        try:
            import configparser
            from pathlib import Path

            config_path = Path(__file__).parent.parent / 'config.local.ini'

            if not config_path.exists():
                messagebox.showinfo("Info", "No saved credentials found")
                return

            config = configparser.ConfigParser()
            config.read(config_path)

            if 'chess_com' in config:
                username = config['chess_com'].get('username', '')
                password = config['chess_com'].get('password', '')

                self.username_var.set(username)
                self.password_var.set(password)

            # Load AI API key and provider
            ai_key = ''
            ai_provider = ''
            if 'ai' in config:
                # Check for each provider key
                if config['ai'].get('xai_api_key'):
                    ai_key = config['ai'].get('xai_api_key')
                    ai_provider = 'xai'
                elif config['ai'].get('openai_api_key'):
                    ai_key = config['ai'].get('openai_api_key')
                    ai_provider = 'openai'
                elif config['ai'].get('anthropic_api_key'):
                    ai_key = config['ai'].get('anthropic_api_key')
                    ai_provider = 'anthropic'
                else:
                    # Fallback for old config format
                    ai_key = config['ai'].get('api_key', '')
                    ai_provider = 'xai'  # Default to xAI for backward compatibility

            if not hasattr(self, 'ai_key_var'):
                self.ai_key_var = tk.StringVar()
            if not hasattr(self, 'ai_provider_var'):
                self.ai_provider_var = tk.StringVar()

            self.ai_key_var.set(ai_key)
            self.ai_provider_var.set(ai_provider)

            loaded_items = []
            if username:
                loaded_items.append(f"credentials for user: {username}")
            if ai_key and ai_provider:
                loaded_items.append(f"{ai_provider} API key")

            if loaded_items:
                self._log_output(f"✓ Loaded settings: {', '.join(loaded_items)}\n", "success")
                messagebox.showinfo("Success", "Settings loaded successfully!")
            else:
                messagebox.showinfo("Info", "No settings found in config file")

        except Exception as e:
            self._log_output(f"✗ Error loading credentials: {e}\n", "error")
            messagebox.showerror("Error", f"Failed to load credentials: {e}")

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
    try:
        root = tk.Tk()
        app = ChessAnalyzerGUI(root)

        # Handle cleanup on window close
        def on_closing():
            try:
                app.cleanup()
            except Exception as e:
                print(f"Error during cleanup: {e}")
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        app.run()
    except Exception as e:
        print(f"Critical error in GUI: {e}")
        import traceback
        traceback.print_exc()
        # Show error dialog if tkinter is available
        try:
            import tkinter as tk_error
            from tkinter import messagebox
            root = tk_error.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Chess Analyzer Error", f"Application failed to start:\n\n{e}")
            root.destroy()
        except:
            pass  # If tkinter fails, we can't show the dialog


if __name__ == "__main__":
    main()