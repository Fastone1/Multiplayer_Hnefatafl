from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, SIDE_PANEL, WIDTH, HEIGHT
from states.state import State
from scripts.board import VisualBoard

class GameMain(State):
    def __init__(self, game: Game, width:int, height:int):
        super().__init__(game)

        pygame.mixer.music.fadeout(500)
        self.game.sounds["start"].play()

        self.width = width * SQUARE_SIZE * RENDER_SCALE
        self.height = height * SQUARE_SIZE * RENDER_SCALE

        self.game.screen = pygame.display.set_mode((self.width + SIDE_PANEL, self.height))
        self.game.board_display = pygame.Surface((self.width // RENDER_SCALE, self.height // RENDER_SCALE))

        self.board = VisualBoard(self.game, width, height)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    pygame.mixer.music.play(-1)
                    self.game.screen = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
                    self.game.board_display = pygame.Surface((WIDTH // RENDER_SCALE, HEIGHT // RENDER_SCALE))
                    print("GameMain -> ChooseSize")

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

                if event.button == 4:
                    self.board.scroll = min(0, self.board.scroll + 16)

                if event.button == 5:
                    spacing = len(self.board.list_of_moves) * 24 - self.game.screen.get_height() // 2
                    if spacing > 0:
                        self.board.scroll = max(-spacing, self.board.scroll - 16)

    def render(self):
        self.game.screen.fill((30, 30, 30))
        self.board.render()
        self.game.screen.blit(pygame.transform.scale(self.game.board_display, (self.width, self.height)), (0, 0))

        text = "Press R to restart"
        self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 32, self.game.font_small)

        text = "Press right click to undo"
        self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 64, self.game.font_small)

        text = "Press ESC to go back"
        self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, 96, self.game.font_small)
        pygame.display.flip()
