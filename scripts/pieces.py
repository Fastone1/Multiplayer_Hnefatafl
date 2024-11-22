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
        self.selected = False
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
        '''
        Check if the piece can capture the piece at the given row and column.

        Parameters:
            row (int): The row of the piece to capture.
            col (int): The column of the piece to capture.

        Returns:
            bool: True if the piece can capture the piece at the given row and column, False otherwise.
        '''
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
                print(orthogonal_pieces)
                print(all((ortho_piece is not None and ortho_piece.color == BLACK) or \
                            self.game.board.is_castle_empty(row + dr, col + dc) or \
                             (row + dr < 0 or row + dr >= self.game.board.height or col + dc < 0 or col + dc >= self.game.board.width) \
                             for ortho_piece, (dr, dc) in zip(orthogonal_pieces, orthogonal)))
                return all((ortho_piece is not None and ortho_piece.color == BLACK) or \
                           self.game.board.is_castle_empty(row + dr, col + dc) or \
                            (row + dr < 0 or row + dr >= self.game.board.height or col + dc < 0 or col + dc >= self.game.board.width) \
                            for ortho_piece, (dr, dc) in zip(orthogonal_pieces, orthogonal))

    def check_legal_move(self, row: int, col: int) -> bool:
        if (row != self.row and col != self.col) or (row == self.row and col == self.col):
            return False

        if self.game.board.get_piece(row, col) is not None:
            return False
        
        if self.type != KING and \
            ((row == 0 and col == 0) or \
             (row == 0 and col == self.game.board.width - 1) or \
             (row == self.game.board.height - 1 and col == 0) or \
             (row == self.game.board.height - 1 and col == self.game.board.width - 1) or \
             (row == self.game.board.height // 2 and col == self.game.board.width // 2)):
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
            if self.check_legal_move(r, self.col):
                moves.append((r, self.col))
        
        for c in range(self.game.board.width):
            if self.check_legal_move(self.row, c):
                moves.append((self.row, c))

        return moves
    
    def render(self, screen: pygame.Surface):
        asset = self.game.assets[self.color][self.type]
        screen.blit(asset, (self.x, self.y))
        if self.selected:
            pygame.draw.rect(screen, (10, 240, 10), (self.x, self.y, SQUARE_SIZE, SQUARE_SIZE), 1)
            for tile in self.legal_moves():
                pygame.draw.rect(screen, (240, 10, 10), (tile[1] * SQUARE_SIZE, tile[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)

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