from game import GameState
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

def test_redo_identity():
    g = GameState()
    g.make_move(g.board.grid[6][4], 4, 4)  # e4

    key_after = g.position_key()

    g.undo_move()
    g.redo_move()

    assert g.position_key() == key_after
    assert g.san_history[-1] == "e4"

def test_multi_redo():
    g = GameState()
    g.make_move(g.board.grid[6][4], 4, 4)  # e4
    g.make_move(g.board.grid[1][4], 3, 4)  # e5

    key = g.position_key()

    g.undo_move()
    g.undo_move()
    g.redo_move()
    g.redo_move()

    assert g.position_key() == key
    assert g.san_history == ["e4", "e5"]

def test_redo_promotion():
    g = GameState()
    g.setup_promotion_test()

    pawn = g.board.grid[1][0]
    g.make_move(pawn, 0, 0)
    g.promote_pawn(pawn, 'q')

    key = g.position_key()
    san = g.san_history[-1]

    g.undo_move()
    g.redo_move()

    assert g.position_key() == key
    assert g.san_history[-1] == san

def test_redo_castling():
    g = GameState()
    g.board.clear()

    wk = King('w', 7, 4)
    wr = Rook('w', 7, 7)
    bk = King('b', 0, 4)

    g.board.grid[7][4] = wk
    g.board.grid[7][7] = wr
    g.board.grid[0][4] = bk
    g.turn = 'w'

    g.make_move(wk, 7, 6)
    key = g.position_key()

    g.undo_move()
    g.redo_move()

    assert g.position_key() == key
    assert g.san_history[-1] == "O-O"

if __name__ == "__main__":
    test_redo_identity()
    test_multi_redo()
    test_redo_promotion()
    test_redo_castling()

    print("\nAll redo tests passed 🎉")
