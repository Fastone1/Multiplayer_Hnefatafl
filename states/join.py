from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from states.state import State
from scripts.connection import Client
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, SIDE_PANEL, WIDTH, HEIGHT, END_CONNECTION, WHITE, BLACK
from scripts.board import VisualBoard


class JoinState(State):
    def __init__(self, game: Game, client: Client, server_id: int):
        super().__init__(game)

        self.reset_proposed = [False, False]
        self.client = client
        self.client.connect(server_id)

        self.client.send("size", self.client.socket)
        msg = self.client.recv(self.client.socket)
        if msg.startswith("size"):
            size = msg.split()[1:]
            width, height = int(size[0]), int(size[1])
        else:
            print("Error: size")
            self.exit_state()
            return
        
        self.width = width * SQUARE_SIZE * RENDER_SCALE
        self.height = height * SQUARE_SIZE * RENDER_SCALE
        
        self.game.screen = pygame.display.set_mode((self.width + SIDE_PANEL, self.height))
        self.game.board_display = pygame.Surface((self.width // RENDER_SCALE, self.height // RENDER_SCALE))

        self.board = VisualBoard(self.game, width, height)
        self.my_turn = BLACK
        
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                self.client.close_connection()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_state()

                if event.key == pygame.K_r:
                    if self.client.socket is not None:
                        self.client.send("reset", self.client.socket)
                        self.reset_proposed[0] = True
                    if self.reset_proposed[0] and self.reset_proposed[1]:
                        self.board.reset(self.width // SQUARE_SIZE // RENDER_SCALE, self.height // SQUARE_SIZE // RENDER_SCALE)
                        self.board.deselect_piece()
                        self.reset_proposed = [False, False]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos() 
                    x, y = x // RENDER_SCALE, y // RENDER_SCALE
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    piece = self.board.get_piece(row, col)
                    if piece is not None and piece.color == self.my_turn:
                        self.board.deselect_piece()
                        self.board.select_piece(piece)
                    elif piece is None and self.board.selected_piece is not None and self.board.turn == self.my_turn:
                        start_row, start_col = self.board.selected_piece.row, self.board.selected_piece.col
                        if self.board.move_piece(self.board.selected_piece, row, col):
                            if self.client.socket is not None:
                                self.client.send(f'move {start_row} {start_col} {row} {col}', self.client.socket)
                        self.board.deselect_piece()
                    else:
                        self.board.deselect_piece()
                    
                if event.button == 4:
                    self.board.scroll = min(0, self.board.scroll + 16)

                if event.button == 5:
                    spacing = len(self.board.list_of_moves) * 24 - self.game.screen.get_height() // 2
                    if spacing > 0:
                        self.board.scroll = max(-spacing, self.board.scroll - 16)

        if self.client.socket is not None:
            if self.board.turn != self.my_turn:
                msg = self.client.recv(self.client.socket)
                if msg is None:
                    self.client.close_connection()
                    self.close_state()
                elif msg == "reset":
                    if self.reset_proposed:
                        self.board.reset(self.width // SQUARE_SIZE // RENDER_SCALE, self.height // SQUARE_SIZE // RENDER_SCALE)
                        self.reset_proposed = [False, False]
                        self.board.deselect_piece()
                    else:
                        self.reset_proposed[1] = True
                elif msg.startswith("move"):
                    _, start_row, start_col, row, col = msg.split()
                    start_row, start_col, row, col = int(start_row), int(start_col), int(row), int(col)
                    piece = self.board.get_piece(start_row, start_col)
                    self.board.move_piece(piece, row, col)
                elif msg == "size":
                    self.client.send(f"size {self.width // SQUARE_SIZE // RENDER_SCALE} {self.height // SQUARE_SIZE // RENDER_SCALE}", self.client.socket)
                elif msg == END_CONNECTION:
                    self.client.close_connection()
                    self.exit_state()
                else:
                    pass
            else:   # If it's my turn
                self.client.send("null", self.client.socket)

    def close_state(self):
        self.exit_state()
        self.game.screen = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
        self.game.board_display = pygame.Surface((WIDTH // RENDER_SCALE, HEIGHT // RENDER_SCALE))

        self.game.loading_screen()

        if self.client.connected:
            self.client.send(END_CONNECTION, self.client.socket)
        self.client.close_connection()
        print("HostState -> HostJoin")

    def render(self):
        self.game.screen.fill((30, 30, 30))
        self.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (self.width, self.height)), (0, 0))

        if self.client.socket is None:
            text = "Waiting for connection" + "." * (pygame.time.get_ticks() // 500 % 4)
            self.game.draw_text(self.game.screen, text, (255, 255, 255), WIDTH + SIDE_PANEL // 2, HEIGHT // 5, self.game.font_small)

        pygame.display.flip()
        

    