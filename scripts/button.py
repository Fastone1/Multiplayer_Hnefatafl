from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, game:Game, pos:tuple[int, int], image:pygame.Surface|None, single_click:bool, text:str=None) -> None:
        super().__init__()
        self.game = game

        self.text = text
        self.image = image
        if not image:
            self.image = pygame.Surface((100, 50))
            self.image.fill((50, 50, 50))
            text:pygame.Surface = self.game.font_small.render(text, True, (255, 255, 255))
            self.image.blit(text, (self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2))

        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos

        self.single_click = single_click
        self.clicked = False

    def change_text(self, text:str) -> None:
        self.text = text
        self.image.fill((50, 50, 50))
        text:pygame.Surface = self.game.font_small.render(text, True, (255, 255, 255))
        self.image.blit(text, (self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2))

    def check_click(self) -> None:
        # reset the clicked flag
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # check if the mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                if self.single_click:
                    self.clicked = True
                return True

        return False
    
    def render(self, surf:pygame.Surface) -> None:
        pygame.draw.rect(surf, (50, 50, 50), self.rect)
        if self.image:
            surf.blit(self.image, self.rect.topleft)
        pygame.draw.rect(surf, (200, 200, 200), self.rect, 2)
