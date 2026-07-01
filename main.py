import typer
import json
import asyncio
import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from domain.schemas import RPMAlert
from orchestrator.orchestrator import Orchestrator

app = typer.Typer(help="ClinicalBridge CLI")
console = Console()

@app.command("process")
def process_alert(
    alert_path: str = typer.Argument(..., help="Path to alert JSON file"),
    prompt_version: str = typer.Option("v3.0", "--prompt-version", help="Prompt version to use")
):
    """Process a single RPM alert through the ClinicalBridge pipeline."""
    if not os.path.exists(alert_path):
        console.print(f"[red]Error: File {alert_path} not found.[/red]")
        raise typer.Exit(code=1)
        
    with open(alert_path, "r") as f:
        alert_data = json.load(f)
        
    alert = RPMAlert(**alert_data)
    orchestrator = Orchestrator(prompt_version=prompt_version)
    
    console.print(Panel.fit(f"Processing Alert ID: {alert.alert_id}", style="bold blue"))
    
    with console.status("[bold green]Running multi-agent pipeline...") as status:
        try:
            ccb = asyncio.run(orchestrator.process_alert(alert))
            console.print("[bold green]Pipeline completed successfully![/bold green]")
            
            console.print(Panel(
                f"[bold]Urgency:[/bold] {ccb.confidence_score}\n\n"
                f"[bold]Summary:[/bold] {ccb.alert_summary}\n\n"
                f"[bold]EHR Context:[/bold] {ccb.ehr_context}\n\n"
                f"[bold]Considerations:[/bold] {', '.join(ccb.clinical_considerations)}\n\n"
                f"[bold]Disclaimer:[/bold] {ccb.disclaimer}",
                title="Clinical Context Brief",
                border_style="green"
            ))
            
            # Print full JSON output separately
            console.print("\n[bold]Full JSON Output:[/bold]")
            console.print(JSON.from_data(ccb.model_dump()))
            
        except Exception as e:
            console.print(f"[red]Pipeline failed: {str(e)}[/red]")

if __name__ == "__main__":
    app()
