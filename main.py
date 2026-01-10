import pygame
from game import GameState
from renderer import Renderer

def mouse_to_square(pos, renderer):
    x, y = pos
    col = (x - renderer.board_x) // renderer.square_size
    row = (y - renderer.board_y) // renderer.square_size

    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None

def handle_undo(game):
    # If promotion UI is open, cancel it instead of undoing
    if not game.move_history or game.promotion_pending:
        return

    game.undo_move()

def handle_redo(game):
    if not game.redo_stack or game.promotion_pending:
        return

    game.redo_move()

def sync_last_move(game):
    if game.move_history:
        last = game.move_history[-1]
        return (
            (last.from_row, last.from_col),
            (last.to_row, last.to_col),
        )
    return None, None

def main():
    selected_move_index = 0
    game_over = False
    selected_piece = None
    legal_targets = []
    last_move_square = None
    last_move_square_prev_square = None

    pygame.init()
    window = pygame.display.set_mode((800, 640))

    game = GameState()

    renderer = Renderer(window, game.board)
    renderer.move_scroll_offset = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Redo move
                if event.key == pygame.K_r:
                    handle_redo(game)
                    selected_piece = None
                    legal_targets = []
                    selected_move_index = len(game.move_history)
                    last_move_square, last_move_square_prev_square = sync_last_move(game)

                # Save PGN file
                if event.key == pygame.K_s:
                    game.export_pgn()

                # Undo move
                if event.key == pygame.K_u:
                    handle_undo(game)
                    selected_piece = None
                    legal_targets = []
                    selected_move_index = len(game.move_history)
                    last_move_square, last_move_square_prev_square = sync_last_move(game)

            if event.type == pygame.MOUSEWHEEL:
                renderer.move_scroll_offset -= event.y * 2

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    game = GameState()
                    renderer = Renderer(window, game.board)
                    selected_move_index = 0
                    renderer.move_scroll_offset = 0
                    selected_piece = None
                    legal_targets = []
                    last_move_square = None
                    last_move_square_prev_square = None
                    game_over = False
                    continue

                if game.promotion_pending:
                    choice = renderer.handle_promotion_click(event.pos)
                    if choice:
                        pawn, _, _ = game.promotion_pending
                        game.promote_pawn(pawn, choice)
                        selected_move_index = len(game.move_history)
                        last_move_square, last_move_square_prev_square = sync_last_move(game)

                    continue

                clicked_ply = renderer.get_clicked_move_index(event.pos)
                if clicked_ply is not None:
                    selected_piece = None
                    legal_targets = []

                    current_index = len(game.move_history)

                    while current_index > clicked_ply:
                        game.undo_move()
                        current_index -= 1

                    while current_index < clicked_ply:
                        if not game.redo_stack:
                            break
                        game.redo_move()
                        current_index += 1

                    last_move_square, last_move_square_prev_square = sync_last_move(game)
                    selected_move_index = clicked_ply
                    continue

                if hasattr(renderer, "undo_rect"):
                    if renderer.undo_rect.collidepoint(event.pos) and game.move_history:
                        handle_undo(game)
                        selected_piece = None
                        legal_targets = []
                        selected_move_index = len(game.move_history)
                        last_move_square, last_move_square_prev_square = sync_last_move(game)
                        continue
                if hasattr(renderer, "redo_rect"):
                    if renderer.redo_rect.collidepoint(event.pos) and game.redo_stack:
                        handle_redo(game)
                        selected_piece = None
                        legal_targets = []
                        selected_move_index = len(game.move_history)
                        last_move_square, last_move_square_prev_square = sync_last_move(game)
                        continue

                square = mouse_to_square(event.pos, renderer)

                if square is None:
                    selected_piece = None
                    legal_targets = []
                    continue

                row, col = square

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
                        selected_move_index = len(game.move_history)
                        renderer.move_scroll_offset = 10**9  # Scroll to bottom

                        last_move = game.move_history[-1] if game.move_history else None
                        if last_move:
                            last_move_square, last_move_square_prev_square = sync_last_move(game)
                        else:
                            last_move_square = None
                            last_move_square_prev_square = None

                    if game.game_over:
                        game_over = True

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
        
        status = game.get_game_status()

        if status:
            kind, winner = status
            if kind == "checkmate":
                status_text = f"Checkmate! {'White' if winner == 'w' else 'Black'} wins"
            elif kind == "stalemate":
                status_text = "Stalemate"
            elif kind == "fifty-move":
                status_text = "Draw by 50-move rule"
            elif kind == "threefold":
                status_text = "Draw by repetition"
            elif kind == "insufficient":
                status_text = "Draw by insufficient material"
        else:
            side = "White" if game.turn == 'w' else "Black"
            status_text = f"{side} to move"

        renderer.draw_board()

        move_list_height = (
            renderer.square_size * 8
            - renderer.button_height
            - 12  # spacing between list and buttons
        )
        renderer.draw_move_list(
            game.san_history,
            start_x=renderer.board_x + 8 * renderer.square_size + 42 ,
            start_y=20,
            height=move_list_height,
            selected_index=selected_move_index
        )

        buttons_y = 20 + move_list_height + 12
        buttons_x = renderer.board_x + 8 * renderer.square_size + 42

        renderer.draw_undo_redo_buttons(
            buttons_x,
            buttons_y,
            can_undo=bool(game.move_history),
            can_redo=bool(game.redo_stack)
        )

        if last_move_square:
            r, c = last_move_square
            renderer.highlight_square(r, c)

            r, c = last_move_square_prev_square
            renderer.highlight_square(r, c, color=(255, 0, 255))

        if legal_targets:
            renderer.highlight_moves(legal_targets)

        if game.is_in_check(game.turn):
            king_pos = game.find_king(game.turn)
            if king_pos:
                renderer.highlight_square(king_pos[0], king_pos[1], color=(255, 0, 0))

        renderer.draw_pieces()
        renderer.draw_status_bar(status_text)

        if game_over:
            game.export_pgn()
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
