import pygame
import sys

# Constants
from scripts.constants import WIDTH, HEIGHT, WHITE, BLACK, ROOK, KING, RENDER_SCALE, SQUARE_SIZE

# Utility functions
from scripts.network import Network
from scripts.util import load_image, set_cursor
from scripts.board import Board

# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display = pygame.Surface((WIDTH // 4, HEIGHT // 4))
        pygame.display.set_caption("Hnefatafl")
        self.clock = pygame.time.Clock()
        self.running = True

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

        # Cursor
        set_cursor(self.assets["mouse"])

        # Board
        self.board = Board(self, 11, 11)

        # Selected piece
        self.selected_piece = None

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            # Update

            # Render
            self.board.render(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos() 
                        x, y = x // RENDER_SCALE, y // RENDER_SCALE
                        col = x // SQUARE_SIZE
                        row = y // SQUARE_SIZE
                        
                        if self.selected_piece is not None:
                            if self.selected_piece.row != row or self.selected_piece.col != col:
                                self.selected_piece.move(row, col)
                            self.selected_piece = None
                        else:
                            piece = self.board.get_piece(row, col)
                            if piece is not None:
                                self.selected_piece = piece

            self.screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()