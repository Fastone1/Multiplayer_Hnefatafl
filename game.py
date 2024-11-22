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
        self.board = Board(self, 9, 9)

        # Selected piece
        self.selected_piece = None

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            # Update
            if self.board.winner is not None:
                print(f"Winner: {"Black" if self.board.winner == BLACK else "White"}")
                self.running = False

            # Render
            self.board.render(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    if event.key == pygame.K_r:
                        self.board = Board(self, 9, 9)
                        self.selected_piece = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
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
                        self.deselect_piece()
                        self.board.undo_move()

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

if __name__ == "__main__":
    game = Game()
    game.run()