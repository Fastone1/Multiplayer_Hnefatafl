from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from states.state import State
from scripts.connection import Client
from scripts.constants import RENDER_SCALE, SQUARE_SIZE, SIDE_PANEL, WIDTH, HEIGHT, END_CONNECTION
from scripts.board import Board


class JoinState(State):
    def __init__(self, game: Game, client: Client, server_id: int):
        super().__init__(game)

        self.client = client
        self.client.connect(server_id)
        self.reset_proposed = [False, False]

        self.client.send("size", self.client.socket)
        msg = self.client.recv(self.client.socket)
        if msg.startswith("size"):
            size = msg.split()[1:]
            width, height = int(size[0]), int(size[1])
        else:
            print("Error: size")
            self.exit_state()
            return
        
        self.width = width * SQUARE_SIZE * RENDER_SCALE
        self.height = height * SQUARE_SIZE * RENDER_SCALE
        
        self.game.screen = pygame.display.set_mode((self.width + SIDE_PANEL, self.height))
        self.game.board_display = pygame.Surface((self.width // RENDER_SCALE, self.height // RENDER_SCALE))
        self.game.top_screen = pygame.Surface((self.width + SIDE_PANEL, self.height), pygame.SRCALPHA)

        self.scroll = 0
        self.board = Board(self.game, width, height)