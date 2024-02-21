import pygame
import random
import time
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class SnakeGame:
    def __init__(self, width=600, height=450, seg_size=20):
        self.width = width
        self.height = height
        self.seg_size = seg_size
        
        # initialize the snake and apple positions
        self.snake = [(self.seg_size, self.seg_size), (0, self.seg_size), (-self.seg_size, 0)]
        self.apple = (0, 0)
        
    def draw(self):
        # clear the display and draw the game board with the current positions of the snake and apple
        window.fill((255, 255, 255))
        
        for x, y in self.snake:
            pygame.draw.rect(window, (0, 255, 0), (x - self.seg_size // 2, y - self.seg_size // 2, self.seg_size, self.seg_size))
        
        pygame.draw.rect(window, (255, 0, 0), self.apple)
        
    def move_snake(self):
        # update the snake's head position based on its previous movement
        head = list(self.snake[-1])
        
        if self.direction == Direction.UP:
            head[1] -= self.seg_size
        elif self.direction == Direction.DOWN:
            head[1] += self.seg_size
        elif self.direction == Direction.LEFT:
            head[0] -= self.seg_size
        elif self.direction == Direction.RIGHT:
            head[0] += self.seg_size
        
        # wrap around the edges of the board if necessary
        if head[0] < 0:
            head[0] = self.width - self.seg_size
        elif head[0] >= self.width - self.seg_size:
            head[0] = 0
        
        if head[1] < 0:
            head[1] = self.height - self.seg_size
        elif head[1] >= self.height - self.seg_size:
            head[1] = 0
        
        # add the new head position to the snake list and remove the last element (the tail)
        self.snake.append(tuple(head))
        self.snake.pop(0)
        
    def handle_input(self):
        # handle user input using Pygame's event system
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
    
    def is_collision(self):
        # check if the snake has collided with itself or the walls of the board
        for x, y in self.snake[1:]:
            if (x, y) == self.snake[-1]:
                return True
            
        head = list(self.snake[-1])
        
        return (head[0] < 0 or head[0] >= self.width - self.seg_size) \
            or (head[1] < 0 or head[1] >= self.height - self.seg_size)
    
    def main(self):
        # run the game loop here, including handling user input and updating game state based on movement
        self.direction = Direction.RIGHT
        
        while True:
            time.sleep(0.1)
            
            self.handle_input()
            
            # move the snake's head based on its previous movement
            self.move_snake()
            
            # generate a new apple position if the snake has eaten it
            if (self.apple[0], self.apple[1]) in self.snake:
                self.apple = (random.randint(0, self.width - self.seg_size), random.randint(0, self.height - self.seg_size))
            
            # update the current head position of the snake after moving it
            head = list(self.snake[-1])
            self.snake[-1] = tuple(head)
            
            # check if the snake has collided with itself or the walls of the board
            if self.is_collision():
                pygame.quit()
                sys.exit()
    
        # display the updated game board and redraw it repeatedly until the user quits
        window.blit(self.background, (0, 0))
        self.draw()
        pygame.display.flip()
        
    def __init__(self):
        # initialize Pygame and set up the game board and display
        pygame.init()
        
        
        self.window = pygame.display.set_mode((1280, 720))
        
        # initialize the game variables and load any necessary assets
        self.apple = (random.randint(0, 1280 - self.seg_size), random.randint(0, 720 - self.seg_size))
        self.direction = Direction.RIGHT
        
        # run the game's main method to start playing
        self.main()

# define the entry point for running the game
def main():
    # create a new instance of the Game class and start playing
    game = Game()