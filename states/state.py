from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from pygame import Surface
    
class State:
    def __init__(self, game: Game):
        self.game = game
        self.prev_state = None

    def update(self, actions: dict[str, bool]):
        pass

    def render(self, surf: Surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()            