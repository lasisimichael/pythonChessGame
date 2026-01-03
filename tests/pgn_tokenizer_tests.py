from game import GameState
from pgn import tokenize_pgn

def run_test(name, pgn, expected):
    tokens = tokenize_pgn(pgn)
    assert tokens == expected, f"{name} FAILED\nExpected: {expected}\nGot: {tokens}"
    print(f"✔ {name}")

def test_basic_game():
    pgn = "1. e4 e5 2. Nf3 Nc6"
    run_test(
        "Basic game",
        pgn,
        ["e4", "e5", "Nf3", "Nc6"]
    )

def test_headers():
    pgn = """
    [Event "Test"]
    [White "Alice"]
    [Black "Bob"]

    1. e4 e5
    """
    run_test(
        "Headers stripped",
        pgn,
        ["e4", "e5"]
    )

def test_comments():
    pgn = "1. e4 {best by test} e5"
    run_test(
        "Comments removed",
        pgn,
        ["e4", "e5"]
    )

def test_variations():
    pgn = "1. e4 (1. d4 d5 (1... Nf6)) e5"
    run_test(
        "Variations removed",
        pgn,
        ["e4", "e5"]
    )

def test_results():
    pgn = "1. e4 e5 1-0"
    run_test(
        "Results stripped",
        pgn,
        ["e4", "e5"]
    )

def test_black_move_numbers():
    pgn = "1... e5 2... Nc6"
    run_test(
        "Black move numbers",
        pgn,
        ["e5", "Nc6"]
    )

def test_realistic_pgn():
    pgn = """
    [Event "Casual Game"]
    [Result "1-0"]

    1. e4 e5 2. Nf3 Nc6
    3. Bb5 a6 (3... Nf6)
    4. Ba4 Nf6
    1-0
    """
    run_test(
        "Realistic PGN",
        pgn,
        ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6"]
    )

def test_realistic_pgn():
    pgn = """
    [Event "Casual Game"]
    [Result "1-0"]

    1. e4 e5 2. Nf3 Nc6
    3. Bb5 a6 (3... Nf6)
    4. Ba4 Nf6
    1-0
    """
    run_test(
        "Realistic PGN",
        pgn,
        ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6"]
    )

def test_promotion_tokens():
    pgn = """
    [Event "Promotion Test"]
    1. a4 h5
    2. a5 h4
    3. a6 h3
    4. axb7 hxg2
    5. bxa8=Q gxh1=N
    """

    tokens = tokenize_pgn(pgn)

    assert tokens == [
        "a4", "h5",
        "a5", "h4",
        "a6", "h3",
        "axb7", "hxg2",
        "bxa8=Q", "gxh1=N"
    ]

def test_promotion_with_check_and_mate():
    pgn = "1. e8=Q+ d1=N#"

    tokens = tokenize_pgn(pgn)

    assert tokens == ["e8=Q+", "d1=N#"]

def test_load_simple_pgn():
    pgn = """
    1. e4 e5
    2. Nf3 Nc6
    3. Bb5 a6
    4. Ba4 Nf6
    """

    game = GameState()
    game.load_pgn(pgn)

    assert game.san_history == [
        "e4", "e5",
        "Nf3", "Nc6",
        "Bb5", "a6",
        "Ba4", "Nf6"
    ]

def test_load_pgn_promotion():
    pgn = """
    1. a4 h5
    2. a5 h4
    3. a6 h3
    4. axb7 hxg2
    5. bxa8=Q
    """

    game = GameState()
    game.load_pgn(pgn)

    assert game.san_history[-1] == "bxa8=Q"

def test_load_pgn_castling():
    pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O"

    game = GameState()
    game.load_pgn(pgn)

    assert game.san_history[-1] == "O-O"

def test_load_pgn_disambiguation():
    pgn = "1. Nf3 Nf6 2. Ng1 Ng8 3. Nf3"

    game = GameState()
    game.load_pgn(pgn)

    assert game.san_history[-1].startswith("N")

def test_load_pgn_checkmate_result():
    pgn = "1. f3 e5 2. g4 Qh4#"

    game = GameState()
    game.load_pgn(pgn)

    assert game.game_over
    assert game.game_result == "0-1"



if __name__ == "__main__":
    test_basic_game()
    test_headers()
    test_comments()
    test_variations()
    test_results()
    test_black_move_numbers()
    test_realistic_pgn()
    test_promotion_tokens()
    test_promotion_with_check_and_mate()
    test_load_simple_pgn()
    test_load_pgn_promotion()

    print("\nAll PGN tests passed 🎉")
