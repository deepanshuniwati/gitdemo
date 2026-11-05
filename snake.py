"""A small, colorful Snake game built with pygame.

Controls
--------
Arrow keys / WASD : steer the snake
SPACE / ENTER     : start or restart
ESC / Q           : quit

Run it with::

    python3 snake.py
"""

import random

import pygame

# --- Layout ---------------------------------------------------------------
CELL = 20
HUD_HEIGHT = 40
COLS = 40
ROWS = 28
WIDTH = COLS * CELL
HEIGHT = HUD_HEIGHT + ROWS * CELL
PLAY_TOP = HUD_HEIGHT
WINDOW_SIZE = (WIDTH, HEIGHT)

START_LENGTH = 3
START_STEP_MS = 140.0
MIN_STEP_MS = 70.0
SPEEDUP_PER_APPLE_MS = 4.0
FPS = 60

# --- Colors ---------------------------------------------------------------
BG = (16, 22, 30)
GRID = (25, 34, 45)
HUD_BG = (22, 30, 41)
HUD_LINE = (46, 60, 78)
TEXT = (236, 242, 248)
TEXT_DIM = (147, 163, 184)
GREEN_BRIGHT = (126, 247, 138)
GREEN_HEAD = (110, 240, 122)
GREEN_MID = (60, 200, 110)
GREEN_DARK = (22, 108, 88)
APPLE = (235, 66, 66)
APPLE_DARK = (160, 34, 44)
APPLE_SHINE = (255, 168, 158)
STEM = (120, 84, 52)
LEAF = (86, 196, 92)
OVERLAY = (8, 12, 18, 200)
DANGER = (255, 99, 99)
GOLD = (255, 210, 100)
EYE = (245, 250, 255)
PUPIL = (18, 38, 30)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def lerp_color(start, end, t):
    """Blend two RGB colors; ``t`` is clamped to 0..1."""
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(start, end))


