import torch
import random
import numpy as np
from collections import deque
from snake_game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.num_of_games = 0
        # Randomness
        self.epsilon = 0
        # Discount rate
        self.gamma = 0.9
        # If exceeds the memory then remove elements from the left
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, learning_rate=LR, gamma=self.gamma)

    def get_state(self, snake_game):
        snake_head = snake_game.snake[0]
        point_left  = Point(snake_head.x - 20, snake_head.y)
        point_right = Point(snake_head.x + 20, snake_head.y)
        point_up    = Point(snake_head.x, snake_head.y - 20)
        point_down  = Point(snake_head.x, snake_head.y + 20)

        dir_left  = snake_game.snake_direction == Direction.LEFT
        dir_right = snake_game.snake_direction == Direction.RIGHT
        dir_up    = snake_game.snake_direction == Direction.UP
        dir_down  = snake_game.snake_direction == Direction.DOWN

        state = [ 
            # Danger straight
            (dir_right and snake_game.is_collision(point_right)) or
            (dir_left and snake_game.is_collision(point_left)) or
            (dir_up and snake_game.is_collision(point_up)) or
            (dir_down and snake_game.is_collision(point_down)),

            # Danger right
            (dir_right and snake_game.is_collision(point_right)) or
            (dir_left and snake_game.is_collision(point_left)) or
            (dir_up and snake_game.is_collision(point_up)) or
            (dir_down and snake_game.is_collision(point_down)),

            # Danger left
            (dir_right and snake_game.is_collision(point_right)) or
            (dir_left and snake_game.is_collision(point_left)) or
            (dir_up and snake_game.is_collision(point_up)) or
            (dir_down and snake_game.is_collision(point_down)),

            # Move direction
            dir_left, dir_right, dir_up, dir_down,

            # Food loaction
            snake_game.food.x < snake_game.snake_head.x, # Food is left
            snake_game.food.x > snake_game.snake_head.x, # Food is right
            snake_game.food.y < snake_game.snake_head.y, # Food is up
            snake_game.food.y > snake_game.snake_head.y  # Food is down
        ]
        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done):
        # Popleft if MAX_MEMORY is reached
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            # Return a list of tuples
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Let the agent perform random moves at the start of training
        self.epsilon = 80 - self.num_of_games
        final_move = [0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    highest_score = 0
    agent = Agent()
    snake_game = SnakeGameAI()
    while True:
        # Get the current state
        current_state = agent.get_state(snake_game)
        # Get the final move
        final_move = agent.get_action(current_state)
        # Perform move and get a new state
        reward, done, score = snake_game.play_step(final_move)
        new_state = agent.get_state(snake_game)
        # Train the short memory of the agent
        agent.train_short_memory(current_state, final_move, reward, new_state, done)
        # Remember
        agent.remember(current_state, final_move, reward, new_state, done)

        if done:
            # Train the long memory of the agent and plot the results
            snake_game.reset()
            agent.num_of_games += 1
            agent.train_long_memory()

            if score > highest_score:
                highest_score = score
                agent.model.save()

            print('Game:', agent.num_of_games, 'Score:', score, 'Highest Score:', highest_score)

            plot_scores.append(score)
            total_score += score
            mean_scores = total_score / agent.num_of_games
            plot_mean_scores.append(mean_scores)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()