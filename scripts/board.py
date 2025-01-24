from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from scripts.constants import SQUARE_SIZE, WHITE, BLACK, ROOK, KING, DARK_TILE, LIGHT_TILE, SIDE_PANEL, DEBUG
from scripts.pieces import Piece
from scripts.move import Move

STARTING_POSITIONS = {
    "9x9": [
        (4, 4, WHITE, KING),
        (0, 4, BLACK, ROOK), (1, 4, BLACK, ROOK), (2, 4, WHITE, ROOK), (3, 4, WHITE, ROOK), (5, 4, WHITE, ROOK), (6, 4, WHITE, ROOK), (7, 4, BLACK, ROOK), (8, 4, BLACK, ROOK),
        (4, 0, BLACK, ROOK), (4, 1, BLACK, ROOK), (4, 2, WHITE, ROOK), (4, 3, WHITE, ROOK), (4, 5, WHITE, ROOK), (4, 6, WHITE, ROOK), (4, 7, BLACK, ROOK), (4, 8, BLACK, ROOK),
        (0, 3, BLACK, ROOK), (0, 5, BLACK, ROOK), (8, 3, BLACK, ROOK), (8, 5, BLACK, ROOK), (3, 0, BLACK, ROOK), (5, 0, BLACK, ROOK), (3, 8, BLACK, ROOK), (5, 8, BLACK, ROOK)
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
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.ready = False
        self.player1 = "Blue"
        self.player2 = "Red"

        self.turn = BLACK
        self.winner = None
        self.board: list[Piece] = []
        self.list_of_moves: list[Move] = []
        self.selected_piece: Piece = None

        self.create_board(width, height)
        self.starting_position()

        self.END_POSITIONS = [(0, 0), (0, self.width - 1), (self.height - 1, 0), (self.height - 1, self.width - 1)]
        self.CASTLE_POSITIONS = [(0, 0), (0, self.width - 1), (self.height - 1, 0), (self.height - 1, self.width - 1), (self.height // 2, self.width // 2)]

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

    def move_piece(self, piece: Piece, row: int, col: int) -> bool:
        if piece is None:
            if DEBUG:
                print("No piece selected")
            return False
            
        if piece.color != self.turn:
            if DEBUG:
                print("Not your turn")
            return False
        
        if self.winner is not None:
            if DEBUG:
                print("Game is over")
            return False
        
        if not piece.check_legal_move(row, col):
            if DEBUG:
                print("Illegal move")
            return False
        
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
    
    def move_piece_by_move(self, move: Move) -> bool:
        piece = self.get_piece(move.from_row, move.from_col)
        return self.move_piece(piece, move.to_row, move.to_col)
    
    def is_capture(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return False
        
        if piece.color != self.turn:
            return False
        
        for square in self.adjacent_squares(to_row, to_col):
            if piece.check_capture(*square):
                return True
        
        return False
    
    def move_is_capture(self, move: Move) -> bool:
        return self.is_capture(move.from_row, move.from_col, move.to_row, move.to_col)
    
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

        if self.winner is not None:
            self.winner = None

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
            if DEBUG:
                print("No legal moves")
            self.winner = BLACK if self.turn == WHITE else WHITE
            return

        if king is None:
            if DEBUG:
                print("King captured")
            self.winner = BLACK
            return

        if (king.row, king.col) in self.END_POSITIONS:
            if DEBUG:
                print("King in castle")
            self.winner = WHITE
            return

    def starting_position(self) -> None:
        for row, col, color, type_p in STARTING_POSITIONS[f"{self.height}x{self.width}"]:
            piece = Piece(self, row, col, color, type_p)
            self.set_piece(row, col, piece)

    def select_piece(self, piece):
        if piece is not None:
            self.selected_piece = piece
        else:
            self.selected_piece = None

    def deselect_piece(self):
        self.selected_piece = None

    def reset(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.board = []
        self.create_board(self.width, self.height)
        self.starting_position()
        self.turn = BLACK
        self.winner = None
        self.list_of_moves = []
        self.selected_piece = None
        self.scroll = 0

    def adjacent_squares(self, row: int, col: int) -> list[tuple[int, int]]:
        squares = []
        for dr, dc in ADJECENT_SQUARES:
            r, c = row + dr, col + dc
            if 0 <= r < self.height and 0 <= c < self.width:
                squares.append((r, c))
        return squares
    
    def is_empty_castle(self, row: int, col: int) -> bool:
        '''
        Check if a square is a castle square and is empty
        '''
        is_castle = (row, col) in self.CASTLE_POSITIONS
        return is_castle and self.get_piece(row, col) is None
    
    def __str__(self):
        board_str = ""
        for row in range(self.height):
            for col in range(self.width):
                piece = self.get_piece(row, col)
                if piece is not None:
                    board_str += str(piece) + " "
                else:
                    board_str += ". "
            board_str += "\n"
        return board_str[:-1]


class VisualBoard(Board):
    def __init__(self, game: Game, width: int, height: int):
        super().__init__(width, height)
        self.game = game

        self.assets = {
            WHITE: {
                ROOK: pygame.transform.scale(game.assets[WHITE][ROOK], (SQUARE_SIZE, SQUARE_SIZE)),
                KING: pygame.transform.scale(game.assets[WHITE][KING], (SQUARE_SIZE, SQUARE_SIZE))
            },
            BLACK: {
                ROOK: pygame.transform.scale(game.assets[BLACK][ROOK], (SQUARE_SIZE, SQUARE_SIZE)),
            },
            "castle_tile": pygame.transform.scale(game.assets["castle_tile"], (SQUARE_SIZE, SQUARE_SIZE)),
        }
        self.scroll = 0

    def adjust_scroll_to_bottom(self):
        spacing = len(self.list_of_moves) * 24 - self.game.screen.get_height() // 2
        if spacing > 0:
            self.scroll = -spacing

    def move_piece(self, piece: Piece, row: int, col: int) -> bool:
        move_result = super().move_piece(piece, row, col)
        if move_result:
            self.adjust_scroll_to_bottom()
            self.game.sounds["move"].play()
        return move_result
    
    def check_winner(self):
        super().check_winner()
        if self.winner is not None:
            self.game.sounds["end"].play()
    
    def undo_move(self) -> None:
        super().undo_move()
        self.adjust_scroll_to_bottom()
        self.game.sounds["move"].play()

    def render(self) -> None:
        light_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        light_tile.fill(LIGHT_TILE)
        dark_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        dark_tile.fill(DARK_TILE)

        board_display = self.game.board_display

        for row in range(self.height):
            for col in range(self.width):
                if (row + col) % 2 == 0:
                    board_display.blit(light_tile, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                else:
                    board_display.blit(dark_tile, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                if (row, col) in self.CASTLE_POSITIONS:
                    board_display.blit(self.assets["castle_tile"], (col * SQUARE_SIZE, row * SQUARE_SIZE))

        for row in range(self.height):
            for col in range(self.width):
                if self.board[row * self.width + col] is not None:
                    self.board[row * self.width + col].render(board_display)

        if self.selected_piece is not None:
            pygame.draw.rect(board_display, (0, 255, 0), (self.selected_piece.col * SQUARE_SIZE, self.selected_piece.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)
            for tile in self.selected_piece.legal_moves():
                pygame.draw.rect(board_display, (255, 0, 0), (tile[1] * SQUARE_SIZE, tile[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)

        if self.winner is not None:
            text = "Blue wins" if self.winner == BLACK else "Red wins"
            self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, self.game.screen.get_height() // 2, self.game.font_big)
        else:
            text = "Turn: " + (self.player1 if self.turn == BLACK else self.player2)
            self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, self.game.screen.get_height() // 2 - 56, self.game.font_small)
            
            text = "Moves:"
            self.game.draw_text(self.game.screen, text, (255, 255, 255), self.game.screen.get_width() - SIDE_PANEL // 2, self.game.screen.get_height() // 2 - 24, self.game.font_small)
            surface = pygame.Surface((SIDE_PANEL, self.game.screen.get_height() // 2))
            surface.fill((30, 30, 30))
            for i, move in enumerate(self.list_of_moves):
                text = f"{i // 2 + 1}. {move}," if i % 2 == 0 else f"{move}"
                spacing = 8 + i * 24
                self.game.draw_text(surface, text, (255, 255, 255), SIDE_PANEL // 2, spacing + self.scroll, self.game.font_small)
            self.game.screen.blit(surface, (self.game.screen.get_width() - SIDE_PANEL, self.game.screen.get_height() // 2))

    def __str__(self):
        return super().__str__()
    
    def __repr__(self):
        return super().__repr__()

