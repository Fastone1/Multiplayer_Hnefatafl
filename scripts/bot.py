from scripts.board import Board
from scripts.move import Move
from scripts.constants import KING, ROOK, BLACK, WHITE, DEBUG

import time
import random
from functools import lru_cache
from typing import Literal

INF = float('inf')
MAX_DEPTH = 10
MAX_TIME_PER_MOVE = 5
MATE_SCORE = 10_000

VALUES = {
    WHITE: 180,
    BLACK: 100
}

PST = {
    WHITE: {
        ROOK: [
            [0, 50, 50, 50, 50, 50, 50, 50, 0],
            [50, 40, 20, 20, 20, 20, 20, 40, 50],
            [50, 20, 10, 10, 10, 10, 10, 20, 50],
            [50, 20, 0, 0, 0, 0, 0, 20, 50],
            [50, 20, 0, 0, 0, 0, 0, 20, 50],
            [50, 20, 0, 0, 0, 0, 0, 20, 50],
            [50, 20, 10, 10, 10, 10, 10, 20, 50],
            [50, 40, 20, 20, 20, 20, 20, 40, 50],
            [0, 50, 50, 50, 50, 50, 50, 50, 0]
        ],
        KING: [
            [MATE_SCORE, 1000, 200, 200, 200, 200, 200, 1000, MATE_SCORE],
            [1000, 50, 0, 0, 0, 0, 0, 50, 1000],
            [200, 0, 0, 0, 0, 0, 0, 0, 200],
            [200, 0, 0, 0, 0, 0, 0, 0, 200],
            [200, 0, 0, 0, 0, 0, 0, 0, 200],
            [200, 0, 0, 0, 0, 0, 0, 0, 200],
            [200, 0, 0, 0, 0, 0, 0, 0, 200],
            [1000, 50, 0, 0, 0, 0, 0, 50, 1000],
            [MATE_SCORE, 1000, 200, 200, 200, 200, 200, 1000, MATE_SCORE]
        ]
    },
    BLACK: {
        ROOK: [
            [0, 0, 40, 0, 0, 0, 40, 0, 0],
            [0, 40, 10, 10, 10, 10, 10, 40, 0],
            [40, 10, 20, 20, 20, 20, 20, 10, 40],
            [0, 10, 20, 30, 30, 30, 20, 10, 0],
            [0, 10, 20, 30, 0, 30, 20, 10, 0],
            [0, 10, 20, 30, 30, 30, 20, 10, 0],
            [40, 10, 20, 20, 20, 20, 20, 10, 40],
            [0, 40, 10, 10, 10, 10, 10, 40, 0],
            [0, 0, 40, 0, 0, 0, 40, 0, 0]
        ]
    }
}

def generate_moves(board: Board) -> list[Move]:
    moves = []
    for piece in board.board:
        if piece is None or piece.color != board.turn:
            continue
        piece_moves = [Move(piece.row, piece.col, row, col) for row, col in piece.legal_moves()]
        moves.extend(piece_moves)
    return moves

def generate_interesting_moves(board: Board) -> list[Move]:
    '''
    Generate all the interesting moves for the current player.
    An interesting move is a move that captures an enemy piece or puts the king on the edge of the board.
    
    Parameters:
        board (Board): The current board.

    Returns:
        list[Move]: A list of all the interesting moves for the current player.
    '''
    moves = []
    for piece in board.board:
        if piece is None or piece.color != board.turn:
            continue
        for row, col in piece.legal_moves():
            move = Move(piece.row, piece.col, row, col)
            if board.move_is_capture(move):
                moves.append(move)
            elif piece.type == KING and board.move_is_to_edge(move):
                moves.append(move)
    return moves


