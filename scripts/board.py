from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame

from scripts.constants import BACKGROUND, SQUARE_SIZE, WHITE, BLACK, ROOK, KING, DARK_TILE, LIGHT_TILE, SIDE_PANEL, DEBUG
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

RANDOM_ARRAY = [
    0x9D39247E33776D41, 0x2AF7398005AAA5C7, 0x44DB015024623547, 0x9C15F73E62A76AE2,
    0x75834465489C0C89, 0x3290AC3A203001BF, 0x0FBBAD1F61042279, 0xE83A908FF2FB60CA,
    0x0D7E765D58755C10, 0x1A083822CEAFE02D, 0x9605D5F0E25EC3B0, 0xD021FF5CD13A2ED5,
    0x40BDF15D4A672E32, 0x011355146FD56395, 0x5DB4832046F3D9E5, 0x239F8B2D7FF719CC,
    0x05D1A1AE85B49AA1, 0x679F848F6E8FC971, 0x7449BBFF801FED0B, 0x7D11CDB1C3B7ADF0,
    0x82C7709E781EB7CC, 0xF3218F1C9510786C, 0x331478F3AF51BBE6, 0x4BB38DE5E7219443,
    0xAA649C6EBCFD50FC, 0x8DBD98A352AFD40B, 0x87D2074B81D79217, 0x19F3C751D3E92AE1,
    0xB4AB30F062B19ABF, 0x7B0500AC42047AC4, 0xC9452CA81A09D85D, 0x24AA6C514DA27500,
    0x4C9F34427501B447, 0x14A68FD73C910841, 0xA71B9B83461CBD93, 0x03488B95B0F1850F,
    0x637B2B34FF93C040, 0x09D1BC9A3DD90A94, 0x3575668334A1DD3B, 0x735E2B97A4C45A23,
    0x18727070F1BD400B, 0x1FCBACD259BF02E7, 0xD310A7C2CE9B6555, 0xBF983FE0FE5D8244,
    0x9F74D14F7454A824, 0x51EBDC4AB9BA3035, 0x5C82C505DB9AB0FA, 0xFCF7FE8A3430B241,
    0x3253A729B9BA3DDE, 0x8C74C368081B3075, 0xB9BC6C87167C33E7, 0x7EF48F2B83024E20,
    0x11D505D4C351BD7F, 0x6568FCA92C76A243, 0x4DE0B0F40F32A7B8, 0x96D693460CC37E5D,
    0x42E240CB63689F2F, 0x6D2BDCDAE2919661, 0x42880B0236E4D951, 0x5F0F4A5898171BB6,
    0x39F890F579F92F88, 0x93C5B5F47356388B, 0x63DC359D8D231B78, 0xEC16CA8AEA98AD76,
    0x5355F900C2A82DC7, 0x07FB9F855A997142, 0x5093417AA8A7ED5E, 0x7BCBC38DA25A7F3C,
    0x19FC8A768CF4B6D4, 0x637A7780DECFC0D9, 0x8249A47AEE0E41F7, 0x79AD695501E7D1E8,
    0x14ACBAF4777D5776, 0xF145B6BECCDEA195, 0xDABF2AC8201752FC, 0x24C3C94DF9C8D3F6,
    0xBB6E2924F03912EA, 0x0CE26C0B95C980D9, 0xA49CD132BFBF7CC4, 0xE99D662AF4243939,
    0x27E6AD7891165C3F, 0x8535F040B9744FF1, 0x54B3F4FA5F40D873, 0x72B12C32127FED2B,
    0xEE954D3C7B411F47, 0x9A85AC909A24EAA1, 0x70AC4CD9F04F21F5, 0xF9B89D3E99A075C2,
    0x87B3E2B2B5C907B1, 0xA366E5B8C54F48B8, 0xAE4A9346CC3F7CF2, 0x1920C04D47267BBD,
    0x87BF02C6B49E2AE9, 0x092237AC237F3859, 0xFF07F64EF8ED14D0, 0x8DE8DCA9F03CC54E,
    0x9C1633264DB49C89, 0xB3F22C3D0B0B38ED, 0x390E5FB44D01144B, 0x5BFEA5B4712768E9,
    0x1E1032911FA78984, 0x9A74ACB964E78CB3, 0x4F80F7A035DAFB04, 0x6304D09A0B3738C4,
    0x2171E64683023A08, 0x5B9B63EB9CEFF80C, 0x506AACF489889342, 0x1881AFC9A3A701D6,
    0x6503080440750644, 0xDFD395339CDBF4A7, 0xEF927DBCF00C20F2, 0x7B32F7D1E03680EC,
    0xB9FD7620E7316243, 0x05A7E8A57DB91B77, 0xB5889C6E15630A75, 0x4A750A09CE9573F7,
    0xCF464CEC899A2F8A, 0xF538639CE705B824, 0x3C79A0FF5580EF7F, 0xEDE6C87F8477609D,
    0x799E81F05BC93F31, 0x86536B8CF3428A8C, 0x97D7374C60087B73, 0xA246637CFF328532,
    0x043FCAE60CC0EBA0, 0x920E449535DD359E, 0x70EB093B15B290CC, 0x73A1921916591CBD,
    0x56436C9FE1A1AA8D, 0xEFAC4B70633B8F81, 0xBB215798D45DF7AF, 0x45F20042F24F1768,
    0x930F80F4E8EB7462, 0xFF6712FFCFD75EA1, 0xAE623FD67468AA70, 0xDD2C5BC84BC8D8FC,
    0x7EED120D54CF2DD9, 0x22FE545401165F1C, 0xC91800E98FB99929, 0x808BD68E6AC10365,
    0xDEC468145B7605F6, 0x1BEDE3A3AEF53302, 0x43539603D6C55602, 0xAA969B5C691CCB7A,
    0xA87832D392EFEE56, 0x65942C7B3C7E11AE, 0xDED2D633CAD004F6, 0x21F08570F420E565,
    0xB415938D7DA94E3C, 0x91B859E59ECB6350, 0x10CFF333E0ED804A, 0x28AED140BE0BB7DD,
    0xC5CC1D89724FA456, 0x5648F680F11A2741, 0x2D255069F0B7DAB3, 0x9BC5A38EF729ABD4,
    0xEF2F054308F6A2BC, 0xAF2042F5CC5C2858, 0x480412BAB7F5BE2A, 0xAEF3AF4A563DFE43,
    0x19AFE59AE451497F, 0x52593803DFF1E840, 0xF4F076E65F2CE6F0, 0x11379625747D5AF3,
    0xBCE5D2248682C115, 0x9DA4243DE836994F, 0x066F70B33FE09017, 0x4DC4DE189B671A1C,
    0x51039AB7712457C3, 0xC07A3F80C31FB4B4, 0xB46EE9C5E64A6E7C, 0xB3819A42ABE61C87,
    0x21A007933A522A20, 0x2DF16F761598AA4F, 0x763C4A1371B368FD, 0xF793C46702E086A0,
    0xD7288E012AEB8D31, 0xDE336A2A4BC1C44B, 0x0BF692B38D079F23, 0x2C604A7A177326B3,
    0x4850E73E03EB6064, 0xCFC447F1E53C8E1B, 0xB05CA3F564268D99, 0x9AE182C8BC9474E8,
    0xA4FC4BD4FC5558CA, 0xE755178D58FC4E76, 0x69B97DB1A4C03DFE, 0xF9B5B7C4ACC67C96,
    0xFC6A82D64B8655FB, 0x9C684CB6C4D24417, 0x8EC97D2917456ED0, 0x6703DF9D2924E97E,
    0xC547F57E42A7444E, 0x78E37644E7CAD29E, 0xFE9A44E9362F05FA, 0x08BD35CC38336615,
    0x9315E5EB3A129ACE, 0x94061B871E04DF75, 0xDF1D9F9D784BA010, 0x3BBA57B68871B59D,
    0xD2B7ADEEDED1F73F, 0xF7A255D83BC373F8, 0xD7F4F2448C0CEB81, 0xD95BE88CD210FFA7,
    0x336F52F8FF4728E7, 0xA74049DAC312AC71, 0xA2F61BB6E437FDB5, 0x4F2A5CB07F6A35B3,
    0x87D380BDA5BF7859, 0x16B9F7E06C453A21, 0x7BA2484C8A0FD54E, 0xF3A678CAD9A2E38C,
    0x39B0BF7DDE437BA2, 0xFCAF55C1BF8A4424, 0x18FCF680573FA594, 0x4C0563B89F495AC3,
    0x40E087931A00930D, 0x8CFFA9412EB642C1, 0x68CA39053261169F, 0x7A1EE967D27579E2,
    0x9D1D60E5076F5B6F, 0x3810E399B6F65BA2, 0x32095B6D4AB5F9B1, 0x35CAB62109DD038A,
    0xA90B24499FCFAFB1, 0x77A225A07CC2C6BD, 0x513E5E634C70E331, 0x4361C0CA3F692F12,
    0xD941ACA44B20A45B, 0x528F7C8602C5807B, 0x52AB92BEB9613989, 0x9D1DFA2EFC557F73,
    0x722FF175F572C348, 0x1D1260A51107FE97, 0x7A249A57EC0C9BA2, 0x04208FE9E8F7F2D6,
    0x5A110C6058B920A0, 0x0CD9A497658A5698, 0x56FD23C8F9715A4C, 0x284C847B9D887AAE,
    0x04FEABFBBDB619CB, 0x742E1E651C60BA83, 0x9A9632E65904AD3C, 0x881B82A13B51B9E2,
]

