import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

BLOCK_SIZE = 20
SPEED = 20

# RGB colors
BLACK = (0,0,0)
RED = (200,0,0)
WHITE = (255,255,255)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)

class SnakeGame:

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # Initialize display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
    
        # Initialize game state
        self.snake_direction = Direction.RIGHT

        self.snake_head = Point(self.width/2, self.height/2)
        self.snake = [self.snake_head, Point(self.snake_head.x-BLOCK_SIZE, self.snake_head.y), Point(self.snake_head.x-(2*BLOCK_SIZE), self.snake_head.y)]

        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0,(self.width-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0,(self.height-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x,y)

        # Make sure that the food does not spawn inside of the snake
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        # Collect the users input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.snake_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.snake_direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.snake_direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.snake_direction = Direction.DOWN

        # Move the snake
        self._move(self.snake_direction)
        self.snake.insert(0, self.snake_head)
        # Check if the game is over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
        # Place new fodd or move the snake
        if self.snake_head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
        # Update the user interface and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # Return game over and score
        game_over = False
        return game_over, self.score
    
    def _is_collision(self):
        # Check if the snake hits the boundary
        if self.snake_head.x > self.width - BLOCK_SIZE or self.snake_head.x < 0 or self.snake_head.y > self.height - BLOCK_SIZE or self.snake_head.y < 0:
            return True
        # Check if the snake hits itself
        if self.snake_head in self.snake[1:]:
            return True
        # Return false if no collision 
        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for point in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(point.x+4, point.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.snake_head.x
        y = self.snake_head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        
        self.snake_head = Point(x,y)

if __name__ == '__main__':
    game = SnakeGame()

    # Loop through the game
    while True:
        game_over, score = game.play_step()

        # Break the loop when the game ends
        if game_over == True:
            break
    
    print(f'Final Score: {score}')


    pygame.quit()