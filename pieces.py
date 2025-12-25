# Base class for chess pieces
class ChessPiece:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False

    def get_moves(self, board, game_state=None):
        raise NotImplementedError

    def move_to(self, row, col):
        self.row = row
        self.col = col
        self.has_moved = True

class King(ChessPiece):
    symbol = 'k'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col = self.row, self.col

        # 8 surrounding squares
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == dc == 0:
                    continue

                new_row = row + dr
                new_col = col + dc

                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    continue
                
                target = board.grid[new_row][new_col]


                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))

        return moves

class Queen(ChessPiece):
    symbol = 'q'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col = self.row, self.col

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                      (-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]

                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break 

                r += dr
                c += dc

        return moves

class Rook(ChessPiece):
    symbol = 'r'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col = self.row, self.col

        directions = [
            (-1, 0),  # up
            (1, 0),   # down
            (0, -1),  # left
            (0, 1),   # right
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]

                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break 

                r += dr
                c += dc

        return moves

class Bishop(ChessPiece):
    symbol = 'b'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col = self.row, self.col

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]

                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break 

                r += dr
                c += dc

        return moves

class Knight(ChessPiece):
    symbol = 'n'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col = self.row, self.col

        directions = [
            (-2, -1), (-2, +1),
            (-1, -2), (-1, +2),
            (+1, -2), (+1, +2),
            (+2, -1), (+2, +1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc

            if not (0 <= r < 8 and 0 <= c < 8):
                continue
            
            target = board.grid[r][c]

            if target is None or target.color != self.color:
                moves.append((r, c))

        return moves

class Pawn(ChessPiece):
    symbol = 'p'

    def get_moves(self, board, game_state=None):
        moves = []
        row, col, color = self.row, self.col, self.color

        dr = -1 if color == 'w' else 1

        # One step forward
        r = row + dr
        if 0 <= r < 8:
            if board.grid[r][col] is None:
                moves.append((r, col))

        # Two steps forward
        if not self.has_moved:
            r2 = row + 2 * dr
            if 0 <= r2 < 8:
                if board.grid[row + dr][col] is None and board.grid[r2][col] is None:
                    moves.append((r2, col))

        # Capture move
        for dc in (-1, 1):
            r, c = row + dr, col + dc

            if not (0 <= r < 8 and 0 <= c < 8):
                continue
            
            target = board.grid[r][c]
            if target is not None and target.color != self.color:
                moves.append((r, c))

        # En-passant
        if game_state and game_state.en_passant_target:
            ep_row, ep_col = game_state.en_passant_target

            direction = -1 if self.color == 'w' else 1

            if self.row + direction == ep_row and abs(self.col - ep_col) == 1:
                moves.append((ep_row, ep_col))

        return moves
