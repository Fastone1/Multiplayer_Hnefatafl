from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import socket
import threading
import pygame
import re

from struct import pack, unpack, error

from states.state import State
from scripts.board import VisualBoard
from scripts.constants import BACKGROUND, SERVER, PORT, END_CONNECTION, MESSAGE_LENGTH, ENCODER, BLACK, SIDE_PANEL, WIDTH, HEIGHT, RENDER_SCALE, SQUARE_SIZE

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

class Client(State):
    def __init__(self, game: Game, size: int, name: str):
        State.__init__(self, game)
        self.msg = ""
        self.msg_to_send = ""
        self.name = name

        self.size = size
        self.width = self.size * SQUARE_SIZE * RENDER_SCALE
        self.height = self.size * SQUARE_SIZE * RENDER_SCALE

        self.game.screen = pygame.display.set_mode((self.width + SIDE_PANEL, self.height))
        self.game.board_display = pygame.Surface((self.width // RENDER_SCALE, self.height // RENDER_SCALE))

        self.board = VisualBoard(self.game, self.size, self.size)

        self.opp_disconnect = False

        self.sock = None
        self.connected = False
        self.CONNECTION_REFUSED = pygame.USEREVENT + 1

        self.thread = threading.Thread(target=self.main_connect)
        self.thread.start()

    def main_connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER, PORT))
        except socket.error as e:
            print(f"Socket error: {e}")
            pygame.event.post(pygame.event.Event(self.CONNECTION_REFUSED, {"error": e}))
            return
        print("[CONNECTED] Connected to server")
        self.connected = True

        send(self.sock, f"info {self.size} {self.name}")    # Send the size of the board and the name of the player
        
        color = recv(self.sock)
        if color is None or re.match(r"color \d", color) is None:
            print("Error: color")
            return
        print(f"Color received: {color}")
        self.color = int(color.split()[1])

        while True:
            pygame.time.wait(int(1000 / 30))
            if self.msg != "":
                print(f"Sending: {self.msg}")
                send(self.sock, self.msg)
                self.msg = ""
            elif self.board.ready and self.color == self.board.turn:
                continue

            print("Waiting for response...")
            resp = recv(self.sock)

            if resp is None:
                break

            if re.match(r"move [\d]{1,2} [\d]{1,2} [\d]{1,2} [\d]{1,2}", resp):
                start_row, start_col, row, col = map(int, resp.split()[1:5])
                if self.board.move_piece(self.board.get_piece(start_row, start_col), row, col):
                    print("Valid move")
                    print(self.board)
                    if self.board.winner is not None:
                        print(f"Winner: {'Blue' if self.board.winner == BLACK else 'Red'}")
                        break
                else:
                    print("Invalid move")
            elif resp == "win":
                self.board.winner = self.color
                self.game.sounds["end"].play()
                self.opp_disconnect = True
                print("You win!")
                break
            elif re.match(r"start [a-zA-Z0-9_]{1,16} [a-zA-Z0-9_]{1,16}", resp):
                name1 , name2 = resp.split()[1:3]
                self.board.player1 = name1 + " (Blue)"
                self.board.player2 = name2 + " (Red)"
                self.board.ready = True
                print(f"Players: {name1} vs {name2}")
                pygame.mixer.music.fadeout(500)
                self.game.sounds["start"].play()
            elif resp == END_CONNECTION:
                print("Closing connection...")
                send(self.sock, END_CONNECTION)
                break
            else:
                print(f"Received: {resp}")

        self.sock.close()

    def close_state(self):
        self.msg = END_CONNECTION
        if self.sock is not None and self.connected:
            try:
                send(self.sock, self.msg)
            except:
                pass
        self.thread.join()
        self.exit_state()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_state()
                self.game.running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_state()
                    self.game.reset_screen()
                    print("Client -> OnlineMode")
                    break

            if event.type == self.CONNECTION_REFUSED:
                self.close_state()
                self.game.reset_screen()
                self.game.show_error(f"Server refused connection")
                break

            if event.type == pygame.MOUSEBUTTONDOWN and self.board.ready:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos() 
                    x, y = x // RENDER_SCALE, y // RENDER_SCALE
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    piece = self.board.get_piece(row, col)
                    if piece is not None:
                        self.board.deselect_piece()
                        self.board.select_piece(piece)
                    elif piece is None and self.board.selected_piece is not None and self.board.selected_piece.color == self.color:   # Only allow moves the player's pieces
                        start_row, start_col = self.board.selected_piece.row, self.board.selected_piece.col
                        if self.sock is not None:
                            self.msg = f'move {start_row} {start_col} {row} {col}'
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

        self.game.screen.fill(BACKGROUND)
        self.board.render()

        if self.board.winner is None:
            text = "Your Turn" if self.board.turn == self.color else "Opponent's Turn"
            self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 20, self.game.font_small)

            self.game.draw_text(self.game.screen, self.board.player1, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 70, self.game.font_small)
            self.game.draw_text(self.game.screen, "VS", (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 90, self.game.font_small)
            self.game.draw_text(self.game.screen, self.board.player2, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 110, self.game.font_small)
        elif self.opp_disconnect:
            self.game.draw_text(self.game.screen, "Opponent Disconnected", (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, self.game.screen.get_height() // 2 + 36, self.game.font_small)

        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (self.width, self.height)), (0, 0))

        
        