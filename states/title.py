from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from states.state import State
from pygame import Surface

class Title(State):
    def __init__(self, game: Game):
        super().__init__(game)

    def update(self, actions: dict[str, bool]):
        pass

    def render(self, surf: Surface):
        pass
    