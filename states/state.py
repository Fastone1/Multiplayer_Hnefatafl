from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
    
class State:
    def __init__(self, game: Game):
        self.game = game
        self.prev_state = None

    def update(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)
        self.game.reset_error()

    def exit_state(self):
        if len(self.game.state_stack) > 1:
            self.game.state_stack.pop()
        else:
            self.game.running = False
        self.game.reset_error()