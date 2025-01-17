from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from states.choose_size import ChooseSize
from states.online_mode import OnlineMode
from scripts.button import Button

import pygame

class Title(State):
    def __init__(self, game: Game):
        super().__init__(game)

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)
        
        self.button_local = Button(self.game, (button_pos[0], button_pos[1]), False, "Local", self.game.font_small, button_size, button_color)
        self.button_online = Button(self.game, (button_pos[0], button_pos[1] + 75), False, "Online", self.game.font_small, button_size, button_color)
        
        self.choosing_size = False
        self.choosing_online = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("Title -> Exit")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_local.check_click():
                        choose_size = ChooseSize(self.game)
                        choose_size.enter_state()
                        print("Title -> ChooseSize")
                    
                    if self.button_online.check_click():
                        online_mode = OnlineMode(self.game)
                        online_mode.enter_state()
                        print("Title -> OnlineMode")

        self.button_local.update()
        self.button_online.update()
    
    def render(self):
        surf = self.game.screen
        surf.fill((30, 30, 30))
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (205, 205, 205), width // 2, height // 4, self.game.font_title)

        self.button_local.render(surf)
        self.button_online.render(surf)

        pygame.display.flip()