from matplotlib.pylab import record
from board import Board
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

class MoveRecord:
    def __init__(
        self,
        piece,
        from_row, from_col,
        to_row, to_col,
        captured,
        en_passant_target,
        was_castling=False,
        rook=None,
        rook_from=None,
        rook_to=None,
        ep_captured=None,
        piece_has_moved=False,
        was_promotion=False,
        promoted_piece=None
    ):
        self.piece = piece
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.captured = captured
        self.en_passant_target = en_passant_target
        self.was_castling = was_castling
        self.rook = rook
        self.rook_from = rook_from
        self.rook_to = rook_to
        self.ep_captured = ep_captured
        self.piece_has_moved = piece_has_moved
        self.fullmove_number = 0
        self.rook_has_moved = False
        self.was_promotion = was_promotion
        self.promoted_piece = promoted_piece
        self.turn = None

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

    def make_move(self, piece, to_row, to_col, simulate=False):
        from_row, from_col = piece.row, piece.col
        captured = self.board.grid[to_row][to_col]
        old_ep = self.en_passant_target
        piece_had_moved = piece.has_moved

        ep_captured = None
        # En passant capture
        if isinstance(piece, Pawn) and (to_row, to_col) == old_ep:
            captured_row = piece.row
            captured_col = to_col
            ep_captured = self.board.grid[captured_row][captured_col]
            self.board.grid[captured_row][captured_col] = None
        
        was_castling = False
        rook = rook_from = rook_to = None
        # Detect castling
        if piece.__class__.__name__ == "King":
            if abs(to_col - from_col) == 2:  # castling attempt
                was_castling = True
                row = from_row
                if to_col == 6:
                    rook_from, rook_to = 7, 5
                else:
                    rook_from, rook_to = 0, 3
                rook = self.board.grid[row][rook_from]
                self.castle_rook(piece, to_col)

        record = MoveRecord(
            piece, from_row, from_col, to_row, to_col,
            captured,
            old_ep,
            was_castling,
            rook, rook_from, rook_to,
            ep_captured,
            piece_had_moved
        )
        record.fullmove_number = self.fullmove_number
        record.rook_has_moved = rook.has_moved if rook else False
        record.turn = self.turn

        self.move_history.append(record)

        # Move the piece normally
        self.board.move_piece(piece, to_row, to_col)

        # Set en passant target if pawn double-steps
        if isinstance(piece, Pawn) and abs(to_row - from_row) == 2:
            ep_row = (from_row + to_row) // 2
            self.en_passant_target = (ep_row, to_col)
        else:
            self.en_passant_target = None

            
        # Promotion
        if isinstance(piece, Pawn) and (to_row == 0 or to_row == 7):
            record.was_promotion = True

            if not simulate:
                self.promotion_pending = (piece, to_row, to_col)
                return
            else:
                # DO NOTHING during simulation
                pass

        # Update turn
        if not simulate:
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

        last_move = self.move_history[-1]
        last_move.was_promotion = True
        last_move.promoted_piece = new_piece

        self.board.grid[row][col] = new_piece
        new_piece.has_moved = True
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
        
        self.make_move(piece, to_row, to_col, True)
        legal = not self.is_in_check(piece.color)
        self.undo_move()

        return legal

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
        if not self.move_history:
            return

        record = self.move_history.pop()
        self.fullmove_number = record.fullmove_number
        piece = record.piece

        # Restore en passant target
        self.en_passant_target = record.en_passant_target

        # Restore turn
        self.turn = record.turn

        # Move piece back
        self.board.grid[record.to_row][record.to_col] = None
        self.board.grid[record.from_row][record.from_col] = piece
        piece.row = record.from_row
        piece.col = record.from_col
        piece.has_moved = record.piece_has_moved

        # Restore captured piece
        if record.captured:
            self.board.grid[record.to_row][record.to_col] = record.captured

        # Restore en passant capture
        if record.ep_captured:
            ep_row = record.from_row
            ep_col = record.to_col
            self.board.grid[ep_row][ep_col] = record.ep_captured

        # Undo castling rook move
        if record.was_castling:
            row = record.from_row
            self.board.grid[row][record.rook_to] = None
            self.board.grid[row][record.rook_from] = record.rook
            record.rook.col = record.rook_from
            record.rook.has_moved = record.rook_has_moved

        if record.was_promotion:
            # Remove promoted piece ONLY if it exists
            if record.promoted_piece:
                self.board.grid[record.to_row][record.to_col] = None

            # Restore pawn
            self.board.grid[record.from_row][record.from_col] = record.piece
            record.piece.row = record.from_row
            record.piece.col = record.from_col

    def setup_promotion_test(self):
        self.board.grid = [[None for _ in range(8)] for _ in range(8)]

        # White pawn ready to promote
        pawn = Pawn('w', 1, 0)
        self.board.grid[1][0] = pawn

        # Kings (required for legality)
        wk = King('w', 7, 4)
        bk = King('b', 0, 4)
        self.board.grid[7][4] = wk
        self.board.grid[0][4] = bk

        self.turn = 'w'
        self.move_history.clear()
        self.en_passant_target = None

def perft(game, depth):
    if depth == 0:
        return 1

    nodes = 0
    moves = game.get_legal_moves()

    for piece, r, c in moves:
        game.make_move(piece, r, c, simulate=True)

        # Handle auto-promotion during simulation
        if game.move_history[-1].was_promotion:
            # Promote to queen only (standard perft rule)
            pawn = game.move_history[-1].piece
            row, col = pawn.row, pawn.col
            color = pawn.color
            game.board.grid[row][col] = Queen(color, row, col)

        nodes += perft(game, depth - 1)
        game.undo_move()

    return nodes

def perft_divide(game, depth):
    results = {}
    moves = game.get_legal_moves()

    for piece, r, c in moves:
        game.make_move(piece, r, c, simulate=True)

        if game.move_history[-1].was_promotion:
            pawn = game.move_history[-1].piece
            row, col = pawn.row, pawn.col
            color = pawn.color
            game.board.grid[row][col] = Queen(color, row, col)

        count = perft(game, depth - 1)
        game.undo_move()

        move_str = f"{piece.__class__.__name__[0]}{piece.col}{piece.row}->{c}{r}"
        results[move_str] = count

    return results
