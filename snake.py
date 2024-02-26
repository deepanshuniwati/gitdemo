import pygame
import sys
import random
pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None)
        self.width, self.height = self.screen.get_size()
        self.snake_speed = 5
        self.food = (random.randint(0, self.width // self.snake_speed) * self.snake_speed, random.randint(0, self.height // self.snake_speed) * self.snake_speed)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.snake_direction = (0, -self.snake_speed)
            elif keys[pygame.K_DOWN]:
                self.snake_direction = (0, self.snake_speed)
            elif keys[pygame.K_LEFT]:
                self.snake_direction = (-self.snake_speed, 0)
            elif keys[pygame.K_RIGHT]:
                self.snake_direction = (self.snake_speed, 0)

    def update(self):
        self.check_collision()
        self.snake.move(self.snake_direction)
        self.food_collision()

    def check_collision(self):
        head = self.snake.positions[0]
        wall_collision = head[0] < 0 or head[0] > self.width or head[1] < 0 or head[1] > self.height
        self.snake.reversed = wall_collision
        self.snake.positions = list(self.snake.move(self.snake.direction))
        body_collision = any(abs(h[0] - head[0]) < self.snake.size and abs(h[1] - head[1]) < self.snake.size for h in self.snake.positions[1:])
        if wall_collision or body_collision:
            self.running = False
            pygame.quit()
            sys.exit()

    def food_collision(self):
        head = self.snake.positions[0]
        if head == self.food:
            self.grow()
            self.food = (random.randint(0, self.width // self.snake_speed) * self.snake_speed, random.randint(0, self.height // self.snake_speed) * self.snake_speed)

    def render(self):
        self.screen.fill((0, 0, 0))
        self.render_snake()
        self.render_food()
        pygame.display.set_caption("Snake Game - Press ESC to Quit")
        pygame.display.flip()

    def grow(self):
        self.snake.positions.append(self.snake.positions[-1])
        self.snake.size += 5

class Snake:
    def __init__(self, pos=(0, 0), direction=(0, 0), size=10):
        self.positions = [pos]
        self.direction = direction
        self.size = size

    def move(self, direction):
        new_head = (self.positions[-1][0] + direction[0], self.positions[-1][1] + direction[1])
        self.positions.append(new_head)
        return self.positions

game = Game()
game.run()