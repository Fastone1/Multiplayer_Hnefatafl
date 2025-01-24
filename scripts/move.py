from scripts.pieces import Piece

class Move:
    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.is_capture = False
        self.captured_pieces: list[Piece] = []

    def __eq__(self, other: 'Move'):
        assert isinstance(other, Move)
        return self.from_row == other.from_row and self.from_col == other.from_col and self.to_row == other.to_row and self.to_col == other.to_col

    def __str__(self):
        return f"{chr(self.from_col + 97)}{-self.from_row + 9}-{chr(self.to_col + 97)}{-self.to_row + 9}{'x' + '/'.join([chr(piece.col + 97) + str(-piece.row + 9) for piece in self.captured_pieces]) if self.is_capture else ''}"
    
    def __repr__(self):
        return f"Move from ({self.from_row}, {self.from_col}) to ({self.to_row}, {self.to_col}) with captures: {self.captured_pieces}"
    
def parse_move(move: str) -> Move:
    move = move.lower()
    from_row = 9 - int(move[1])
    from_col = ord(move[0]) - 97
    to_row = 9 - int(move[3])
    to_col = ord(move[2]) - 97
    return Move(from_row, from_col, to_row, to_col)