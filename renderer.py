import pygame

class Renderer:
    def __init__(self, window, board):
        self.window = window
        self.board = board
        self.board_x = 32
        self.board_y = 32
        self.square_size = 64
        self.images = {}
        self.status_height = 48
        self.status_y = self.board_y + 8 * self.square_size + 32
        self.status_font = pygame.font.SysFont("arial", 22, bold=True)
        self.font = pygame.font.SysFont("arial", 18)
        self.load_images()

    def load_images(self):
        for piece in ['bp','br','bn','bb','bq','bk','wp','wr','wn','wb','wq','wk']:
            img = pygame.image.load(f"images/{piece}.png")
            img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
            self.images[piece] = img

    def draw_board(self):
        self.window.fill((235, 209, 166))
        self.draw_labels()
        for row in range(8):
            for col in range(8):
                color = (235, 209, 166) if (row + col) % 2 == 0 else (106, 45, 29)
                pygame.draw.rect(
                    self.window,
                    color,
                    (self.board_x + col * self.square_size, self.board_y + row * self.square_size,
                     self.square_size, self.square_size)
                )

        # Thin black border around the board
        pygame.draw.rect(
            self.window,
            (0, 0, 0),
            (
                self.board_x,
                self.board_y,
                8 * self.square_size,
                8 * self.square_size
            ),
            1
        )

    def draw_labels(self):
        files = "abcdefgh"
        for col in range(8):
            letter = self.font.render(files[col], True, (0, 0, 0))
            x = self.board_x + col * self.square_size + self.square_size // 2 - letter.get_width() // 2

            # Top
            self.window.blit(letter, (x, 8))

            # Bottom
            self.window.blit(letter, (x, self.board_y + 8 * self.square_size + 8))

        for row in range(8):
            number = self.font.render(str(8 - row), True, (0, 0, 0))
            y = self.board_y + row * self.square_size + self.square_size // 2 - number.get_height() // 2

            # Left
            self.window.blit(number, (8, y))

            # Right
            self.window.blit(number, (self.board_x + 8 * self.square_size + 8, y))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]

                if piece:
                    key = piece.color + piece.symbol
                    self.window.blit(
                        self.images[key],
                        (self.board_x + col * self.square_size, self.board_y + row * self.square_size)
                    )

    def draw_status_bar(self, status_text, can_undo=False):
        bar_height = 64
        y = self.status_y

        # Background
        pygame.draw.rect(
            self.window,
            (20, 20, 20),
            (0, y, self.window.get_width(), bar_height)
        )

        if can_undo:
            full_text = f"{status_text}   •   [U] Undo"
        else:
            full_text = status_text

        # Text
        font = pygame.font.SysFont(None, 28)
        text_color = (240, 240, 240)

        if can_undo:
            full_text = f"{status_text}   •   [U] Undo"
        else:
            full_text = status_text

        text_surface = font.render(full_text, True, text_color)
        text_rect = text_surface.get_rect()

        text_rect.centerx = self.window.get_width() // 2
        text_rect.centery = y + bar_height // 2

        self.window.blit(text_surface, text_rect)

    def highlight_moves(self, moves):
        for r, c in moves:
            if self.board.grid[r][c] is not None:
                pygame.draw.rect(
                    self.window,
                    (255, 255, 0),
                    (self.board_x + c * self.square_size, self.board_y + r * self.square_size,
                     self.square_size, self.square_size),
                    4
                )
            else:
                center = (
                    self.board_x + c * self.square_size + self.square_size // 2,
                    self.board_y + r * self.square_size + self.square_size // 2
                )
                pygame.draw.circle(self.window, (0, 255, 0), center, 10)

    def highlight_square(self, row, col, color=(0, 255, 0)):
        pygame.draw.rect(
            self.window,
            color,
            (self.board_x + col * self.square_size, self.board_y + row * self.square_size,
             self.square_size, self.square_size),
            4
        )

    def dim_board(self, alpha=160):
        """
        Draw a semi-transparent overlay over the board area.
        """
        overlay = pygame.Surface((8 * self.square_size, 8 * self.square_size))
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))

        self.window.blit(overlay, (self.board_x, self.board_y))

    def draw_restart_prompt(self):
        font_big = pygame.font.SysFont("arial", 28, bold=True)
        font_small = pygame.font.SysFont("arial", 20)

        title = font_big.render("Game Over", True, (255, 255, 255))
        prompt = font_small.render("Click anywhere to restart", True, (220, 220, 220))

        center_x = self.board_x + 4 * self.square_size
        center_y = self.board_y + 4 * self.square_size

        self.window.blit(
            title,
            (center_x - title.get_width() // 2, center_y - 40)
        )

        self.window.blit(
            prompt,
            (center_x - prompt.get_width() // 2, center_y + 10)
        )

    def draw_promotion_menu(self, color):
        pieces = ['q', 'r', 'b', 'n']

        popup_size = self.square_size * 4
        x = self.board_x + (8 * self.square_size - popup_size) // 2
        y = self.board_y + (8 * self.square_size - self.square_size) // 2

        self.promotion_rects = []

        # Background
        pygame.draw.rect(
            self.window,
            (40, 40, 40),
            (x, y, popup_size, self.square_size),
            border_radius=8
        )

        pygame.draw.rect(
            self.window,
            (200, 200, 200),
            (x, y, popup_size, self.square_size),
            2,
            border_radius=8
        )

        for i, p in enumerate(pieces):
            px = x + i * self.square_size
            py = y
            key = color + p

            self.window.blit(self.images[key], (px, py))

            rect = pygame.Rect(px, py, self.square_size, self.square_size)
            self.promotion_rects.append((rect, p))

    def handle_promotion_click(self, pos):
        if not hasattr(self, "promotion_rects"):
            return None

        for rect, piece in self.promotion_rects:
            if rect.collidepoint(pos):
                return piece
        return None

    def draw_move_list(self, san_history, start_x, start_y, height):
        panel_width = self.window.get_width() - start_x - 10

        pygame.draw.rect(
            self.window,
            (30, 30, 30),
            (start_x - 8, start_y - 8, panel_width, height + 16),
            border_radius=6
        )

        font = pygame.font.SysFont(None, 24)
        line_height = 22
        max_lines = height // line_height

        moves = []
        for i in range(0, len(san_history), 2):
            white = san_history[i]
            black = san_history[i+1] if i+1 < len(san_history) else ""
            moves.append(f"{i//2 + 1}. {white:<6} {black}")

        # Scroll last moves into view
        moves = moves[-max_lines:]

        for i, text in enumerate(moves):
            surf = font.render(text, True, (230, 230, 230))
            self.window.blit(surf, (start_x, start_y + i * line_height))