class Snake:
    """Grid-based snake whose head is the first entry in ``positions``."""

    def __init__(self, positions, direction=RIGHT):
        self.positions = list(positions)
        self.direction = direction
        self.pending = []

    @property
    def head(self):
        return self.positions[0]

    def queue_direction(self, direction):
        """Queue a turn, ignoring reversals and duplicate inputs."""
        if direction not in (UP, DOWN, LEFT, RIGHT):
            return
        last = self.pending[-1] if self.pending else self.direction
        if direction == last:
            return
        if (direction[0] == -last[0] and direction[1] == -last[1]):
            return
        if len(self.pending) < 2:
            self.pending.append(direction)

    def next_direction(self):
        if self.pending:
            self.direction = self.pending.pop(0)
        return self.direction


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 96)
        self.big_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True
        self.best = 0
        self.reset()
        self.state = "start"

    # -- setup -------------------------------------------------------------
    def reset(self):
        self.score = 0
        self.won = False
        self.state = "start"
        self.step_ms = START_STEP_MS
        self.accumulator = 0.0
        mid_x = COLS // 2
        mid_y = ROWS // 2
        body = [(mid_x - i, mid_y) for i in range(START_LENGTH)]
        self.snake = Snake(body, RIGHT)
        self.food = self.spawn_food()

    def start_game(self):
        self.reset()
        self.state = "playing"

    def spawn_food(self):
        occupied = set(self.snake.positions)
        free = [
            (x, y)
            for y in range(ROWS)
            for x in range(COLS)
            if (x, y) not in occupied
        ]
        if not free:
            return None
        return random.choice(free)

    # -- input and simulation ---------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.state in ("start", "game_over"):
                        self.start_game()
                elif self.state == "playing":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.queue_direction(UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.queue_direction(DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.queue_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.queue_direction(RIGHT)

    def step(self):
        """Advance the game by one grid cell."""
        if self.state != "playing":
            return

        direction = self.snake.next_direction()
        head_x, head_y = self.snake.head
        new_head = (head_x + direction[0], head_y + direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self.end_game()
            return

        growing = new_head == self.food
        body = self.snake.positions if growing else self.snake.positions[:-1]
        if new_head in body:
            self.end_game()
            return

        self.snake.positions.insert(0, new_head)
        if growing:
            self.score += 1
            self.best = max(self.best, self.score)
            self.food = self.spawn_food()
            self.step_ms = max(
                MIN_STEP_MS, START_STEP_MS - self.score * SPEEDUP_PER_APPLE_MS
            )
            if self.food is None:
                self.won = True
                self.end_game()
        else:
            self.snake.positions.pop()

    def end_game(self):
        self.best = max(self.best, self.score)
        self.state = "game_over"

    def update(self, dt_ms):
        if self.state != "playing":
            return
        self.accumulator += dt_ms
        while self.accumulator >= self.step_ms and self.state == "playing":
            self.accumulator -= self.step_ms
            self.step()

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt_ms)
            self.render()
        pygame.quit()

    # -- drawing -----------------------------------------------------------
    def cell_rect(self, cell):
        x, y = cell
        return pygame.Rect(x * CELL + 1, PLAY_TOP + y * CELL + 1, CELL - 2, CELL - 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, HUD_BG, (0, 0, WIDTH, HUD_HEIGHT))
        pygame.draw.line(
            self.screen, HUD_LINE, (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 2
        )

        score = self.small_font.render(f"SCORE {self.score:>3}", True, TEXT)
        self.screen.blit(score, (14, (HUD_HEIGHT - score.get_height()) // 2))

        best = self.small_font.render(f"BEST {self.best:>3}", True, TEXT_DIM)
        self.screen.blit(best, (150, (HUD_HEIGHT - best.get_height()) // 2))

        hint = self.small_font.render("ARROWS / WASD TO MOVE  |  ESC TO QUIT", True, TEXT_DIM)
        self.screen.blit(
            hint,
            (
                WIDTH - hint.get_width() - 14,
                (HUD_HEIGHT - hint.get_height()) // 2,
            ),
        )

    def draw_board(self):
        pygame.draw.rect(self.screen, BG, (0, PLAY_TOP, WIDTH, HEIGHT - PLAY_TOP))
        for x in range(CELL, WIDTH, CELL):
            pygame.draw.line(self.screen, GRID, (x, PLAY_TOP), (x, HEIGHT))
        for y in range(PLAY_TOP + CELL, HEIGHT, CELL):
            pygame.draw.line(self.screen, GRID, (0, y), (WIDTH, y))

    def draw_food(self):
        if self.food is None:
            return
        center = (
            self.food[0] * CELL + CELL // 2,
            PLAY_TOP + self.food[1] * CELL + CELL // 2,
        )
        pygame.draw.circle(self.screen, APPLE_DARK, center, CELL // 2 - 3)
        pygame.draw.circle(self.screen, APPLE, center, CELL // 2 - 4)
        pygame.draw.circle(
            self.screen, APPLE_SHINE, (center[0] - 3, center[1] - 3), 2
        )
        pygame.draw.line(
            self.screen,
            STEM,
            (center[0], center[1] - CELL // 2 + 5),
            (center[0] + 1, center[1] - CELL // 2 + 1),
            2,
        )
        pygame.draw.circle(
            self.screen, LEAF, (center[0] + 5, center[1] - CELL // 2 + 3), 3
        )

    def draw_snake(self):
        total = len(self.snake.positions)
        for index, cell in enumerate(self.snake.positions):
            t = index / max(1, total - 1)
            if index == 0:
                color = GREEN_HEAD
            else:
                color = lerp_color(GREEN_MID, GREEN_DARK, t)
            pygame.draw.rect(self.screen, color, self.cell_rect(cell), border_radius=7)

        head_cell = self.snake.head
        cx = head_cell[0] * CELL + CELL // 2
        cy = PLAY_TOP + head_cell[1] * CELL + CELL // 2
        dx, dy = self.snake.direction
        px, py = -dy, dx
        eye_x = cx + dx * 3
        eye_y = cy + dy * 3
        for sign in (-1, 1):
            ex = int(round(eye_x + px * 4 * sign))
            ey = int(round(eye_y + py * 4 * sign))
            pygame.draw.circle(self.screen, EYE, (ex, ey), 2)
            pygame.draw.circle(self.screen, PUPIL, (ex, ey), 1)

    def draw_overlay(self):
        panel = pygame.Surface((WIDTH, HEIGHT - PLAY_TOP), pygame.SRCALPHA)
        panel.fill(OVERLAY)
        self.screen.blit(panel, (0, PLAY_TOP))

    def blit_centered(self, surface, y):
        self.screen.blit(surface, ((WIDTH - surface.get_width()) // 2, y))

    def draw_start_screen(self):
        self.draw_overlay()
        title = self.title_font.render("SNAKE", True, GREEN_BRIGHT)
        self.blit_centered(title, PLAY_TOP + 110)

        subtitle = self.font.render("Eat the apples. Grow. Don't crash.", True, TEXT)
        self.blit_centered(subtitle, PLAY_TOP + 200)

        controls = self.small_font.render(
            "Arrow keys or WASD to steer", True, TEXT_DIM
        )
        self.blit_centered(controls, PLAY_TOP + 260)

        prompt = self.font.render("Press SPACE to start", True, GOLD)
        self.blit_centered(prompt, PLAY_TOP + 340)

        quit_hint = self.small_font.render("Press ESC to quit", True, TEXT_DIM)
        self.blit_centered(quit_hint, PLAY_TOP + 390)

    def draw_game_over_screen(self):
        self.draw_overlay()
        if self.won:
            title_text, color = "YOU WIN!", GOLD
        else:
            title_text, color = "GAME OVER", DANGER
        title = self.big_font.render(title_text, True, color)
        self.blit_centered(title, PLAY_TOP + 120)

        score = self.font.render(f"Score: {self.score}", True, TEXT)
        self.blit_centered(score, PLAY_TOP + 210)

        best = self.small_font.render(f"Best: {self.best}", True, TEXT_DIM)
        self.blit_centered(best, PLAY_TOP + 255)

        prompt = self.font.render("Press SPACE to play again", True, GOLD)
        self.blit_centered(prompt, PLAY_TOP + 340)

        quit_hint = self.small_font.render("Press ESC to quit", True, TEXT_DIM)
        self.blit_centered(quit_hint, PLAY_TOP + 390)

    def render(self):
        self.screen.fill(BG)
        self.draw_board()
        if self.state != "start":
            self.draw_food()
            self.draw_snake()
        self.draw_hud()
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "game_over":
            self.draw_game_over_screen()
        pygame.display.flip()


def main():
    game = Game()
    try:
        game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
