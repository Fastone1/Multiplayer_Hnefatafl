from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from states.client import Client
from scripts.button import Button

import pygame
import socket
import re

class OnlineMode(State):
    def __init__(self, game: Game):
        super().__init__(game)

        button_pos = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
        button_size = (200, 50)
        button_color = (50, 50, 50)

        self.button_9x9 = Button(self.game, (button_pos[0] * 3 // 5, button_pos[1]), False, "9x9", self.game.font_small, button_size, button_color)
        self.button_11x11 = Button(self.game, (button_pos[0] * 7 // 5, button_pos[1]), False, "11x11", self.game.font_small, button_size, button_color)

        self.button_back = Button(self.game, (button_pos[0], button_pos[1] * 5 // 3), False, "Back", self.game.font_small, (100, 50), button_color)

        self.name = ""
        self.name_warning = 0
        self.name_warning_surf = pygame.Surface((150, 40))
        self.name_warning_surf.fill((30, 30, 30))
        self.name_warning_surf.set_alpha(0)

        self.input_box = pygame.Rect(self.game.screen.get_width() // 2 - 150, self.game.screen.get_height() // 2 + 75, 300, 50)
        self.writing = False
        self.deleting = 0
        self.inserting = 0

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    print("OnlineMode -> Title")

                if self.writing:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                        self.deleting = 6
                    elif event.key == pygame.K_RETURN:
                        pass
                    else:
                        if len(self.name) < 16 and re.match(r"[a-zA-Z0-9_]", event.unicode):
                            self.name += event.unicode
                            self.inserting = 7

            if event.type == pygame.KEYUP:
                if self.writing:
                    if event.key == pygame.K_BACKSPACE:
                        self.deleting = 0
                    else:
                        self.inserting = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_9x9.check_click():
                        if self.name == "":
                            self.name_warning = 6000
                        else:
                            try:
                                game_main = Client(self.game, 9, self.name)
                                game_main.enter_state()
                                print("OnlineMode -> Client")
                            except socket.error as e:
                                print(f"Connection refused: {e}")

                    if self.button_11x11.check_click():
                        if self.name == "":
                            self.name_warning = 6000
                        else:
                            try:
                                game_main = Client(self.game, 11, self.name)
                                game_main.enter_state()
                                print("OnlineMode -> Client")
                            except socket.error as e:
                                print(f"Connection refused: {e}")

                    if self.button_back.check_click():
                        self.exit_state()
                        print("OnlineMode -> Title")

                    if self.input_box.collidepoint(event.pos):
                        self.writing = True
                    else:
                        self.writing = False
                        self.deleting = 0
                        self.inserting = 0

        if self.deleting > 0:
            self.deleting -= 1
            if self.deleting == 0:
                self.name = self.name[:-1]
                self.deleting = 6

        if self.inserting > 0:
            self.inserting -= 1
            if self.inserting == 0 and len(self.name) < 16 and len(self.name) > 0:
                self.name += self.name[-1]
                self.inserting = 7

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

        if self.name_warning > 0:
            self.name_warning -= max(1, (6000 - self.name_warning) ** 2 // 10000)
            self.name_warning_surf.set_alpha(int(255 * (self.name_warning / 6000)))
            self.game.draw_text(self.name_warning_surf, "Enter a name", (245, 40, 30), self.name_warning_surf.get_width() // 2, self.name_warning_surf.get_height() // 2, self.game.font_small)
            surf.blit(self.name_warning_surf, (self.game.screen.get_width() // 2 - self.name_warning_surf.get_width() // 2, self.game.screen.get_height() // 2 - self.name_warning_surf.get_height() // 2 - 50))

        pygame.draw.rect(surf, (0, 0, 0), self.input_box, 0, 10)
        pygame.draw.rect(surf, (255, 255, 255), self.input_box, 2, 10)
        self.game.draw_text(surf, self.name, (255, 255, 255), self.input_box.centerx, self.input_box.centery, self.game.font_small)

        pygame.display.flip()