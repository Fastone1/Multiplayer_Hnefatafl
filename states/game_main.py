from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, WIDTH, HEIGHT
from states.state import State

class GameMain(State):
    def __init__(self, game: Game):
        super().__init__(game)

    def update(self, actions: dict[str, bool]):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("GameMain -> Title")

                if event.key == pygame.K_r:
                    self.game.board.reset(9, 9)
                    self.game.board.deselect_piece()
                    self.scroll = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos() 
                    x, y = x // RENDER_SCALE, y // RENDER_SCALE
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    piece = self.game.board.get_piece(row, col)
                    if piece is not None and piece.color == self.game.board.turn:
                        self.game.board.deselect_piece()
                        self.game.board.select_piece(piece)
                    elif piece is None and self.game.board.selected_piece is not None:
                        self.game.board.move_piece(self.game.board.selected_piece, row, col)
                        self.game.board.deselect_piece()

                if event.button == 3:
                    self.game.board.deselect_piece()
                    self.game.board.undo_move()

    def render(self):
        self.game.screen.fill((30, 30, 30))
        self.game.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (WIDTH, HEIGHT)), (0, 0))
        self.game.screen.blit(self.game.top_screen, (0, 0))
        pygame.display.flip()
