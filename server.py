import socket
import threading
import json
import sys

HOST = '0.0.0.0'
PORT = 12345

def reset_game():
    global board, current_player, game_over
    board = [' ' for _ in range(9)]
    current_player = 'X'
    game_over = False

board = [' ' for _ in range(9)]
players = {}
connections = []
current_player = 'X'
lock = threading.Lock()
game_over = False

def check_win(board):
    win_positions = [
        [0,1,2], [3,4,5], [6,7,8], # satırlar
        [0,3,6], [1,4,7], [2,5,8], # sütunlar
        [0,4,8], [2,4,6]           # çaprazlar
    ]
    for pos in win_positions:
        if board[pos[0]] == board[pos[1]] == board[pos[2]] != ' ':
            return board[pos[0]]
    if ' ' not in board:
        return 'draw'
    return None

def send_all(msg):
    data = json.dumps(msg).encode()
    for conn in connections[:]:
        try:
            conn.sendall(data + b'\n')
        except:
            if conn in connections:
                connections.remove(conn)
            if conn in players.values():
                for player, conn_ref in list(players.items()):
                    if conn_ref == conn:
                        del players[player]

def handle_client(conn, addr, player):
    global current_player, game_over, board
    try:
        conn.sendall(json.dumps({
            "type": "start", 
            "player": player,
            "board": board.copy(),
            "next": current_player
        }).encode() + b'\n')
        
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                for line in data.split(b'\n'):
                    if not line.strip():
                        continue
                    msg = json.loads(line.decode())
                    if msg.get('type') == 'move' and not game_over:
                        with lock:
                            if current_player != player:
                                continue
                            pos = msg.get('position')
                            if pos is None or not (0 <= pos < 9) or board[pos] != ' ':
                                continue
                            board[pos] = player
                            winner = check_win(board)
                            if winner == 'draw':
                                send_all({"type": "update", "board": board.copy(), "next": None})
                                send_all({"type": "result", "winner": None, "board": board.copy()})
                                game_over = True
                            elif winner:
                                send_all({"type": "update", "board": board.copy(), "next": None})
                                send_all({"type": "result", "winner": winner, "board": board.copy()})
                                game_over = True
                            else:
                                current_player = 'O' if current_player == 'X' else 'X'
                                send_all({"type": "update", "board": board.copy(), "next": current_player})
                                print(f"Turn changed to: {current_player}")  # Debug print
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error in client handler: {e}")
                break
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if conn in connections:
            connections.remove(conn)
        if player in players:
            del players[player]
        conn.close()

def main():
    global current_player
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
        s.listen(2)
        print(f"Server started. Waiting on port {PORT}...")

        while True:
            reset_game()
            connections.clear()
            players.clear()
            
            print("\nWaiting for players to connect...")
            while len(connections) < 2:
                conn, addr = s.accept()
                player = 'X' if len(connections) == 0 else 'O'
                players[player] = conn
                connections.append(conn)
                print(f"Player {player} connected: {addr}")

            print(f"Game started! Turn: {current_player}")
            # Send initial game state to all players
            for player, conn in players.items():
                conn.sendall(json.dumps({
                    "type": "start",
                    "player": player,
                    "board": board.copy(),
                    "next": current_player
                }).encode() + b'\n')
            
            # Send initial board state
            send_all({"type": "update", "board": board.copy(), "next": current_player})

            threads = []
            for i, player in enumerate(['X', 'O']):
                t = threading.Thread(target=handle_client, args=(connections[i], None, player))
                t.daemon = True
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            print("\nGame ended. Waiting for new game...")

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
