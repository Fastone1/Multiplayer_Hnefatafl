import pygame
import sys
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Constants
from scripts.constants import *

# Utility functions
from scripts.util import load_image, set_cursor, load_font, load_sound, load_music
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

        # Error handling
        self.error = 0
        self.error_msg = ""
        self.error_surf = pygame.Surface((150, 40))
        self.error_surf.fill((30, 30, 30))
        self.error_surf.set_alpha(200)

        # State stack
        self.state_stack: list[State] = []

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
        self.font_title = load_font("Grand9K_Pixel.ttf", 64)
        self.font_big = load_font("Grand9K_Pixel.ttf", 32)
        self.font_small = load_font("Grand9K_Pixel.ttf", 16)

        # Sounds
        self.sounds: dict[str, pygame.mixer.Sound] = {
            "move": load_sound("move.wav"),
            "start": load_sound("start.wav"),
            "end": load_sound("end.wav"),
        }
        self.sounds["end"].set_volume(0.5)
        self.sounds["start"].set_volume(0.3)

        # Music
        load_music("music.wav")
        pygame.mixer.music.set_volume(0.5)
        # Cursor
        set_cursor(self.assets["mouse"])

        # Initial state
        title = Title(self)
        title.enter_state()

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
        self.state_stack[-1].update()

    def render(self):
        self.state_stack[-1].render()

        if self.error > 0:
            self.error -= max(1, (6000 - self.error) ** 2 // 10000)

            
        pygame.display.flip()

    def draw_text(self, surf: pygame.Surface, text: str, color: tuple[int, int, int], x: int, y: int, font: pygame.font.Font):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        surf.blit(text_surf, text_rect)

    def loading_screen(self):
        self.screen.fill((30, 30, 30))
        self.draw_text(self.screen, "Loading...", (205, 205, 205), self.screen.get_width() // 2, self.screen.get_height() // 2, self.font_big)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()