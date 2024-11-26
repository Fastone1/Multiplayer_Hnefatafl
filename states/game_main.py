from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, WIDTH, HEIGHT
from states.state import State
from scripts.board import Board

class GameMain(State):
    def __init__(self, game: Game):
        super().__init__(game)

        self.board = Board(self.game, 9, 9)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("GameMain -> Title")

                if event.key == pygame.K_r:
                    self.board.reset(9, 9)
                    self.board.deselect_piece()
                    self.scroll = 0

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
                        self.board.deselect_piece()

                if event.button == 3:
                    self.board.deselect_piece()
                    self.board.undo_move()

    def adjust_scroll_to_bottom(self):
        spacing = len(self.board.list_of_moves) * 24 - HEIGHT // 2
        if spacing > 0:
            self.scroll = -spacing

    def render(self):
        self.game.screen.fill((30, 30, 30))
        self.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (WIDTH, HEIGHT)), (0, 0))
        self.game.screen.blit(self.game.top_screen, (0, 0))
        pygame.display.flip()
