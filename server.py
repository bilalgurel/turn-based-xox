import socket
import threading
import json
import sys
import random

HOST = '0.0.0.0'
PORT = 12345

BOARD_SIZE = 25  # 5x5 board
NUM_BLOCKS = 5   # Number of random obstacles

def reset_game():
    global board, current_player, game_over
    board = [' ' for _ in range(BOARD_SIZE)]
    # Place random obstacles
    block_positions = random.sample(range(BOARD_SIZE), NUM_BLOCKS)
    for pos in block_positions:
        board[pos] = '#'
    current_player = 'X'
    game_over = False

board = [' ' for _ in range(BOARD_SIZE)]
players = {}
connections = []
current_player = 'X'
lock = threading.Lock()
game_over = False

def check_win(board):
    # Horizontal checks
    for i in range(0, BOARD_SIZE, 5):
        for j in range(3):  # For groups of 3
            if board[i+j] == board[i+j+1] == board[i+j+2] != ' ' and board[i+j] != '#':
                return board[i+j]
    
    # Vertical checks
    for i in range(5):
        for j in range(0, 15, 5):  # For groups of 3
            if board[i+j] == board[i+j+5] == board[i+j+10] != ' ' and board[i+j] != '#':
                return board[i+j]
    
    # Diagonal checks
    # Top-left to bottom-right
    for i in range(0, 15, 5):
        for j in range(3):
            if board[i+j] == board[i+j+6] == board[i+j+12] != ' ' and board[i+j] != '#':
                return board[i+j]
    
    # Top-right to bottom-left
    for i in range(2, 15, 5):
        for j in range(3):
            if board[i+j] == board[i+j+4] == board[i+j+8] != ' ' and board[i+j] != '#':
                return board[i+j]
    
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
        # Send player role on initial connection
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
                            if pos is None or not (0 <= pos < BOARD_SIZE):
                                conn.sendall(json.dumps({
                                    "type": "invalid_move",
                                    "next": current_player
                                }).encode() + b'\n')
                                continue
                            if board[pos] != ' ':  # Check if square is empty or blocked
                                conn.sendall(json.dumps({
                                    "type": "invalid_move",
                                    "next": current_player
                                }).encode() + b'\n')
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
                                print(f"Move made: {player} -> {pos}")
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
        print(f"Server started. Listening on port {PORT}...")

        while True:
            reset_game()
            connections.clear()
            players.clear()
            
            print("\nWaiting for players...")
            while len(connections) < 2:
                conn, addr = s.accept()
                player = 'X' if len(connections) == 0 else 'O'
                players[player] = conn
                connections.append(conn)
                print(f"Player {player} connected: {addr}")

            # Start game when both players are connected
            print("\nGame starting...")
            # Send initial state only once
            send_all({"type": "update", "board": board.copy(), "next": current_player})

            threads = []
            for i, player in enumerate(['X', 'O']):
                t = threading.Thread(target=handle_client, args=(connections[i], None, player))
                t.daemon = True
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            print("\nReady for new game...")

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
