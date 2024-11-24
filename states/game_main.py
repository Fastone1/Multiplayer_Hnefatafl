from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from scripts.constants import RENDER_SCALE, SQUARE_SIZE
from states.state import State

class GameMain(State):
    def __init__(self, game: Game):
        super().__init__(game)

    def update(self, actions: dict[str, bool]):
        if actions["exit"]:
            self.exit_state()
            print("GameMain -> Title")

        if actions["restart"]:
            self.game.board.reset()

        if actions["undo"]:
            self.game.board.undo_move()

        if actions["click"]:
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

        if actions["right_click"]:
            self.game.board.deselect_piece()
            self.game.board.undo_move()

    def render(self, surf: pygame.Surface):
        pass
