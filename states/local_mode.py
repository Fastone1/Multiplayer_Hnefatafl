from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from states.choose_size import ChooseSize
from states.ai_mode import AIMode
from scripts.button import Button
from scripts.constants import BACKGROUND

import pygame

class LocalMode(State):
    def __init__(self, game: Game):
        super().__init__(game)

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)
        
        self.button_friend = Button(self.game, (button_pos[0], button_pos[1]), False, "Against Friend", self.game.font_small, button_size, button_color)
        self.button_bot = Button(self.game, (button_pos[0], button_pos[1] + 75), False, "Against Computer", self.game.font_small, button_size, button_color)

        self.button_back = Button(self.game, (button_pos[0], button_pos[1] * 5 // 3), False, "Back", self.game.font_small, (100, 50), button_color)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("LocalMode -> Title")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_friend.check_click():
                        choose_size = ChooseSize(self.game)
                        choose_size.enter_state()
                        print("LocalMode -> ChooseSize")
                    
                    if self.button_bot.check_click():
                        online_mode = AIMode(self.game, 9, 9)
                        online_mode.enter_state()
                        print("LocalMode -> AIMode")

                    if self.button_back.check_click():
                        self.exit_state()
                        print("LocalMode -> Title")

        self.button_friend.update()
        self.button_bot.update()
        self.button_back.update()

    def render(self):
        surf = self.game.screen
        surf.fill(BACKGROUND)
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (205, 205, 205), width // 2, height // 4, self.game.font_title)

        self.button_friend.render(surf)
        self.button_bot.render(surf)
        self.button_back.render(surf)

        