from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from scripts.constants import WIDTH, HEIGHT, SIDE_PANEL

from states.state import State
from scripts.button import Button
from scripts.connection import Client
from states.join import JoinState

class JoinChooseServerState(State):
    def __init__(self, game: Game):
        super().__init__(game)
        self.scroll = 0

        self.client = Client()
        self.servers_len = 0

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)

        for i, server in enumerate(self.client.servers_ip):
            button = Button(self.game, (button_pos[0], button_pos[1] + i * 100), False, server, self.game.font_small, button_size, button_color)
            setattr(self, f"button_{i}", button)
            self.servers_len += 1

        self.button_back = Button(self.game, (button_pos[0], button_pos[1] * 3 // 2), False, "Back", self.game.font_small, (100, 50), button_color)

    def update(self):
        if len(self.client.servers_ip) != self.servers_len:
            self.servers_len = 0
            for i, server in enumerate(self.client.servers_ip):
                button = Button(self.game, (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2 + i * 50), False, server, self.game.font_small, (200, 50), (50, 50, 50))
                setattr(self, f"button_{i}", button)
                self.servers_len += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                self.client.close_connection()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_state()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_back.check_click():
                        self.close_state()

                    for i in range(self.servers_len):
                        if getattr(self, f"button_{i}").check_click():
                            join = JoinState(self.game, self.client, i)
                            join.enter_state()
                            print(f"JoinChooseServer -> Join {i}")

                if event.button == 4:
                    self.scroll = min(self.scroll + 50, 0)
                if event.button == 5:
                    self.scroll = max(self.scroll - 50, -100 * (self.servers_len - 1))

    def close_state(self):
        self.exit_state()

        self.game.loading_screen()

        self.client.close_connection()
        print("JoinChooseServer -> HostJoin")


    def render(self):
        surf = self.game.screen
        surf.fill((30, 30, 30))
        width, height = surf.get_width(), surf.get_height()
        self.game.draw_text(surf, "Hnefatafl", (205, 205, 205), width // 2, height // 4, self.game.font_title)

        for i in range(self.servers_len):
            getattr(self, f"button_{i}").render(surf, offset=(0, self.scroll))

        self.button_back.render(surf)

        pygame.display.flip()