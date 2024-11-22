import pygame
import sys

# Constants
from scripts.constants import *

# Utility functions
from scripts.network import Network
from scripts.util import load_image, set_cursor
from scripts.board import Board

# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Hnefatafl")
        self.clock = pygame.time.Clock()
        self.running = True

        # State stack
        self.state_stack = []
        self.actions = {"click": False, "right_click": False, "esc": False}

        # Network
        #self.client = Network()

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
        self.font = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 32)

        # Cursor
        set_cursor(self.assets["mouse"])

        # Board
        self.board = Board(self, 9, 9)

        # Selected piece
        self.selected_piece = None

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            # Update
            if self.board.winner is not None:
                print(f'Winner: {"Black" if self.board.winner == BLACK else "White"}')
                self.board.reset(9, 9)

            # Render
            self.board.render(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.actions["esc"] = True

                    if event.key == pygame.K_r:
                        self.board = Board(self, 9, 9)
                        self.selected_piece = None

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.actions["esc"] = False
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.actions["click"] = True
                        x, y = pygame.mouse.get_pos() 
                        x, y = x // RENDER_SCALE, y // RENDER_SCALE
                        col = x // SQUARE_SIZE
                        row = y // SQUARE_SIZE
                        if self.selected_piece is not None:
                            if self.selected_piece.row != row or self.selected_piece.col != col:
                                self.board.move_piece(self.selected_piece, row, col)
                            self.deselect_piece()
                        else:
                            piece = self.board.get_piece(row, col)
                            self.select_piece(piece)

                    if event.button == 3:
                        self.actions["right_click"] = True
                        self.deselect_piece()
                        self.board.undo_move()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.actions["click"] = False

                    if event.button == 3:
                        self.actions["right_click"] = False

            self.screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def select_piece(self, piece):
        if piece is not None:
            piece.selected = True
            self.selected_piece = piece
        else:
            self.selected_piece = None

    def deselect_piece(self):
        if self.selected_piece is not None:
            self.selected_piece.selected = False
            self.selected_piece = None

    def draw_text(self, surf: pygame.Surface, text: str, color: tuple[int, int, int], x: int, y: int):
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        surf.blit(text_surf, text_rect)

if __name__ == "__main__":
    game = Game()
    game.run()