from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from sys import exit
import socket
import threading
import pygame
import re

from struct import pack, unpack, error

from states.state import State
from scripts.board import Board, VisualBoard
from scripts.constants import SERVER, PORT, END_CONNECTION, MESSAGE_LENGTH, ENCODER, BLACK, WHITE, SIDE_PANEL, WIDTH, HEIGHT, RENDER_SCALE, SQUARE_SIZE

def send(conn: socket.socket, msg: str) -> None:
    try:
        msg_len = len(msg)
        send_len = pack('!I', msg_len)
        conn.send(send_len)
        conn.send(msg.encode(ENCODER))
    except socket.error as e:
        print(f"Send error: {e}")

def recv(conn:socket.socket) -> str:
    try:
        msg_len = unpack('!I', conn.recv(MESSAGE_LENGTH))[0]
        return conn.recv(msg_len).decode()
    except socket.error as e:
        print(f'Recv error: {e}')
    except error as e:
        print(f'Unpacking error: {e}')

running = True
msg = ""
board: Board = None

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
except socket.error as e:
    print(f"Socket error: {e}")
    running = False
    exit()

def main_connect():
    global msg, board, running

    size = recv(sock)
    if size is None:
        return
    print(f"Size receive: {size}")
    if re.match(r"size \d \d", size):
        width, height = map(int, size.split(" ")[1:3])
    else:
        print("Error: size")
        return
    
    color = recv(sock)
    if color is None:
        return
    print(f"Color received: {color}")
    if re.match(r"color \d", color):
        color = int(color.split(" ")[1])
    else:
        print("Error: color")
        return

    board = Board(width, height)

    while True:
        pygame.time.wait(int(1000 / 30))
        if msg != "":
            print(f"Sending: {msg}")
            send(sock, msg)
            msg = ""
        elif color == board.turn:
            continue

        print("Waiting for response...")
        resp = recv(sock)

        if resp is None:
            break

        if re.match(r"move \d \d \d \d", resp):
            start_row, start_col, row, col = map(int, resp.split()[1:5])
            if board.move_piece(board.get_piece(start_row, start_col), row, col):
                print("Valid move")
                print(board)
                if board.winner is not None:
                    print(f"Winner: {'Blue' if board.winner == BLACK else 'Red'}")
                    break
            else:
                print("Invalid move")
        elif resp == END_CONNECTION:
            print("Closing connection...")
            send(sock, END_CONNECTION)
            break
        else:
            print(f"Received: {resp}")

    sock.close()

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Client Test")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

