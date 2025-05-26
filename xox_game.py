import pygame
import sys

# Pygame initialization
pygame.init()

# Constants
WINDOW_SIZE = 600
BOARD_SIZE = 3
CELL_SIZE = WINDOW_SIZE // BOARD_SIZE
LINE_WIDTH = 15
CIRCLE_WIDTH = 15
CROSS_WIDTH = 20
CIRCLE_RADIUS = CELL_SIZE // 3
SPACE = CELL_SIZE // 4

# Colors
BG_COLOR = (41, 45, 62)  # Dark blue-gray
LINE_COLOR = (255, 255, 255)  # White
CIRCLE_COLOR = (255, 107, 107)  # Coral red
CROSS_COLOR = (72, 219, 251)  # Bright blue

# Screen settings
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Tic Tac Toe')

# Game board
board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_lines():
    # Horizontal lines
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), LINE_WIDTH)
    
    # Vertical lines
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, 
                                 (int(col * CELL_SIZE + CELL_SIZE // 2), 
                                  int(row * CELL_SIZE + CELL_SIZE // 2)), 
                                 CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR,
                               (col * CELL_SIZE + SPACE, row * CELL_SIZE + SPACE),
                               ((col + 1) * CELL_SIZE - SPACE, (row + 1) * CELL_SIZE - SPACE),
                               CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                               ((col + 1) * CELL_SIZE - SPACE, row * CELL_SIZE + SPACE),
                               (col * CELL_SIZE + SPACE, (row + 1) * CELL_SIZE - SPACE),
                               CROSS_WIDTH)

def check_winner():
    # Horizontal check
    for row in range(BOARD_SIZE):
        if board[row][0] == board[row][1] == board[row][2] != '':
            return board[row][0]
    
    # Vertical check
    for col in range(BOARD_SIZE):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return board[0][col]
    
    # Diagonal check
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2]
    
    return None

def is_board_full():
    return all(board[i][j] != '' for i in range(BOARD_SIZE) for j in range(BOARD_SIZE))

def main():
    current_player = 'X'
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouseX = event.pos[0]
                mouseY = event.pos[1]
                
                clicked_row = mouseY // CELL_SIZE
                clicked_col = mouseX // CELL_SIZE
                
                if board[clicked_row][clicked_col] == '':
                    board[clicked_row][clicked_col] = current_player
                    
                    winner = check_winner()
                    if winner:
                        game_over = True
                        print(f"Winner: {winner}")
                    elif is_board_full():
                        game_over = True
                        print("It's a tie!")
                    
                    current_player = 'O' if current_player == 'X' else 'X'
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    for i in range(BOARD_SIZE):
                        for j in range(BOARD_SIZE):
                            board[i][j] = ''
                    current_player = 'X'
                    game_over = False
        
        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures()
        pygame.display.update()

if __name__ == '__main__':
    main() 