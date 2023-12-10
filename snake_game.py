import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

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

class SnakeGameAI:

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # Initialize display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        
    
    def reset(self):
        # Initialize game state
        self.snake_direction = Direction.RIGHT

        self.snake_head = Point(self.width/2, self.height/2)
        self.snake = [self.snake_head, Point(self.snake_head.x-BLOCK_SIZE, self.snake_head.y), Point(self.snake_head.x-(2*BLOCK_SIZE), self.snake_head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0,(self.width-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0,(self.height-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x,y)

        # Make sure that the food does not spawn inside of the snake
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # Collect the users input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Move the snake
        self._move(action)
        self.snake.insert(0, self.snake_head)
        # Check if the game is over
        reward = 0
        game_over = False
        # If there is a collision or the snake does not make any progress for a certain time 
        if self._is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        # Place new fodd or move the snake
        if self.snake_head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        # Update the user interface and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # Return game over and score
        game_over = False
        return reward, game_over, self.score
    
    def _is_collision(self, point=None):
        if point is None:
            point = self.snake_head
        # Check if the snake hits the boundary
        if point.x > self.width - BLOCK_SIZE or point.x < 0 or point.y > self.height - BLOCK_SIZE or point.y < 0:
            return True
        # Check if the snake hits itself
        if point in self.snake[1:]:
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

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.snake_direction)

        if np.array_equal(action, [1,0,0]):
            # No change in the direction
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0,1,0]):
            next_index = (index + 1) % 4
            # Right turn in the direction
            new_direction = clock_wise[next_index]
        else:
            next_index = (index - 1) % 4
            # Left turn in the direction
            new_direction = clock_wise[next_index]

        self.snake_direction = new_direction
            
        x = self.snake_head.x
        y = self.snake_head.y
        if self.snake_direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.snake_direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.snake_direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.snake_direction == Direction.UP:
            y -= BLOCK_SIZE
        
        self.snake_head = Point(x,y)