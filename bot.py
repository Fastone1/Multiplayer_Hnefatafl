from scripts.board import Board
from scripts.move import Move, parse_move_9x9
from scripts.constants import KING, ROOK, BLACK, WHITE

import time
import random

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
            [MATE_SCORE, 200, 100, 50, 50, 50, 100, 200, MATE_SCORE],
            [200, 50, 0, 0, 0, 0, 0, 50, 200],
            [100, 0, 0, 0, 0, 0, 0, 0, 100],
            [50, 0, 0, 0, 0, 0, 0, 0, 50],
            [50, 0, 0, 0, 0, 0, 0, 0, 50],
            [50, 0, 0, 0, 0, 0, 0, 0, 50],
            [100, 0, 0, 0, 0, 0, 0, 0, 100],
            [200, 50, 0, 0, 0, 0, 0, 50, 200],
            [MATE_SCORE, 200, 100, 50, 50, 50, 100, 200, MATE_SCORE]
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

class Bot():
    def __init__(self, board: Board, color: int) -> None:
        self.board = board
        self.color = color

        self.numpos = 0
        self.start_time = 0
        self.cur_max_depth = 0

    def generate_moves(self) -> list[Move]:
        moves = []
        for piece in self.board.board:
            if piece is None or piece.color != self.board.turn:
                continue
            piece_moves = [Move(piece.row, piece.col, row, col) for row, col in piece.legal_moves()]
            moves.extend(piece_moves)
        return moves
    
    def generate_interesting_moves(self) -> list[Move]:
        '''
        Generate all the interesting moves for the current player.
        An interesting move is a move that captures an enemy piece or puts the king on the edge of the board.
        
        Returns:
            list[Move]: A list of all the interesting moves for the current player.
        '''
        moves = []
        for piece in self.board.board:
            if piece is None or piece.color != self.board.turn:
                continue
            for row, col in piece.legal_moves():
                move = Move(piece.row, piece.col, row, col)
                if self.board.move_is_capture(move):
                    moves.append(move)
                elif piece.type == KING and self.board.move_is_to_edge(move):
                    moves.append(move)
        return moves
    
    def order_moves(self, moves: list[Move]) -> list[Move]:
        capture_moves = [move for move in moves if move.is_capture]
        non_capture_moves = [move for move in moves if not move.is_capture]
        return capture_moves + non_capture_moves
    
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
                king_distance = self.distance_to_center(piece.row, piece.col)
                if king_distance == 7 and not self.are_there_adj_enemies(piece.row, piece.col):
                    return (MATE_SCORE - self.cur_max_depth) * multiplier
                score += king_distance * 50 * multiplier

                king_moves = len(piece.legal_moves())
                score += king_moves * 10 * multiplier

        return score
    
    def quiesce(self, alpha: int, beta: int, q_depth: int = 3) -> int:
        if self.board.winner is not None:
            mate_score = MATE_SCORE - (self.cur_max_depth + q_depth)
            print(f'Mate score: {mate_score}, at max depth: {self.cur_max_depth}, at q_depth: {q_depth}')
            return mate_score if self.board.winner == self.board.turn else -mate_score
        
        stand_pat = self.evaluate()

        if q_depth == 0:
            return stand_pat

        best_score = stand_pat
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
        
        legal_moves = self.generate_interesting_moves()
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
    
    def negamax(self, depth: int, alpha: int, beta: int) -> int:
        if time.time() - self.start_time > MAX_TIME_PER_MOVE:
            print('Time limit reached in negamax')
            return None
        
        alpha_orig = alpha

        if self.board.winner is not None:
            mate_score = MATE_SCORE - (self.cur_max_depth - depth)
            return mate_score if self.board.winner == self.board.turn else -mate_score
        
        if depth == 0:
            return self.quiesce(alpha, beta)
        
        legal_moves = self.generate_moves()
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
        
        return best_move_value

    def root_move(self, depth: int, ex_best_move: Move) -> tuple[int, Move]:
        best_eval = -INF
        best_move = None
        alpha = -INF
        beta = INF

        legal_moves = self.generate_moves()
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
            legal_moves = self.generate_moves()
            return random.choice(legal_moves)

        self.start_time = time.time()
        best_move = None
        self.numpos = 0
        for cur_depth in range(1, MAX_DEPTH + 1):
            self.cur_max_depth = cur_depth
            if time.time() - self.start_time > MAX_TIME_PER_MOVE:
                print('Time limit reached in get_move')
                break
            eval, move = self.root_move(cur_depth, best_move)

            if move is not None:
                best_eval, best_move = eval, move
                print(f'Depth reached:\t{cur_depth}')
                print(f'Partial eval:\t{best_eval}')
                print(f'Partial move:\t{best_move}')
            else:
                break

            if abs(best_eval) >= MATE_SCORE - cur_depth:
                break

        print(f'Best eval: {best_eval}')
        print(f'Best move: {best_move}')
        print(f'Number of positions: {self.numpos}')
        return best_move

if __name__ == '__main__':
    board = Board(9, 9)
    bot = Bot(board, WHITE)

    while board.winner is None:
        print(board)

        if board.turn == bot.color:
            move = bot.get_move()
            board.move_piece_by_move(move)
        else:
            moved = False
            while not moved:
                move = input('Enter move: ')
                try:
                    move = parse_move_9x9(move)
                except ValueError:
                    print('Invalid move format')
                    continue
                moved = board.move_piece_by_move(move)
                if not moved:
                    print('Invalid move')
        
    print(board)
    print('You win!' if board.winner != bot.color else 'AI will take over the world!')
