from game import GameState
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

def roundtrip_test(name, setup_fn, move_fn):
    game = GameState()
    setup_fn(game)
    move_fn(game)

    san = game.san_history[-1]
    
    game2 = GameState()
    setup_fn(game2)

    parsed = game2.parse_san(san)
    game2.apply_parsed_san(parsed)

    san2 = game2.san_history[-1]

    assert san == san2, f"{name} FAILED: {san} → {san2}"
    print(f"✔ {name}")

def test_roundtrip_quiet():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][4] = Pawn('w',6,4)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[6][4], 5, 4)

    roundtrip_test("Roundtrip quiet pawn", setup, move)

def test_roundtrip_capture():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][4] = Pawn('w',6,4)
        g.board.grid[5][3] = Pawn('b',5,3)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[6][4], 5, 3)

    roundtrip_test("Roundtrip pawn capture", setup, move)

def test_roundtrip_check():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][0] = Rook('w',6,0)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[6][0], 0, 0)

    roundtrip_test("Roundtrip Check", setup, move)

def test_roundtrip_capture_check():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[4][4] = Queen('w',4,4)
        g.board.grid[2][4] = Rook('b',2,4)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[4][4], 2, 4)

    roundtrip_test("Roundtrip Capture with check", setup, move)

def test_roundtrip_checkmate():
    def setup(g):
        g.board.clear()
        g.board.grid[0][0] = King('b',0,0)
        g.board.grid[2][1] = Queen('w',2,1)
        g.board.grid[2][0] = King('w',2,0)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[2][1], 1, 1)

    roundtrip_test("Roundtrip Checkmate", setup, move)

def test_roundtrip_file_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[4][7] = Knight('w',4,7)
        g.board.grid[4][5] = Knight('w',4,5)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[4][7], 6, 6)

    roundtrip_test("Rpundtrip File disambiguation", setup, move)

def test_roundtrip_rank_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[7][6] = Knight('w',7,6)
        g.board.grid[5][6] = Knight('w',5,6)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[7][6], 6, 4)

    roundtrip_test("Roundtrip Rank disambiguation", setup, move)

def test_roundtrip_full_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][1] = Knight('w',6,1)
        g.board.grid[4][1] = Knight('w',4,1)
        g.board.grid[6][5] = Knight('w',6,5)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[6][1], 5, 3)

    roundtrip_test("Roundtrip Full disambiguation", setup, move)

def test_roundtrip_capture_disambiguation():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[0][4] = King('b',0,4)
        g.board.grid[6][5] = Knight('w',6,5)
        g.board.grid[4][5] = Knight('w',4,5)
        g.board.grid[5][3] = Pawn('b',5,3)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[6][5], 5, 3)

    roundtrip_test("Roundtrip Capture disambiguation", setup, move)

def test_roundtrip_kingside_castle():
    def setup(g):
        g.board.clear()
        g.board.grid[7][4] = King('w',7,4)
        g.board.grid[7][7] = Rook('w',7,7)
        g.board.grid[0][4] = King('b',0,4)
        g.turn = 'w'

    def move(g):
        g.make_move(g.board.grid[7][4], 7, 6)

    roundtrip_test("Roundtrip Kingside castling", setup, move)

def test_roundtrip_promotion():
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

    roundtrip_test("Roundtrip Pawn promotion", setup, move)

def test_roundtrip_promotion_check():
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

    roundtrip_test("Roundtrip Promotion with check", setup, move)

def test_roundtrip_promotion_mate():
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

    roundtrip_test("Roundtrip Promotion with mate", setup, move)



if __name__ == "__main__":
    test_roundtrip_quiet()
    test_roundtrip_capture()
    test_roundtrip_check()
    test_roundtrip_capture_check()
    test_roundtrip_checkmate()
    test_roundtrip_file_disambiguation()
    test_roundtrip_rank_disambiguation()
    test_roundtrip_full_disambiguation()
    test_roundtrip_capture_disambiguation()
    test_roundtrip_kingside_castle()
    test_roundtrip_promotion()
    test_roundtrip_promotion_check()
    test_roundtrip_promotion_mate()

    print("\nAll SAN round trip tests passed 🎉")