def zobrist_hash(board: Board) -> int:
    h = 0
    if board.turn == BLACK:
        h ^= RANDOM_ARRAY[-1]
    for row in range(board.height):
        for col in range(board.width):
            piece = board.get_piece(row, col)
            if piece is not None:
                piece_value = piece.color * 2 + (piece.type - 2)
                h ^= RANDOM_ARRAY[row * board.width + col + piece_value]
    return h

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
        self.list_of_moves.append(Move(piece.row, piece.col, row, col, self.height))
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
        if (from_row == to_row and from_col == to_col) or (from_row != to_row and from_col != to_col):
            return False
        
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
    
    def is_to_edge(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        if (from_row != to_row and from_col != to_col) or (from_row == to_row and from_col == to_col):
            return False
        
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return False
        
        if piece.color != self.turn:
            return False
        
        if (to_row not in [0, self.height - 1]) and (to_col not in [0, self.width - 1]):
            return False
        
        return True
    
    def move_is_to_edge(self, move: Move) -> bool:
        return self.is_to_edge(move.from_row, move.from_col, move.to_row, move.to_col)
    
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
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return zobrist_hash(self)


class VisualBoard(Board):
    def __init__(self, game: Game, width: int, height: int):
        super().__init__(width, height)
        self.game = game

        light_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        light_tile.fill(LIGHT_TILE)
        dark_tile = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        dark_tile.fill(DARK_TILE)
        self.assets = {
            WHITE: {
                ROOK: pygame.transform.scale(game.assets[WHITE][ROOK], (SQUARE_SIZE, SQUARE_SIZE)),
                KING: pygame.transform.scale(game.assets[WHITE][KING], (SQUARE_SIZE, SQUARE_SIZE))
            },
            BLACK: {
                ROOK: pygame.transform.scale(game.assets[BLACK][ROOK], (SQUARE_SIZE, SQUARE_SIZE)),
            },
            "castle_tile": pygame.transform.scale(game.assets["castle_tile"], (SQUARE_SIZE, SQUARE_SIZE)),
            "light_tile": light_tile,
            "dark_tile": dark_tile,
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
        board_display = self.game.board_display

        for row in range(self.height):
            for col in range(self.width):
                if (row + col) % 2 == 0:
                    board_display.blit(self.assets["light_tile"], (col * SQUARE_SIZE, row * SQUARE_SIZE))
                else:
                    board_display.blit(self.assets["dark_tile"], (col * SQUARE_SIZE, row * SQUARE_SIZE))
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
            surface.fill(BACKGROUND)
            for i, move in enumerate(self.list_of_moves):
                text = f"{i // 2 + 1}. {move}," if i % 2 == 0 else f"{move}"
                spacing = 8 + i * 24
                self.game.draw_text(surface, text, (255, 255, 255), SIDE_PANEL // 2, spacing + self.scroll, self.game.font_small)
            self.game.screen.blit(surface, (self.game.screen.get_width() - SIDE_PANEL, self.game.screen.get_height() // 2))

    def __str__(self):
        return super().__str__()
    
    def __repr__(self):
        return super().__repr__()

