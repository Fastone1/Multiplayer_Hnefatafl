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
        self.top_screen = pygame.Surface((WIDTH + SIDE_PANEL, HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption("Hnefatafl")
        self.clock = pygame.time.Clock()
        self.running = True

        # State stack
        self.state_stack: list[State] = [Title(self)]   # Start with the title screen
        self.actions = {
            "click": False,
            "right_click": False,
            "esc": False,
            "restart": False, 
            "start": False,
            "exit": False,
            "undo": False,
        }

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
            "mouse": load_image("mouse.png"),
            "castle_tile": load_image("castle_tile.png"),
        }

        # Font
        self.font_title = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 64)
        self.font_big = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 32)
        self.font_small = pygame.font.Font("assets/fonts/Grand9K_Pixel.ttf", 16)

        # Cursor
        set_cursor(self.assets["mouse"])
        self.scroll = 0

        # Board
        self.board = Board(self, 9, 9)

    def run(self):
        while self.running:
            # Update
            self.update()

            # Render
            self.render()
            
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def update(self):
        self.state_stack[-1].update(self.actions)

    def render(self):
        self.state_stack[-1].render()

    def reset_keys(self):
        for key in self.actions:
            self.actions[key] = False

    def draw_text(self, surf: pygame.Surface, text: str, color: tuple[int, int, int], x: int, y: int, font: pygame.font.Font):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        surf.blit(text_surf, text_rect)

    def adjust_scroll_to_bottom(self):
        spacing = len(self.board.list_of_moves) * 24 - self.screen.get_height() // 2
        if spacing > 0:
            self.scroll = -spacing

if __name__ == "__main__":
    game = Game()
    game.run()