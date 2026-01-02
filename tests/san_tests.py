from game import GameState
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

def run_test(name, setup_fn, move_fn, expected_san):
    game = GameState()
    setup_fn(game)
    move_fn(game)

    actual = game.san_history[-1] if game.san_history else None
    assert actual == expected_san, f"{name} FAILED: expected {expected_san}, got {actual}"
    print(f"✔ {name}")

def test_quiet_move():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][4] = Pawn('w',6,4)
        g.turn = 'w'

    def move(g):
        pawn = g.board.grid[6][4]
        g.make_move(pawn, 5, 4)

    run_test("Quiet pawn move", setup, move, "e3")

def test_capture():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][4] = Pawn('w',6,4)
        g.board.grid[5][3] = Pawn('b',5,3)
        g.turn = 'w'

    def move(g):
        pawn = g.board.grid[6][4]
        g.make_move(pawn, 5, 3)

    run_test("Pawn capture", setup, move, "exd3")

def test_check():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][0] = Rook('w',6,0)
        g.turn = 'w'

    def move(g):
        rook = g.board.grid[6][0]
        g.make_move(rook, 0, 0)

    run_test("Check", setup, move, "Ra8+")

def test_capture_check():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[4][4] = Queen('w',4,4)
        g.board.grid[2][4] = Rook('b',2,4)
        g.turn = 'w'

    def move(g):
        queen = g.board.grid[4][4]
        g.make_move(queen, 2, 4)

    run_test("Capture with check", setup, move, "Qxe6+")

def test_checkmate():
    def setup(g):
        g.board.clear()
        g.board.grid[0][0] = King('b',0,0)
        g.board.grid[2][1] = Queen('w',2,1)
        g.board.grid[2][0] = King('w',2,0)
        g.turn = 'w'

    def move(g):
        queen = g.board.grid[2][1]
        g.make_move(queen, 1, 1)

    run_test("Checkmate", setup, move, "Qb7#")

def test_file_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[4][7] = Knight('w',4,7)
        g.board.grid[4][5] = Knight('w',4,5)
        g.turn = 'w'

    def move(g):
        knight = g.board.grid[4][7]
        g.make_move(knight, 6, 6)

    run_test("File disambiguation", setup, move, "Nhg2")

def test_rank_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[7][6] = Knight('w',7,6)
        g.board.grid[5][6] = Knight('w',5,6)
        g.turn = 'w'

    def move(g):
        knight = g.board.grid[7][6]
        g.make_move(knight, 6, 4)

    run_test("Rank disambiguation", setup, move, "N1e2")

def test_full_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][1] = Knight('w',6,1)
        g.board.grid[4][1] = Knight('w',4,1)
        g.board.grid[6][5] = Knight('w',6,5)
        g.turn = 'w'

    def move(g):
        knight = g.board.grid[6][1]
        g.make_move(knight, 5, 3)

    run_test("Full disambiguation", setup, move, "Nb2d3")

def test_capture_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][5] = Knight('w',6,5)
        g.board.grid[4][5] = Knight('w',4,5)
        g.board.grid[5][3] = Pawn('b',5,3)
        g.turn = 'w'

    def move(g):
        knight = g.board.grid[6][5]
        g.make_move(knight, 5, 3)

    run_test("Capture disambiguation", setup, move, "N2xd3")

def test_kingside_castle():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[7][7] = Rook('w',7,7)
        g.board.grid[0][4] = King('b',0,4)
        g.turn = 'w'

    def move(g):
        king = g.board.grid[7][4]
        g.make_move(king, 7, 6)

    run_test("Kingside castling", setup, move, "O-O")

def test_promotion():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[1][4] = King('b',1,4)
        g.board.grid[1][0] = Pawn('w',1,0)
        g.turn = 'w'

    def move(g):
        pawn = g.board.grid[1][0]
        g.make_move(pawn, 0, 0)
        g.promote_pawn(pawn, 'q')

    run_test("Pawn promotion", setup, move, "a8=Q")

def test_promotion_check():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][7] = King('b',0,7)
        g.board.grid[1][5] = Pawn('w',1,5)
        g.turn = 'w'

    def move(g):
        pawn = g.board.grid[1][5]
        g.make_move(pawn, 0, 5)
        g.promote_pawn(pawn, 'q')

    run_test("Promotion with check", setup, move, "f8=Q+")

def test_promotion_mate():
    def setup(g):
        g.board.clear()
        g.board.grid[2][0] = King('w',2,0)
        g.board.grid[0][0] = King('b',0,0)
        g.board.grid[1][2] = Pawn('w',1,2)
        g.turn = 'w'

    def move(g):
        pawn = g.board.grid[1][2]
        g.make_move(pawn, 0, 2)
        g.promote_pawn(pawn, 'q')

    run_test("Promotion with mate", setup, move, "c8=Q#")



if __name__ == "__main__":
    test_quiet_move()
    test_capture()
    test_check()
    test_capture_check()
    test_checkmate()
    test_file_disambiguation()
    test_rank_disambiguation()
    test_full_disambiguation()
    test_capture_disambiguation()
    test_kingside_castle()
    test_promotion()
    test_promotion_check()
    test_promotion_mate()

    print("\nAll SAN tests passed 🎉")
