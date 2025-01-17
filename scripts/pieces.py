from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.board import Board

import pygame

from scripts.constants import SQUARE_SIZE, WHITE, BLACK, ROOK, KING

ADJECENT_SQUARES = [(0, 1), (0, -1), (1, 0), (-1, 0)]

class Piece:
    def __init__(self, board: Board, row: int, col: int, color: int, type_p: int):
        self.board = board
        self.row = row
        self.col = col
        self.color = color
        self.type = type_p

    def move(self, row: int, col: int):
        self.row = row
        self.col = col

    def check_capture(self, row: int, col: int) -> bool:
        '''
        Check if the piece can capture the piece at the given row and column.

        Parameters:
            row (int): The row of the piece to capture.
            col (int): The column of the piece to capture.

        Returns:
            bool: True if the piece can capture the piece at the given row and column, False otherwise.
        '''
        piece = self.board.get_piece(row, col)
        
        if piece is None:
            return False
        
        if piece.color != self.color:
            if piece.type == ROOK:
                direction = (row - self.row, col - self.col)
                opposite_piece = self.board.get_piece(row + direction[0], col + direction[1])
                return (opposite_piece is not None and opposite_piece.color == self.color) or self.board.is_empty_castle(row + direction[0], col + direction[1])
            elif piece.type == KING:
                orthogonal = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                orthogonal_pieces = [self.board.get_piece(row + dr, col + dc) for dr, dc in orthogonal]
                return all((ortho_piece is not None and ortho_piece.color == BLACK) or \
                           self.board.is_empty_castle(row + dr, col + dc) or \
                            (row + dr < 0 or row + dr >= self.board.height or col + dc < 0 or col + dc >= self.board.width) \
                            for ortho_piece, (dr, dc) in zip(orthogonal_pieces, orthogonal))

    def check_legal_move(self, row: int, col: int) -> bool:
        if (row != self.row and col != self.col) or (row == self.row and col == self.col):
            return False

        if self.board.get_piece(row, col) is not None:
            return False
        
        if self.type != KING and (row, col) in self.board.CASTLE_POSITIONS:
            return False
        
        if row == self.row:
            for c in range(min(self.col, col) + 1, max(self.col, col)):
                if self.board.get_piece(row, c) is not None:
                    return False
                
        if col == self.col:
            for r in range(min(self.row, row) + 1, max(self.row, row)):
                if self.board.get_piece(r, col) is not None:
                    return False
        
        return True
    
    def legal_moves(self) -> list[tuple[int, int]]:
        moves = []
        
        for r in range(self.board.height):
            if self.check_legal_move(r, self.col):
                moves.append((r, self.col))
        
        for c in range(self.board.width):
            if self.check_legal_move(self.row, c):
                moves.append((self.row, c))

        return moves
    
    def render(self, screen: pygame.Surface):
        asset = self.board.assets[self.color][self.type]
        x, y = self.col * SQUARE_SIZE, self.row * SQUARE_SIZE
        screen.blit(asset, (x, y))
        
    def __repr__(self) -> str:
        color = "Red" if self.color == WHITE else "Blue"
        type_p = "Rook" if self.type == ROOK else "King"
        return f"{color} {type_p} at ({self.row}, {self.col})"
    
    def __str__(self) -> str:
        type_p = "R" if self.type == ROOK else "K"
        if self.color == WHITE:
            return type_p
        return type_p.lower()

    
    def __eq__(self, other: Piece) -> bool:
        return self.row == other.row and self.col == other.col and self.color == other.color and self.type == other.type

    def __ne__(self, other: Piece) -> bool:
        return not self == other
    
class Rook(Piece):
    def __init__(self, board: Board, row: int, col: int, color: int):
        super().__init__(board, row, col, color, ROOK)

class King(Piece):
    def __init__(self, board: Board, row: int, col: int, color: int):
        super().__init__(board, row, col, color, KING)