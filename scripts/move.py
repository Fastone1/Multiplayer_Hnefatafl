from scripts.pieces import Piece

class Move:
    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.is_capture = False
        self.captured_pieces: list[Piece] = []

    def __str__(self):
        return f"Move to ({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Move to ({self.x}, {self.y}) with {len(self.captured_pieces)} captures"