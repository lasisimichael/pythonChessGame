from board import Board
from pieces import King, Queen, Rook, Bishop, Knight

class GameState:
    def __init__(self):
        self.board = Board()
        self.turn = 'w'
        self.move_history = []
        self.en_passant_target = None
        self.promotion_pending = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def get_pseudo_legal_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is None:
                    continue
                if piece.color != self.turn:
                    continue

                for (r, c) in piece.get_moves(self.board, self):
                    moves.append((piece, r, c))

                if isinstance(piece, King):
                    self._add_castling_moves(piece, moves)

        return moves

    def _add_castling_moves(self, king, moves):
        if king.has_moved:
            return

        row = king.row
        enemy = 'b' if king.color == 'w' else 'w'

        # King-side
        rook = self.board.grid[row][7]
        if rook and isinstance(rook, Rook) and rook.color == king.color and not rook.has_moved:
            if (self.board.grid[row][5] is None and
                self.board.grid[row][6] is None):
                if not self.is_square_attacked(row, 4, enemy) and \
                not self.is_square_attacked(row, 5, enemy) and \
                not self.is_square_attacked(row, 6, enemy):
                    moves.append((king, row, 6))

        # Queen-side
        rook = self.board.grid[row][0]
        if rook and isinstance(rook, Rook) and rook.color == king.color and not rook.has_moved:
            if (self.board.grid[row][1] is None and
                self.board.grid[row][2] is None and
                self.board.grid[row][3] is None):
                if not self.is_square_attacked(row, 4, enemy) and \
                not self.is_square_attacked(row, 3, enemy) and \
                not self.is_square_attacked(row, 2, enemy):
                    moves.append((king, row, 2))

    def make_move(self, piece, to_row, to_col):
        from_row, from_col = piece.row, piece.col

        old_ep = self.en_passant_target

        # Detect two-square pawn move to create en-passant target
        if piece.__class__.__name__ == "Pawn":
            if abs(to_row - from_row) == 2:
                self.en_passant_target = ((from_row + to_row) // 2, from_col)
            # En passant capture
            if (to_row, to_col) == old_ep:
                captured_row = from_row
                captured_col = to_col
                self.board.grid[captured_row][captured_col] = None

        # Detect castling
        if piece.__class__.__name__ == "King":
            if abs(to_col - from_col) == 2:  # castling attempt
                self.castle_rook(piece, to_col)

        # Move the piece normally
        self.board.move_piece(piece, to_row, to_col)

        # Promotion check
        if piece.__class__.__name__ == "Pawn":
            if (piece.color == 'w' and to_row == 0) or \
            (piece.color == 'b' and to_row == 7):
                self.promotion_pending = (piece, to_row, to_col)
                return

        # Update turn
        self.turn = 'b' if self.turn == 'w' else 'w'
        if self.turn == 'w':
            self.fullmove_number += 1

        if piece.__class__.__name__ != "Pawn" or abs(to_row - from_row) != 2:
            self.en_passant_target = None

    def castle_rook(self, king, king_target_col):
        row = king.row

        if king_target_col == 6:  # king-side castle
            rook_from = 7
            rook_to = 5
        else:                    # queen-side castle
            rook_from = 0
            rook_to = 3

        rook = self.board.grid[row][rook_from]
        if rook:
            self.board.move_piece(rook, row, rook_to)

    def promote_pawn(self, pawn, piece_type):
        row, col = pawn.row, pawn.col
        color = pawn.color

        self.board.grid[row][col] = None

        if piece_type == 'q':
            new_piece = Queen(color, row, col)
        elif piece_type == 'r':
            new_piece = Rook(color, row, col)
        elif piece_type == 'b':
            new_piece = Bishop(color, row, col)
        else:
            new_piece = Knight(color, row, col)

        self.board.grid[row][col] = new_piece
        self.promotion_pending = None

        # NOW switch turn
        self.turn = 'b' if self.turn == 'w' else 'w'

    def get_legal_moves(self):
        """
        Filter pseudo-legal moves by removing:
        - moves that leave king in check
        - illegal castling
        - illegal en-passant (if king would be exposed)
        """
        legal_moves = []

        for (piece, r, c) in self.get_pseudo_legal_moves():
            if self.is_legal(piece, r, c):
                legal_moves.append((piece, r, c))

        return legal_moves

    def is_legal(self, piece, to_row, to_col):
        """
        Make the move on a temporary board and check:
        - does own king remain safe?
        """
        
        # Save state
        from_row, from_col = piece.row, piece.col
        captured = self.board.grid[to_row][to_col]

        ep_captured = None

        # Simulate en passant capture
        if piece.__class__.__name__ == "Pawn":
            if (to_row, to_col) == self.en_passant_target:
                ep_row = from_row
                ep_col = to_col
                ep_captured = self.board.grid[ep_row][ep_col]
                self.board.grid[ep_row][ep_col] = None

        is_castling = (
            piece.__class__.__name__ == "King" and
            abs(to_col - from_col) == 2
        )

        # Save rook state if castling
        rook = None
        rook_from = rook_to = None

        if is_castling:
            row = from_row
            if to_col == 6:  # king-side
                rook_from, rook_to = 7, 5
            else:            # queen-side
                rook_from, rook_to = 0, 3

            rook = self.board.grid[row][rook_from]
            self.board.grid[row][rook_from] = None
            self.board.grid[row][rook_to] = rook
            rook.col = rook_to


        # Make move
        self.board.grid[from_row][from_col] = None
        self.board.grid[to_row][to_col] = piece
        piece.row, piece.col = to_row, to_col

        # Check if in check
        in_check = self.is_in_check(piece.color)

        # Undo move
        self.board.grid[from_row][from_col] = piece
        self.board.grid[to_row][to_col] = captured
        piece.row, piece.col = from_row, from_col

        # Undo en passant
        if ep_captured:
            self.board.grid[ep_row][ep_col] = ep_captured

        # Undo castling
        if is_castling:
            self.board.grid[row][rook_to] = None
            self.board.grid[row][rook_from] = rook
            rook.col = rook_from

        return not in_check

    def is_square_attacked(self, row, col, by_color):
        """
        Returns True if the square (row,col) is attacked by `by_color`.
        """
        board = self.board.grid

        # ---------- Pawn attacks ----------
        dr = 1 if by_color == 'w' else -1
        for dc in (-1, 1):
            r = row + dr
            c = col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                attacker = board[r][c]
                if attacker and attacker.color == by_color and attacker.__class__.__name__ == "Pawn":
                    return True

        
        # ---------- Knight attacks ----------
        knight_moves = [(-2, 1), (-1, 2), (1, 2), (2, 1),
                        (-2, -1), (-1, -2), (1, -2), (2, -1)]
        
        for dr, dc in knight_moves:
            r = row + dr
            c = col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                attacker = board[r][c]
                if attacker is not None and attacker.color == by_color:
                    if attacker.__class__.__name__ == "Knight":
                        return True
        
        # ---------- King attacks ----------
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue

                r = row + dr
                c = col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    attacker = board[r][c]
                    if attacker is not None and attacker.color == by_color:
                        if attacker.__class__.__name__ == "King":
                            return True

        # ---------- Sliding pieces ----------
        # Diagonals (Bishop / Queen)
        diag_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diag_dirs:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                attacker = board[r][c]
                if attacker is not None:
                    if attacker.color == by_color and attacker.__class__.__name__ in ("Bishop","Queen"):
                        return True
                    break
                r += dr
                c += dc

        # Straight (Rook / Queen)
        straight_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in straight_dirs:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                attacker = board[r][c]
                if attacker is not None:
                    if attacker.color == by_color and attacker.__class__.__name__ in ("Rook","Queen"):
                        return True
                    break
                r += dr
                c += dc

        return False

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board.grid[r][c]
                if piece and piece.color == color and piece.__class__.__name__ == "King":
                    return (r, c)
        return None

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if king_pos is None:
            return False  # should never happen, but keeps things safe

        enemy = 'b' if color == 'w' else 'w'
        return self.is_square_attacked(king_pos[0], king_pos[1], enemy)

    def current_player_in_check(self):
        return self.is_in_check(self.turn)

    def is_checkmate(self, color):
        # Condition 1: king must be in check
        if not self.is_in_check(color):
            return False

        # Condition 2: no legal moves available
        current_turn = self.turn
        self.turn = color  # temporarily set turn

        legal_moves = self.get_legal_moves()

        self.turn = current_turn  # restore turn

        return len(legal_moves) == 0

    def is_stalemate(self, color):
        # Not in check
        if self.is_in_check(color):
            return False

        current_turn = self.turn
        self.turn = color

        legal_moves = self.get_legal_moves()

        self.turn = current_turn

        return len(legal_moves) == 0

    def undo_move(self):
        """
        Undo the last move.
        """
        pass