class Bot():
    def __init__(self, size: int, color: int) -> None:
        self.board = Board(size, size)
        self.color = color

        self.transposition_table = {}

        self.numpos = 0
        self.start_time = 0
        self.cur_max_depth = 0
    
    def order_moves(self, moves: list[Move]) -> list[Move]:
        capture_moves = []
        non_capture_moves = []
        king_on_edge_moves = []
        for move in moves:
            if self.board.move_is_capture(move):
                capture_moves.append(move)
            elif self.board.move_is_to_edge(move):
                king_on_edge_moves.append(move)
            else:
                non_capture_moves.append(move)
        return king_on_edge_moves + capture_moves + non_capture_moves
    
    def distance_to_center(self, row: int, col: int) -> int:
        return abs(row - self.board.height // 2) + abs(col - self.board.width // 2)
    
    def are_there_adj_enemies(self, row: int, col: int) -> bool:
        for square in self.board.adjacent_squares(row, col):
            piece = self.board.get_piece(*square)
            if piece is not None and piece.color != self.board.turn:
                return True
        return False
    
    def evaluate(self) -> int:
        self.numpos += 1
        score = 0
        for piece in self.board.board:
            if piece is None:
                continue

            multiplier = 1 if piece.color == self.board.turn else -1
            score += VALUES[piece.color] * multiplier
            # score += PST[piece.color][piece.type][piece.row][piece.col] * multiplier

            if piece.type == KING:
                # add distance to center to encourage king to move to the corners
                score += PST[piece.color][KING][piece.row][piece.col] * multiplier

                # add king moves to encourage king to move
                king_moves = len(piece.legal_moves())
                score += king_moves * 20 * multiplier

                # add king access to edge to encourage defending team to restrict king's movement to the edge
                

        return score
    
    def quiesce(self, alpha: int, beta: int, q_depth: int = 3) -> int:
        if self.board.winner is not None:
            mate_score = MATE_SCORE - (self.cur_max_depth + q_depth)
            return mate_score if self.board.winner == self.board.turn else -mate_score
        
        stand_pat = self.evaluate()

        if q_depth == 0:
            return stand_pat

        best_score = stand_pat
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
        
        legal_moves = generate_interesting_moves(self.board)
        for move in legal_moves:
            self.board.move_piece_by_move(move)
            score = -self.quiesce(-beta, -alpha, q_depth - 1)
            self.board.undo_move()

            if score >= beta:
                return score
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
        return best_score
    
    def store_transposition(self, depth: int, value: int, node_type: Literal["exact", "lower_bound", "upper_bound"]) -> None:
        if self.is_mate_score(value):
            sign = 1 if value > 0 else -1
            value = value + ((self.cur_max_depth - depth) * sign)
        self.transposition_table[hash(self.board)] = {'depth': depth, 'value': value, 'type': node_type}
    
    def is_mate_score(self, score: int) -> bool:
        return abs(score) >= MATE_SCORE - 100
    
    def ply_to_mate_score(self, score: int) -> int:
        return MATE_SCORE - abs(score)
    
    def correct_mate_score(self, score: int, ply: int) -> int:
        if self.is_mate_score(score):
            sign = 1 if score > 0 else -1
            score = score - (ply * sign)
        return score

    def negamax(self, depth: int, alpha: int, beta: int) -> int:
        if time.time() - self.start_time > MAX_TIME_PER_MOVE:
            return None
        
        alpha_orig = alpha

        if self.board.winner is not None:
            mate_score = MATE_SCORE - (self.cur_max_depth - depth)
            return mate_score if self.board.winner == self.board.turn else -mate_score
        
        transposition_entry = self.transposition_table.get(hash(self.board), None)
        if transposition_entry is not None and transposition_entry['depth'] >= depth:
            corrected_value = self.correct_mate_score(transposition_entry['value'], self.cur_max_depth - depth)
            if transposition_entry['type'] == "exact":
                return corrected_value
            if transposition_entry['type'] == "lower_bound":
                alpha = max(alpha, corrected_value)
            if transposition_entry['type'] == "upper_bound":
                beta = min(beta, corrected_value)

            if alpha >= beta:
                return corrected_value
        
        if depth == 0:
            return self.quiesce(alpha, beta)
        
        legal_moves = generate_moves(self.board)
        legal_moves = self.order_moves(legal_moves)
        
        best_move_value = -INF
        for move in legal_moves:
            self.board.move_piece_by_move(move)
            eval = self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            if eval is None:    # time limit reached
                return None
            eval = -eval

            best_move_value = max(best_move_value, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break

        node_type = "exact"
        if best_move_value <= alpha_orig:
            node_type = "upper_bound"
        elif best_move_value >= beta:
            node_type = "lower_bound"
        self.store_transposition(depth, best_move_value, node_type)
        
        return best_move_value

    def root_move(self, depth: int, ex_best_move: Move) -> tuple[int, Move]:
        best_eval = -INF
        best_move = None
        alpha = -INF
        beta = INF

        legal_moves = generate_moves(self.board)
        legal_moves = self.order_moves(legal_moves)
        if ex_best_move is not None:
            legal_moves.remove(ex_best_move)
            legal_moves.insert(0, ex_best_move)
    
        for move in legal_moves:
            self.board.move_piece_by_move(move)
            eval = self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            if eval is None:    # time limit reached
                return best_eval, best_move
            eval = -eval

            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if alpha >= beta:
                break

        return best_eval, best_move
    
    def get_move(self) -> Move:
        if self.board.list_of_moves == []:
            legal_moves = generate_moves(self.board)
            return random.choice(legal_moves)

        self.start_time = time.time()
        best_move = None
        self.numpos = 0
        for cur_depth in range(1, MAX_DEPTH + 1):
            self.cur_max_depth = cur_depth
            if time.time() - self.start_time > MAX_TIME_PER_MOVE:
                break
            eval, move = self.root_move(cur_depth, best_move)

            if DEBUG:
                print(f"Depth: {cur_depth}, Eval: {eval}, Move: {move}, Numpos: {self.numpos}")
            if move is not None:
                best_eval, best_move = eval, move
            else:
                break

            if self.is_mate_score(best_eval):
                break

        return best_move
