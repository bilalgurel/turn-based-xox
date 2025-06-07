import socket
import json
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.columns import Columns

HOST = '127.0.0.1'  # Server IP address
PORT = 12345        # Server port
console = Console()

def print_board(board):
    # Game Board
    game_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    for _ in range(5):
        game_table.add_column("", style="cyan")
    
    for i in range(0, 25, 5):
        row = []
        for j in range(5):
            cell = board[i + j]
            if cell == 'X':
                cell = Text(cell, style="bold red")
            elif cell == 'O':
                cell = Text(cell, style="bold blue")
            elif cell == '#':
                cell = Text(cell, style="bold yellow")
            else:
                cell = Text(cell, style="dim")
            row.append(cell)
        game_table.add_row(*row)
    
    game_panel = Panel(game_table, title="Game Board", border_style="cyan")
    
    # Position Reference
    pos_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    for _ in range(5):
        pos_table.add_column("", style="dim")
    
    for i in range(0, 25, 5):
        row = [str(i), str(i+1), str(i+2), str(i+3), str(i+4)]
        pos_table.add_row(*row)
    
    pos_panel = Panel(pos_table, title="Position Reference", border_style="dim")
    
    # Display both panels side by side
    console.print()  
    console.print(Columns([game_panel, pos_panel], equal=True, expand=True))
    console.print()  

def main():
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]Welcome to Tic-Tac-Toe![/bold cyan]\n"
        "[dim]Waiting to connect to server...[/dim]",
        border_style="cyan"
    ))
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            console.print("[green]Connected to server![/green]")
            break
        except ConnectionRefusedError:
            console.print("[yellow]Server is not available. Retrying in 5 seconds...[/yellow]")
            time.sleep(5)
        except Exception as e:
            console.print(f"[red]Connection error: {e}[/red]")
            sys.exit(1)

    my_player = None
    while True:
        try:
            data = s.recv(1024)
            if not data:
                console.print("[red]Server closed the connection.[/red]")
                break

            for line in data.split(b'\n'):
                if not line.strip():
                    continue
                
                try:
                    msg = json.loads(line.decode())
                    
                    if msg.get('type') == 'start':
                        my_player = msg['player']
                        console.clear()
                        console.print(f"[green]You are assigned as player {my_player}[/green]")
                        if len(msg.get('board', [])) > 0:
                            print_board(msg['board'])
                        if msg.get('next') == my_player:
                            console.print(f"[bold green]Your turn! Make your move.[/bold green]")
                            while True:
                                try:
                                    pos = int(console.input("\n[bold cyan]Enter your move (0-24): [/bold cyan]"))
                                    if 0 <= pos <= 24:
                                        s.sendall(json.dumps({"type": "move", "position": pos}).encode() + b'\n')
                                        break
                                    else:
                                        console.print("[red]Please enter a number between 0 and 24.[/red]")
                                except ValueError:
                                    console.print("[red]Please enter a valid number.[/red]")
                        else:
                            console.print("[dim]Waiting for other player...[/dim]")
                    
                    elif msg.get('type') == 'update':
                        console.clear()
                        print_board(msg['board'])
                        
                        if msg['next'] is not None:
                            if msg['next'] == my_player:
                                console.print(f"[bold green]Your turn! Make your move.[/bold green]")
                                while True:
                                    try:
                                        pos = int(console.input("\n[bold cyan]Enter your move (0-24): [/bold cyan]"))
                                        if 0 <= pos <= 24:
                                            s.sendall(json.dumps({"type": "move", "position": pos}).encode() + b'\n')
                                            break
                                        else:
                                            console.print("[red]Please enter a number between 0 and 24.[/red]")
                                    except ValueError:
                                        console.print("[red]Please enter a valid number.[/red]")
                            else:
                                console.print(f"[bold yellow]Waiting for other player's move...[/bold yellow]")
                    
                    elif msg.get('type') == 'invalid_move':
                        console.print("[red]Invalid move! This square is occupied or blocked. Please choose another square.[/red]")
                        if msg['next'] == my_player:
                            while True:
                                try:
                                    pos = int(console.input("\n[bold cyan]Enter your move (0-24): [/bold cyan]"))
                                    if 0 <= pos <= 24:
                                        s.sendall(json.dumps({"type": "move", "position": pos}).encode() + b'\n')
                                        break
                                    else:
                                        console.print("[red]Please enter a number between 0 and 24.[/red]")
                                except ValueError:
                                    console.print("[red]Please enter a valid number.[/red]")
                    
                    elif msg.get('type') == 'result':
                        console.clear()
                        print_board(msg['board'])
                        if msg['winner']:
                            if msg['winner'] == my_player:
                                console.print(Panel.fit(
                                    "[bold green]Congratulations! You won![/bold green]",
                                    border_style="green"
                                ))
                            else:
                                console.print(Panel.fit(
                                    "[bold red]You lost![/bold red]",
                                    border_style="red"
                                ))
                        else:
                            console.print(Panel.fit(
                                "[bold yellow]Game ended in a draw![/bold yellow]",
                                border_style="yellow"
                            ))
                        s.close()
                        sys.exit(0)
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    continue

        except Exception as e:
            console.print(f"[red]Connection error: {e}[/red]")
            break

    s.close()

if __name__ == "__main__":
    main()
