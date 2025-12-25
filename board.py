from pieces import *

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_starting_position()

    def setup_starting_position(self):
        layout = [
            ['br','bn','bb','bq','bk','bb','bn','br'],
            ['bp'] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ['wp'] * 8,
            ['wr','wn','wb','wq','wk','wb','wn','wr']
        ]

        for r in range(8):
            for c in range(8):
                cell = layout[r][c]
                if cell is None:
                    continue

                color = cell[0]
                piece_type = cell[1]

                if piece_type == 'k':
                    piece = King(color, r, c)
                elif piece_type == 'q':
                    piece = Queen(color, r, c)
                elif piece_type == 'r':
                    piece = Rook(color, r, c)
                elif piece_type == 'b':
                    piece = Bishop(color, r, c)
                elif piece_type == 'n':
                    piece = Knight(color, r, c)
                elif piece_type == 'p':
                    piece = Pawn(color, r, c)

                self.place_piece(piece)

    def place_piece(self, piece):
        self.grid[piece.row][piece.col] = piece

    def move_piece(self, piece, to_row, to_col):
        self.grid[piece.row][piece.col] = None
        self.grid[to_row][to_col] = piece
        piece.move_to(to_row, to_col)
        piece.has_moved = True