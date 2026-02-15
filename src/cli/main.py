import typer
import httpx
import json
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="MCP Framework CLI - Manage and test connectors")
console = Console()
API_BASE_URL = "http://localhost:8000/api/v1"

@app.command()
def list():
    """List all registered connectors."""
    try:
        response = httpx.get(f"{API_BASE_URL}/connectors")
        response.raise_for_status()
        connectors = response.json()

        table = Table(title="Registered Connectors")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Actions", style="white")

        for c in connectors:
            table.add_row(
                c["id"], 
                c["name"], 
                c["status"], 
                ", ".join(c["supported_actions"])
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing connectors: {e}[/red]")

@app.command()
def test(connector_id: str, action: str, params: str = "{}"):
    """Test a connector action."""
    try:
        payload = {
            "action": action,
            "params": json.loads(params)
        }
        console.print(f"Executing [bold]{action}[/bold] on [bold]{connector_id}[/bold]...")
        
        response = httpx.post(
            f"{API_BASE_URL}/execute/{connector_id}",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        if result["success"]:
            console.print("[green]Success![/green]")
            console.print_json(data=result["data"])
        else:
            console.print(f"[red]Failed: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error testing connector: {e}[/red]")

if __name__ == "__main__":
    app()
