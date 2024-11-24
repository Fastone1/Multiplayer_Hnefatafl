import pygame
import sys

# Constants
from scripts.constants import *

# Utility functions
from scripts.connection import Connection
from scripts.util import load_image, set_cursor
from scripts.board import Board
from states.state import State
from states.title import Title

# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.size = (9, 9)
        self.screen = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
        self.board_display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Hnefatafl")
        self.clock = pygame.time.Clock()
        self.running = True

        # State stack
        self.state_stack: list[State] = [Title(self)]
        self.load_initial_states()
        self.actions = {"click": False, "right_click": False, "esc": False, "restart": False, "start": False}

        # Connection
        #self.connection = Connection()

        # Assets
        self.assets = {
            WHITE: {
                ROOK: load_image("white_rook.png"),
                KING: load_image("white_king.png")
            },
            BLACK: {
                ROOK: load_image("black_rook.png"),
            },
            "mouse": load_image("mouse.png")
        }

        # Font
        self.font_big = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 32)
        self.font_small = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 16)

        # Cursor
        set_cursor(self.assets["mouse"])
        self.scroll = 0

        # Board
        self.board = Board(self, 9, 9)

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            # Update
            if self.board.winner is not None:
                print(f'Winner: {"Black" if self.board.winner == BLACK else "White"}')
                self.board.reset(9, 9)

            # Render
            self.board.render(self.board_display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.actions["esc"] = True

                    if event.key == pygame.K_RETURN:
                        self.actions["start"] = True

                    if event.key == pygame.K_r:
                        self.actions["restart"] = True
                        self.board.reset(9, 9)
                        self.board.deselect_piece()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.actions["esc"] = False

                    if event.key == pygame.K_RETURN:
                        self.actions["start"] = True

                    if event.key == pygame.K_r:
                        self.actions["restart"] = False
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.actions["click"] = True
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
                        self.actions["right_click"] = True
                        self.board.deselect_piece()
                        self.board.undo_move()

                    if event.button == 4:
                        self.scroll += 8

                    if event.button == 5:
                        self.scroll -= 8

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.actions["click"] = False

                    if event.button == 3:
                        self.actions["right_click"] = False

            self.screen.blit(pygame.transform.scale(self.board_display, (WIDTH, HEIGHT)), (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def update(self):
        self.state_stack[-1].update(self.actions)

    def render(self):
        self.state_stack[-1].render(self.screen)

    def draw_text(self, surf: pygame.Surface, text: str, color: tuple[int, int, int], x: int, y: int, font: pygame.font.Font):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        surf.blit(text_surf, text_rect)

    def load_initial_states(self):
        title_screen = Title(self)
        title_screen.enter_state()

if __name__ == "__main__":
    game = Game()
    game.run()