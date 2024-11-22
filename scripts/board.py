from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from scripts.constants import SQUARE_SIZE, WHITE, BLACK, ROOK, KING, DARK_TILE, LIGHT_TILE
from scripts.pieces import Piece
from scripts.move import Move
""""9x9": [
        (4, 4, WHITE, KING),
        (0, 4, BLACK, ROOK), (1, 4, BLACK, ROOK), (2, 4, WHITE, ROOK), (3, 4, WHITE, ROOK), (5, 4, WHITE, ROOK), (6, 4, WHITE, ROOK), (7, 4, BLACK, ROOK), (8, 4, BLACK, ROOK),
        (4, 0, BLACK, ROOK), (4, 1, BLACK, ROOK), (4, 2, WHITE, ROOK), (4, 3, WHITE, ROOK), (4, 5, WHITE, ROOK), (4, 6, WHITE, ROOK), (4, 7, BLACK, ROOK), (4, 8, BLACK, ROOK),
        (0, 3, BLACK, ROOK), (0, 5, BLACK, ROOK), (8, 3, BLACK, ROOK), (8, 5, BLACK, ROOK), (3, 0, BLACK, ROOK), (5, 0, BLACK, ROOK), (3, 8, BLACK, ROOK), (5, 8, BLACK, ROOK)
    ],"""
STARTING_POSITIONS = {
    
    "9x9": [
        (0, 1, WHITE, KING),
        (0, 2, BLACK, ROOK), (1, 2, BLACK, ROOK), (4, 8, BLACK, ROOK), (8, 4, BLACK, ROOK),
    ],
    "11x11": [
        (5, 5, WHITE, KING),
        (3, 5, WHITE, ROOK), (4, 4, WHITE, ROOK), (4, 5, WHITE, ROOK), (4, 6, WHITE, ROOK), (5, 3, WHITE, ROOK), (5, 4, WHITE, ROOK),
        (5, 6, WHITE, ROOK), (5, 7, WHITE, ROOK), (6, 4, WHITE, ROOK), (6, 5, WHITE, ROOK), (6, 6, WHITE, ROOK), (7, 5, WHITE, ROOK),
        (0, 3, BLACK, ROOK), (0, 4, BLACK, ROOK), (0, 5, BLACK, ROOK), (0, 6, BLACK, ROOK), (0, 7, BLACK, ROOK), (1, 5, BLACK, ROOK),
        (3, 0, BLACK, ROOK), (4, 0, BLACK, ROOK), (5, 0, BLACK, ROOK), (6, 0, BLACK, ROOK), (7, 0, BLACK, ROOK), (5, 1, BLACK, ROOK),
        (3, 10, BLACK, ROOK), (4, 10, BLACK, ROOK), (5, 10, BLACK, ROOK), (6, 10, BLACK, ROOK), (7, 10, BLACK, ROOK), (5, 9, BLACK, ROOK),
        (10, 3, BLACK, ROOK), (10, 4, BLACK, ROOK), (10, 5, BLACK, ROOK), (10, 6, BLACK, ROOK), (10, 7, BLACK, ROOK), (9, 5, BLACK, ROOK),
    ]
}

ADJECENT_SQUARES = [(0, 1), (0, -1), (1, 0), (-1, 0)]

class Board:
    def __init__(self, game: Game, width: int, height: int):
        self.game = game
        self.width = width
        self.height = height
        self.turn = BLACK
        self.winner = None
        self.board: list[Piece] = []
        self.list_of_moves: list[Move] = []
        self.create_board(width, height)
        self.starting_position()

    def create_board(self, size_width: int, size_height: int) -> None:
        for _ in range(size_height * size_width):
            self.board.append(None)

    def get_piece(self, row: int, col: int) -> Piece:
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return None

        return self.board[row * self.width + col]
    
    def set_piece(self, row: int, col: int, piece: Piece) -> None:
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return

        self.board[row * self.width + col] = piece

    def move_piece(self, piece: Piece, row: int, col: int) -> None:
        if piece is None or piece.color != self.turn:
            print("Not your turn")
            return
        
        if self.winner is not None:
            print("Game is over")
            return
        
        if not piece.check_legal_move(row, col):
            print("Illegal move")
            return
        
        self.set_piece(piece.row, piece.col, None)
        self.set_piece(row, col, piece)
        self.list_of_moves.append(Move(piece.row, piece.col, row, col))
        piece.move(row, col)

        for square in self.adjacent_squares(row, col):
            if piece.check_capture(square[0], square[1]):
                captured_piece = self.get_piece(square[0], square[1])
                self.list_of_moves[-1].is_capture = True
                self.list_of_moves[-1].captured_pieces.append(captured_piece)
                self.set_piece(square[0], square[1], None)

        self.turn = not self.turn
        self.check_winner()

        return True

    def undo_move(self) -> None:
        if len(self.list_of_moves) == 0:
            return
        
        self.turn = not self.turn

        move = self.list_of_moves.pop()
        piece = self.get_piece(move.to_row, move.to_col)
        self.set_piece(move.from_row, move.from_col, piece)
        piece.move(move.from_row, move.from_col)
        self.set_piece(move.to_row, move.to_col, None)
        
        if move.is_capture:
            for captured_piece in move.captured_pieces:
                self.set_piece(captured_piece.row, captured_piece.col, captured_piece)
                captured_piece.move(captured_piece.row, captured_piece.col)

    def check_winner(self) -> None:
        king = None
        legal_moves = 0
        for piece in self.board:
            if piece is not None:
                if piece.color == self.turn and piece.legal_moves() != []:
                    legal_moves += 1

                if piece.type == KING:
                    king = piece

        if legal_moves == 0:
            print("No legal moves")
            self.winner = BLACK if self.turn == WHITE else WHITE
            return

        if king is None:
            print("No king")
            self.winner = BLACK
            return

        if (king.row == 0 and king.col == 0) or (king.row == 0 and king.col == self.width - 1) or (king.row == self.height - 1 and king.col == 0) or (king.row == self.height - 1 and king.col == self.width - 1):
            print("King in castle")
            self.winner = WHITE
            return

    def starting_position(self) -> None:
        for row, col, color, type_p in STARTING_POSITIONS[f"{self.height}x{self.width}"]:
            piece = Piece(self.game, row, col, color, type_p)
            self.set_piece(row, col, piece)

    def adjacent_squares(self, row: int, col: int) -> list[tuple[int, int]]:
        squares = []
        for dr, dc in ADJECENT_SQUARES:
            r, c = row + dr, col + dc
            if 0 <= r < self.height and 0 <= c < self.width:
                squares.append((r, c))
        return squares
    
    def is_castle_empty(self, row: int, col: int) -> bool:
        topleft = row == 0 and col == 0
        topright = row == 0 and col == self.width - 1
        bottomleft = row == self.height - 1 and col == 0
        bottomnright = row == self.height - 1 and col == self.width - 1
        middle = row == self.height // 2 and col == self.width // 2

        return (topleft or topright or bottomleft or bottomnright or middle) and self.get_piece(row, col) is None

    def render(self, screen: pygame.Surface) -> None:
        light_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        light_tile.fill(LIGHT_TILE)
        dark_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        dark_tile.fill(DARK_TILE)

        for row in range(self.height):
            for col in range(self.width):
                if (row + col) % 2 == 0:
                    screen.blit(light_tile, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                else:
                    screen.blit(dark_tile, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        for row in range(self.height):
            for col in range(self.width):
                if self.board[row * self.width + col] is not None:
                    self.board[row * self.width + col].render(screen)
