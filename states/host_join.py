from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from states.state import State
from scripts.button import Button
from states.host import HostState
from states.join_choose_server import JoinChooseServerState

class HostJoinState(State):
    def __init__(self, game: Game):
        super().__init__(game)

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)

        self.button_host = Button(self.game, (button_pos[0] * 3 // 5, button_pos[1]), False, "Host", self.game.font_small, button_size, button_color)
        self.button_join = Button(self.game, (button_pos[0] * 7 // 5, button_pos[1]), False, "Join", self.game.font_small, button_size, button_color)

        self.button_back = Button(self.game, (button_pos[0], button_pos[1] * 3 // 2), False, "Back", self.game.font_small, (100, 50), button_color)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("HostJoin -> Title")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_host.check_click():
                        host = HostState(self.game, 9, 9)
                        host.enter_state()
                        print("HostJoin -> Host")

                    if self.button_join.check_click():
                        join = JoinChooseServerState(self.game)
                        join.enter_state()
                        print("HostJoin -> Join")

                    if self.button_back.check_click():
                        self.exit_state()
                        print("HostJoin -> Title")

    def render(self):
        surf = self.game.screen
        surf.fill((30, 30, 30))
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (205, 205, 205), width // 2, height // 4, self.game.font_title)

        self.button_host.render(surf)
        self.button_join.render(surf)

        self.button_back.render(surf)

        pygame.display.flip()