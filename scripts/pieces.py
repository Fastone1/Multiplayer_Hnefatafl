from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from scripts.constants import SQUARE_SIZE, WHITE, BLACK, ROOK, KING

ADJECENT_SQUARES = [(0, 1), (0, -1), (1, 0), (-1, 0)]

class Piece:
    def __init__(self, game: Game, row: int, col: int, color: int, type_p: int):
        self.game = game
        self.row = row
        self.col = col
        self.color = color
        self.type = type_p
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE

    def move(self, row: int, col: int):
        self.row = row
        self.col = col
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE

    def check_capture(self, row: int, col: int) -> bool:
        piece = self.game.board.get_piece(row, col)
        
        if piece is None:
            return False
        
        if piece.color != self.color:
            if piece.type == ROOK:
                direction = (row - self.row, col - self.col)
                opposite_piece = self.game.board.get_piece(row + direction[0], col + direction[1])
                return (opposite_piece is not None and opposite_piece.color == self.color) or self.game.board.is_castle_empty(row + direction[0], col + direction[1])
            elif piece.type == KING:
                orthogonal = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                orthogonal_pieces = [self.game.board.get_piece(row + dr, col + dc) for dr, dc in orthogonal]
                return all((piece is not None and piece.color == self.color) or self.game.board.is_castle_empty(row + dr, col + dc) for piece, (dr, dc) in zip(orthogonal_pieces, orthogonal))

    def check_legal_move(self, row: int, col: int) -> bool:
        raise NotImplementedError
    
    def legal_moves(self) -> list[tuple[int, int]]:
        raise NotImplementedError

    def check_legal_move(self, row: int, col: int) -> bool:
        if row != self.row and col != self.col:
            return False
        
        if row == self.row:
            for c in range(min(self.col, col) + 1, max(self.col, col)):
                if self.game.board.get_piece(row, c) is not None:
                    return False
                
        if col == self.col:
            for r in range(min(self.row, row) + 1, max(self.row, row)):
                if self.game.board.get_piece(r, col) is not None:
                    return False
        
        return True
    
    def legal_moves(self) -> list[tuple[int, int]]:
        moves = []
        
        for r in range(self.game.board.height):
            if r != self.row:
                if self.check_legal_move(r, self.col):
                    moves.append((r, self.col))
        
        for c in range(self.game.board.width):
            if c != self.col:
                if self.check_legal_move(self.row, c):
                    moves.append((self.row, c))
        
        return moves
    
    def render(self, screen: pygame.Surface):
        asset = self.game.assets[self.color][self.type]
        screen.blit(asset, (self.x, self.y))

    def __repr__(self) -> str:
        color = "White" if self.color == WHITE else "Black"
        type_p = "Rook" if self.type == ROOK else "King"
        return f"{color} {type_p} at ({self.row}, {self.col})"
    
    def __str__(self) -> str:
        color = "White" if self.color == WHITE else "Black"
        type_p = "Rook" if self.type == ROOK else "King"
        return f"{color} {type_p} at ({self.row}, {self.col})"
    
    def __eq__(self, other: Piece) -> bool:
        return self.row == other.row and self.col == other.col and self.color == other.color and self.type == other.type

    def __ne__(self, other: Piece) -> bool:
        return not self == other
    
class Rook(Piece):
    def __init__(self, game: Game, row: int, col: int, color: int):
        super().__init__(game, row, col, color, ROOK)

class King(Piece):
    def __init__(self, game: Game, row: int, col: int, color: int):
        super().__init__(game, row, col, color, KING)