def main():
    global msg, board, running

    print("Starting client...")
    thread = threading.Thread(target=main_connect)
    thread.start()

    print("Starting pygame...")
    msg_to_send = ""
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                msg = END_CONNECTION
                send(sock, msg)
                running = False

            if event.type == pygame.KEYDOWN:
                # Check for backspace 
                if event.key == pygame.K_BACKSPACE: 
    
                    # get text input from 0 to -1 i.e. end. 
                    msg_to_send = msg_to_send[:-1] 

                # Pressing enter will send the message (hopefully)
                elif event.key == pygame.K_RETURN:
                    msg = msg_to_send
                    msg_to_send = ""
                    if msg == END_CONNECTION:
                        running = False
    
                # Unicode standard is used for string formation 
                else: 
                    msg_to_send += event.unicode

        text = font.render(msg_to_send, True, (255, 255, 255))
        screen.blit(text, (100, 100))

        if board is not None:
            board_text = str(board).split("\n")
            board_text = map(lambda x: x.split(" "), board_text)
            for i, line in enumerate(board_text):
                for j, piece in enumerate(line):
                    text = font.render(piece, True, (255, 255, 255))
                    screen.blit(text, (screen.get_width() // 2 - 150 + j * 32, screen.get_height() // 2 - 120 + i * 32))

        pygame.display.update()
        clock.tick(60)

    print("Closing client...")
    thread.join()
    print("Closing pygame...")
    pygame.quit()

class GameOnlineMain(State):
    def __init__(self, game: Game):
        State.__init__(self, game)
        self.msg = ""
        self.msg_to_send = ""
        self.board = None

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER, PORT))
        except socket.error as e:
            print(f"Socket error: {e}")
            self.exit_state()
            exit()

        self.thread = threading.Thread(target=self.main_connect)
        self.thread.start()

    def main_connect(self):
        size = recv(self.sock)
        if size is None:
            return
        print(f"Size receive: {size}")
        if re.match(r"size \d \d", size):
            width, height = map(int, size.split(" ")[1:3])
        else:
            print("Error: size")
            return
        
        color = recv(self.sock)
        if color is None:
            return
        print(f"Color received: {color}")
        if re.match(r"color \d", color):
            self.color = int(color.split(" ")[1])
        else:
            print("Error: color")
            return

        self.board = VisualBoard(width, height)

        while True:
            pygame.time.wait(int(1000 / 30))
            if self.msg != "":
                print(f"Sending: {self.msg}")
                send(self.sock, self.msg)
                self.msg = ""
            elif self.color == self.board.turn:
                continue

            print("Waiting for response...")
            resp = recv(self.sock)

            if resp is None:
                break

            if re.match(r"move \d \d \d \d", resp):
                start_row, start_col, row, col = map(int, resp.split()[1:5])
                if self.board.move_piece(self.board.get_piece(start_row, start_col), row, col):
                    print("Valid move")
                    print(self.board)
                    if self.board.winner is not None:
                        print(f"Winner: {'Blue' if self.board.winner == BLACK else 'Red'}")
                        break
                else:
                    print("Invalid move")
            elif resp == END_CONNECTION:
                print("Closing connection...")
                send(self.sock, END_CONNECTION)
                break
            else:
                print(f"Received: {resp}")

        self.sock.close()

    def close_state(self):
        self.msg = END_CONNECTION
        send(self.sock, self.msg)
        self.thread.join()
        self.exit_state()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_state()
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                # Check for backspace 
                if event.key == pygame.K_ESCAPE:
                    self.close_state()
                    self.game.screen = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
                    self.game.board_display = pygame.Surface((WIDTH // RENDER_SCALE, HEIGHT // RENDER_SCALE))
                    print("GameMain -> Title")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos() 
                    x, y = x // RENDER_SCALE, y // RENDER_SCALE
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    piece = self.board.get_piece(row, col)
                    if piece is not None and piece.color == self.board.turn:
                        self.board.deselect_piece()
                        self.board.select_piece(piece)
                    elif piece is None and self.board.selected_piece is not None:
                        self.board.move_piece(self.board.selected_piece, row, col)
                
                if event.button == 1:
                    x, y = pygame.mouse.get_pos() 
                    x, y = x // RENDER_SCALE, y // RENDER_SCALE
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    piece = self.board.get_piece(row, col)
                    if piece is not None and piece.color == self.board.turn:    # Only allow selection of pieces of the current player color
                        self.board.deselect_piece()
                        self.board.select_piece(piece)
                    elif piece is None and self.board.selected_piece is not None and self.board.selected_piece.color == self.color and self.board.turn == self.color:   # Only allow moves if it's the player's turn
                        start_row, start_col = self.board.selected_piece.row, self.board.selected_piece.col
                        if self.sock is not None:
                            self.msg = f'move {start_row} {start_col} {row} {col}'
                        else:
                            print("Invalid move")
                        self.board.deselect_piece()
                    else:
                        self.board.deselect_piece()

                if event.button == 4:
                    self.board.scroll = min(0, self.board.scroll + 16)

                if event.button == 5:
                    spacing = len(self.board.list_of_moves) * 24 - self.game.screen.get_height() // 2
                    if spacing > 0:
                        self.board.scroll = max(-spacing, self.board.scroll - 16)

    def render(self):
        if self.board is None or not self.board.ready:
            self.game.loading_screen()
            return

        self.game.screen.fill((30, 30, 30))
        self.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (self.width, self.height)), (0, 0))

        pygame.display.flip()
        

if __name__ == "__main__":
    main()