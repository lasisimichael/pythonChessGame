import re

def strip_headers(pgn: str) -> str:
    lines = pgn.strip().splitlines()
    movetext_lines = [
        line for line in lines
        if not line.lstrip().startswith("[")
    ]
    return " ".join(movetext_lines)

def remove_comments(text: str) -> str:
    return re.sub(r"\{[^}]*\}", "", text)

def remove_variations(text: str) -> str:
    result = []
    depth = 0

    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            result.append(ch)

    return "".join(result)

def remove_move_numbers(text: str) -> str:
    return re.sub(r"\b\d+\.(?:\.\.)?", "", text)

def remove_results(tokens: list[str]) -> list[str]:
    return [
        t for t in tokens
        if t not in {"1-0", "0-1", "1/2-1/2", "*"}
    ]

def tokenize_pgn(pgn: str) -> list[str]:
    text = strip_headers(pgn)
    text = remove_comments(text)
    text = remove_variations(text)
    text = remove_move_numbers(text)

    tokens = text.split()
    tokens = remove_results(tokens)

    return tokens
