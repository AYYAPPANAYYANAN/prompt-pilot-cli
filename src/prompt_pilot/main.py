import typer
import pyperclip
import os
import json
from typing import List
from rich import print
from rich.console import Console
from rich.table import Table
from pathlib import Path
from .brain import optimize_intent, save_to_history, HISTORY_FILE

app = typer.Typer(help="PromptPilot: Orchestrate your AI workflow.")
console = Console()

# Define the path for the configuration file
CONFIG_FILE = Path.home() / ".prompt_pilot.env"

@app.command()
def config(key: str = typer.Option(..., help="Your Groq API Key")):
    """⚙️ Save your Groq API key to a local config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"GROQ_API_KEY={key}\n")
        console.print(f"[bold green]✅ API Key saved successfully to {CONFIG_FILE}![/bold green]")
        console.print("[dim]Note: Ensure you have python-dotenv installed to load this key.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error saving config:[/bold red] {e}")

@app.command()
def optimize(
    intent: List[str] = typer.Argument(..., help="The casual thought to professionalize"),
    copy: bool = typer.Option(False, "--copy", "-c", help="Copy result to clipboard")
):
    """🚀 Orchestrate a pro prompt and save it to history."""
    full_intent = " ".join(intent)
    console.print(f"\n[bold blue]Input Intent:[/bold blue] [italic]{full_intent}[/italic]")
    
    with console.status("[bold green]Groq is thinking...", spinner="clock"):
        pro_prompt = optimize_intent(full_intent)
    
    console.print("\n[bold green]✅ Optimized Prompt:[/bold green]")
    print(f"[dim]{'-'*60}[/dim]")
    print(pro_prompt.strip())
    print(f"[dim]{'-'*60}[/dim]\n")

    # Save to history if successful
    if pro_prompt and "Error" not in pro_prompt:
        save_to_history(full_intent, pro_prompt)

    if copy:
        pyperclip.copy(pro_prompt.strip())
        console.print("[bold yellow]📋 Copied to clipboard![/bold yellow]\n")

@app.command()
def history():
    """📚 View your recent prompt history."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No history found yet![/yellow]")
        return

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        console.print("[red]Error reading history file.[/red]")
        return

    table = Table(title="Recent Orchestrations")
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Intent", style="magenta")
    table.add_column("Optimized Snippet", style="green")

    # Show the last 10 entries
    for entry in data[-10:]:
        # Truncate prompt for better table display
        snippet = (entry["prompt"][:50] + '..') if len(entry["prompt"]) > 50 else entry["prompt"]
        table.add_row(entry["timestamp"], entry["intent"], snippet)

    console.print(table)

@app.command()
def clear():
    """🗑️ Clear all prompt history."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        console.print("[bold red]History deleted successfully.[/bold red]")
    else:
        console.print("[yellow]No history file found to delete.[/yellow]")

if __name__ == "__main__":
    app()