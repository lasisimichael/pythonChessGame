import pygame
from game import GameState
import game
from renderer import Renderer

def mouse_to_square(pos, renderer):
    x, y = pos
    col = (x - renderer.board_x) // renderer.square_size
    row = (y - renderer.board_y) // renderer.square_size

    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None

def main():
    game_over = False
    selected_piece = None
    legal_targets = []
    last_move_square = None

    pygame.init()
    window = pygame.display.set_mode((576, 640))

    game = GameState()
    renderer = Renderer(window, game.board)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.promotion_pending:
                    choice = renderer.handle_promotion_click(event.pos)
                    if choice:
                        pawn, _, _ = game.promotion_pending
                        game.promote_pawn(pawn, choice)
                    continue

                if game_over:
                    game = GameState()
                    renderer = Renderer(window, game.board)

                    selected_piece = None
                    legal_targets = []
                    last_move_square = None
                    game_over = False
                    continue

                square = mouse_to_square(event.pos, renderer)

                if square is None:
                    selected_piece = None
                    legal_targets = []
                    continue

                row, col = square

                # Ignore clicks outside board
                if not (0 <= row < 8 and 0 <= col < 8):
                    selected_piece = None
                    legal_targets = []
                    continue

                clicked_piece = game.board.grid[row][col]

                if selected_piece is None:
                    if clicked_piece and clicked_piece.color == game.turn:
                        selected_piece = clicked_piece
                        legal_targets = [
                            (r, c) for (p, r, c) in game.get_legal_moves()
                            if p == selected_piece
                        ]

                else:
                    if (row, col) in legal_targets:
                        game.make_move(selected_piece, row, col)

                    if game.is_checkmate(game.turn) or game.is_stalemate(game.turn):
                        game_over = True

                        last_move_square = (row, col)
                        selected_piece = None
                        legal_targets = []

                    elif clicked_piece and clicked_piece.color == game.turn:
                        selected_piece = clicked_piece
                        legal_targets = [
                            (r, c) for (p, r, c) in game.get_legal_moves()
                            if p == selected_piece
                        ]

                    else:
                        selected_piece = None
                        legal_targets = []
        
        status_text = ""
        if game.is_checkmate(game.turn):
            winner = "White" if game.turn == 'b' else "Black"
            status_text = f"Checkmate! {winner} wins"

        elif game.is_stalemate(game.turn):
            status_text = "Stalemate"

        elif game.is_in_check(game.turn):
            side = "White" if game.turn == 'w' else "Black"
            status_text = f"{side} is in check"

        else:
            side = "White" if game.turn == 'w' else "Black"
            status_text = f"{side} to move"

        renderer.draw_board()

        if legal_targets:
            renderer.highlight_moves(legal_targets)

        if last_move_square:
            r, c = last_move_square
            renderer.highlight_square(r, c)

        if game.is_in_check(game.turn):
            king_pos = game.find_king(game.turn)
            if king_pos:
                renderer.highlight_square(king_pos[0], king_pos[1], color=(255, 0, 0))

        renderer.draw_pieces()
        renderer.draw_status_bar(status_text)

        if game_over:
            renderer.dim_board()
            renderer.draw_restart_prompt()

        if game.promotion_pending:
            pawn, _, _ = game.promotion_pending
            renderer.dim_board()
            renderer.draw_promotion_menu(pawn.color)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
