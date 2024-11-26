from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from states.game_main import GameMain
from scripts.button import Button

import pygame

class Title(State):
    def __init__(self, game: Game):
        super().__init__(game)

        self.buttons = [
            Button("Local", 100, 200, 200, 50),
            Button("Multiplayer", 100, 300, 200, 50),
        ]

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

            if event.type == pygame.MOUSEBUTTONUP:
                new_state = GameMain(self.game)
                new_state.enter_state()
                print("Title -> GameMain")
    
    def render(self):
        surf = self.game.screen
        surf.fill((30, 30, 30))
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (255, 255, 255), width // 2, height // 4, self.game.font_title)

        for button in self.buttons:
            button.render(surf)

        pygame.display.flip()