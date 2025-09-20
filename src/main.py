#!/usr/bin/env python3
"""Chess Analyzer - Main CLI application."""

import click
from pathlib import Path
from datetime import datetime

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from api.client import ChessComClient
from db.database import ChessDatabase
from analysis.analyzer import ChessAnalyzer
from ai.grok_client import GrokClient

@click.group()
@click.option('--gui', is_flag=True, help='Launch GUI interface')
@click.version_option(version="0.1.0")
def cli(gui):
    """Chess Analyzer - Analyze your chess games with AI-powered insights."""
    if gui:
        # Launch GUI
        from gui import main
        main()
        return
    pass

@cli.command()
@click.argument('username')
def fetch(username):
    """Fetch games for a Chess.com username."""
    click.echo(f"Fetching games for user: {username}")
    
    client = ChessComClient()
    db = ChessDatabase()
    
    try:
        games = client.get_all_games(username)
        if games:
            db.insert_games_batch(games)
            click.echo(f"Successfully fetched and stored {len(games)} games for {username}")
        else:
            click.echo(f"No games found for {username}")
    except Exception as e:
        click.echo(f"Error fetching games: {e}", err=True)
    finally:
        db.close()

@cli.command()
@click.option('--username', required=True, help='Chess.com username')
@click.option('--all', is_flag=True, help='Analyze all games')
@click.option('--game-id', help='Analyze specific game ID')
@click.option('--date-range', help='Date range in format YYYY-MM-DD:YYYY-MM-DD')
def analyze(username, all, game_id, date_range):
    """Analyze chess games and provide insights."""
    click.echo(f"Analyzing games for {username}")
    
    db = ChessDatabase()
    analyzer = ChessAnalyzer()
    ai_client = GrokClient()
    
    try:
        games = []
        
        if game_id:
            game = db.get_game_by_id(game_id)
            if game:
                games = [game]
            else:
                click.echo(f"Game {game_id} not found in database")
                return
        elif date_range:
            # Parse date range
            start_str, end_str = date_range.split(':')
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
            games = db.get_games_by_date_range(username, start_date, end_date)
        else:
            games = db.get_games_by_username(username, limit=10)  # Limit for demo
        
        if not games:
            click.echo("No games found to analyze")
            return
        
        total_blunders = 0
        total_mistakes = 0
        
        for game in games:
            click.echo(f"\nAnalyzing game: {game['game_id']}")
            analysis = analyzer.analyze_game(game['pgn'])
            
            if 'error' in analysis:
                click.echo(f"Error analyzing game: {analysis['error']}")
                continue
            
            summary = analysis['summary']
            click.echo(f"Moves: {summary['total_moves']}")
            click.echo(f"Blunders: {summary['blunder_count']}")
            click.echo(f"Mistakes: {summary['mistake_count']}")
            click.echo(f"Accuracy: {summary['accuracy']:.1f}%")
            
            total_blunders += summary['blunder_count']
            total_mistakes += summary['mistake_count']
            
            # Show top blunders
            blunders = analysis['blunders'][:3]  # Top 3
            if blunders:
                click.echo("Top blunders:")
                for blunder in blunders:
                    click.echo(f"  Move {blunder['move_number']}: {blunder['move']} "
                             f"(lost {blunder['score_change']} cp)")
            
            # Get AI advice
            click.echo("\nAI Analysis:")
            advice = ai_client.get_chess_advice(game['pgn'], analysis)
            click.echo(advice)
        
        click.echo(f"\nOverall: {total_blunders} blunders, {total_mistakes} mistakes across {len(games)} games")
        
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
    finally:
        db.close()
        analyzer.close()
        # ai_client doesn't need closing

@cli.command()
@click.option('--username', required=True, help='Chess.com username')
def stats(username):
    """Show statistics for a Chess.com player."""
    click.echo(f"Fetching stats for {username}")
    
    client = ChessComClient()
    try:
        stats_data = client.get_player_stats(username)
        profile = client.get_player_profile(username)
        
        click.echo(f"Player: {profile.get('username', username)}")
        click.echo(f"Name: {profile.get('name', 'N/A')}")
        click.echo(f"Country: {profile.get('country', 'N/A')}")
        click.echo(f"Joined: {profile.get('joined', 'N/A')}")
        
        # Display some key stats
        if 'chess_rapid' in stats_data:
            rapid = stats_data['chess_rapid']
            click.echo(f"Rapid Rating: {rapid.get('last', {}).get('rating', 'N/A')}")
        if 'chess_blitz' in stats_data:
            blitz = stats_data['chess_blitz']
            click.echo(f"Blitz Rating: {blitz.get('last', {}).get('rating', 'N/A')}")
            
    except Exception as e:
        click.echo(f"Error fetching stats: {e}", err=True)

if __name__ == '__main__':
    cli()