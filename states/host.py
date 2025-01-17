from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from states.state import State
from scripts.connection import Server
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, SIDE_PANEL, WIDTH, HEIGHT, END_CONNECTION, WHITE, BLACK
from scripts.board import VisualBoard


class HostState(State):
    def __init__(self, game: Game, width:int, height:int):
        super().__init__(game)

        self.server = Server()
        self.reset_proposed = [False, False]
        
        self.width = width * SQUARE_SIZE * RENDER_SCALE
        self.height = height * SQUARE_SIZE * RENDER_SCALE

        self.game.screen = pygame.display.set_mode((self.width + SIDE_PANEL, self.height))
        self.game.board_display = pygame.Surface((self.width // RENDER_SCALE, self.height // RENDER_SCALE))

        self.scroll = 0
        self.board = VisualBoard(self.game, width, height)
        self.my_turn = WHITE

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                self.server.close_connection()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_state()

                if event.key == pygame.K_r:
                    if self.server.conn is not None:
                        self.server.send("reset", self.server.conn)
                        self.reset_proposed[0] = True
                    if self.reset_proposed[0] and self.reset_proposed[1]:
                        self.board.reset(self.width // SQUARE_SIZE // RENDER_SCALE, self.height // SQUARE_SIZE // RENDER_SCALE)
                        self.board.deselect_piece()
                        self.scroll = 0
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
                            if self.server.conn is not None:
                                self.server.send(f'move {start_row} {start_col} {row} {col}', self.server.conn)
                        self.board.deselect_piece()
                    else:
                        self.board.deselect_piece()

                if event.button == 4:
                    self.board.scroll = min(0, self.board.scroll + 16)

                if event.button == 5:
                    spacing = len(self.board.list_of_moves) * 24 - self.game.screen.get_height() // 2
                    if spacing > 0:
                        self.board.scroll = max(-spacing, self.board.scroll - 16)

        if self.server.conn is not None:
            if self.board.turn != self.my_turn:
                msg = self.server.recv(self.server.conn)
                if msg is None:
                    self.server.close_connection()
                    self.close_state()
                elif msg == "reset":
                    if self.reset_proposed:
                        self.board.reset(self.width // SQUARE_SIZE // RENDER_SCALE, self.height // SQUARE_SIZE // RENDER_SCALE)
                        self.reset_proposed = [False, False]
                        self.scroll = 0
                        self.board.deselect_piece()
                    else:
                        self.reset_proposed[1] = True
                elif msg.startswith("move"):
                    _, start_row, start_col, row, col = msg.split()
                    start_row, start_col, row, col = int(start_row), int(start_col), int(row), int(col)
                    piece = self.board.get_piece(start_row, start_col)
                    self.board.move_piece(piece, row, col)
                elif msg == "size":
                    self.server.send(f"size {self.width // SQUARE_SIZE // RENDER_SCALE} {self.height // SQUARE_SIZE // RENDER_SCALE}", self.server.conn)
                elif msg == END_CONNECTION:
                    self.server.close_connection()
                    self.exit_state()
                else:
                    pass
            else:   # If it's my turn
                self.server.send("null", self.server.conn)

    def adjust_scroll_to_bottom(self):
        spacing = len(self.board.list_of_moves) * 24 - self.game.screen.get_height()
        if spacing > 0:
            self.scroll = -spacing

    def close_state(self):
        '''Close the connection, exit the state, and return to the HostJoin state.'''
        self.exit_state()
        self.game.screen = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
        self.game.board_display = pygame.Surface((WIDTH // RENDER_SCALE, HEIGHT // RENDER_SCALE))

        self.game.loading_screen()

        if self.server.connected:
            self.server.send(END_CONNECTION, self.server.conn)
        self.server.close_connection()
        print("HostState -> HostJoin")

    def render(self):
        self.game.screen.fill((30, 30, 30))
        self.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (self.width, self.height)), (0, 0))

        if self.server.conn is None:
            text = "Waiting for connection" + "." * (pygame.time.get_ticks() // 500 % 4)
            self.game.draw_text(self.game.screen, text, (255, 255, 255), WIDTH + SIDE_PANEL // 2, HEIGHT // 5, self.game.font_small)

        pygame.display.flip()
        

    