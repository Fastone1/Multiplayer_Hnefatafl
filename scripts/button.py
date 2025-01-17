from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

class Button():
    def __init__(self, game:Game, pos:tuple[int, int], single_click:bool, text:str, font:pygame.font.Font, size:tuple[int, int] = (100, 50), color:tuple[int, int, int] = (50, 50, 50)) -> None:
        super().__init__()
        self.game = game

        self.text = text
        self.size = size
        self.original_size = size
        self.font = font
        self.color = color
        self.anti_color = (255 - color[0], 255 - color[1], 255 - color[2])

        self.image = pygame.Surface(size)
        self.image.fill(color)
        text:pygame.Surface = self.font.render(text, True, self.anti_color)
        self.image.blit(text, (self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2))

        self.rect = self.image.get_rect(center=pos)
        self.pos = pos

        self.single_click = single_click
        self.clicked = False

    def change_text(self, text:str) -> None:
        self.text = text
        self.image.fill(self.color)
        text:pygame.Surface = self.font.render(text, True, self.anti_color)
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
    
    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.change_size((self.original_size[0] * 1.1, self.original_size[1] * 1.1))
        else:
            self.change_size(self.original_size)

    def change_size(self, size:tuple[int, int]) -> None:
        self.size = size
        self.image = pygame.Surface(size)
        self.image.fill(self.color)
        text:pygame.Surface = self.font.render(self.text, True, self.anti_color)
        self.image.blit(text, (self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2))

        self.rect = self.image.get_rect(center=self.pos)
    
    def render(self, surf:pygame.Surface, offset:tuple[int, int] = (0, 0)) -> None:
        pygame.draw.rect(surf, self.color, self.rect.move(offset), 0, 10)
        surf.blit(self.image, self.rect.move(offset))
        pygame.draw.rect(surf, self.anti_color, self.rect.move(offset), 2, 10)
