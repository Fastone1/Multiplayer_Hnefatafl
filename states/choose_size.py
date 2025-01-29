from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from states.game_main import GameMain
from scripts.button import Button

import pygame

class ChooseSize(State):
    def __init__(self, game: Game):
        super().__init__(game)

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)

        self.button_9x9 = Button(self.game, (button_pos[0] * 3 // 5, button_pos[1]), False, "9x9", self.game.font_small, button_size, button_color)
        self.button_11x11 = Button(self.game, (button_pos[0] * 7 // 5, button_pos[1]), False, "11x11", self.game.font_small, button_size, button_color)

        self.button_back = Button(self.game, (button_pos[0], button_pos[1] * 5 // 3), False, "Back", self.game.font_small, (100, 50), button_color)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("ChooseSize -> Title")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_9x9.check_click():
                        game_main = GameMain(self.game, 9, 9)
                        game_main.enter_state()
                        print("ChooseSize -> GameMain")

                    if self.button_11x11.check_click():
                        game_main = GameMain(self.game, 11, 11)
                        game_main.enter_state()
                        print("ChooseSize -> GameMain")

                    if self.button_back.check_click():
                        self.exit_state()
                        print("ChooseSize -> Title")

        self.button_9x9.update()
        self.button_11x11.update()
        self.button_back.update()
    
    def render(self):
        surf = self.game.screen
        surf.fill((30, 30, 30))
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (205, 205, 205), width // 2, height // 4, self.game.font_title)

        self.button_9x9.render(surf)
        self.button_11x11.render(surf)

        self.button_back.render(surf)
