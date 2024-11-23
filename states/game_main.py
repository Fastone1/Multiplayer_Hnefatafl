from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from states.state import State

class GameMain(State):
    def __init__(self, game: Game):
        super().__init__(game)
