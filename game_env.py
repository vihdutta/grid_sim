import gymnasium as gym
from gymnasium import spaces
import numpy as np
from helpers.sim_objects import Entity, Coin
from helpers.draw import generate_unique_positions, draw_scene
import random
import pygame

class GameEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()
        
        # Game constants
        self.CELLS = 12  # not constant
        self.ENTITIES = 1
        self.COINS = 1
        self.ENTITY_COLOR = (50, 175, 50)
        self.COIN_COLOR = (255, 230, 10)
        self.GAME_DECISION_LIMIT = 2 * (self.CELLS-1)
        self.score = 0
        
        # Define action and observation space
        self.action_space = spaces.Discrete(8)  # up, down, left, right
        
        # Observation space: distances in all 4 directions
        self.observation_space = spaces.Box(
            low=0, 
            high=float('inf'), 
            shape=(12,), 
            dtype=np.float32
        )
        
        self.render_mode = render_mode
        if render_mode == 'human':
            pygame.init()
            pygame.font.init()
            pygame.display.set_caption("DQN Game Training")
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 800
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.scale_factor = 1.0
            self.grid_x_offset = 0
            self.grid_y_offset = 0
        
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # change self.CELLS size
        # self.CELLS = random.randint(2, 12)
        
        # Generate positions
        entity_positions = generate_unique_positions(self.ENTITIES, self.CELLS)
        coin_positions = generate_unique_positions(self.COINS, self.CELLS, existing_positions=entity_positions)
        
        # Create entities and coins
        self.entity = Entity(entity_positions[0][0], entity_positions[0][1], self.ENTITY_COLOR)
        self.coin = Coin(coin_positions[0][0], coin_positions[0][1], self.COIN_COLOR)
        
        # Reset counters
        self.steps = 0
        
        # Get initial observation
        observation = self._get_observation()

        if self.render_mode == "human":
            self.render()
        
        return observation, {}

    def step(self, action):
        # Get distances before move for reward calculation
        prev_distances = self.entity.get_manhattan_distances(self.coin, self.CELLS)
        
        # Execute action
        hit_wall, moved_unoptimal = self.entity.move(action, prev_distances, self.CELLS)
        
        # Get new observation
        observation = self._get_observation()
        
        # Calculate reward
        reward = self._calculate_reward(hit_wall, moved_unoptimal)
        
        # Check if episode is done
        terminated = hit_wall
        truncated = self._is_truncated()
        
        if self.render_mode == "human":
            self.render()

        self.steps = 0 if reward == 1 else self.steps + 1
        
        return observation, reward, terminated, truncated, {}

    def _get_observation(self):
        distances = self.entity.get_manhattan_distances(self.coin, self.CELLS)
        # Convert any infinite values to a large finite number
        distances = [1000 if x == float('inf') else x for x in distances]
        return np.array(distances, dtype=np.float32)

    def _calculate_reward(self, hit_wall, moved_unoptimal):
        reward = 0
        
        # Check if coin collected
        if self.entity.x == self.coin.x and self.entity.y == self.coin.y:
            reward += 1  # Big reward for collecting coin
            # Respawn the coin at a new position
            new_positions = generate_unique_positions(1, self.CELLS, existing_positions=[(self.entity.x, self.entity.y)])
            self.coin.x, self.coin.y = new_positions[0]
        elif hit_wall:
            reward -= 1  # Penalty for hitting wall
        # elif moved_unoptimal:
        #     reward -= 0.10  # Small penalty for suboptimal moves
            
        self.score += reward
        
        return reward

    def _is_truncated(self):
        # Episode ends if max steps reached
        return self.steps >= self.GAME_DECISION_LIMIT

    def render(self):
        if self.render_mode == "human":
            # Calculate display parameters
            cell_pixel_size = max(1, int(self.WINDOW_HEIGHT * 0.8 // self.CELLS * self.scale_factor))
            grid_pixel_size = cell_pixel_size * self.CELLS

            grid_x = (self.WINDOW_WIDTH - grid_pixel_size) // 2 + self.grid_x_offset
            grid_y = (self.WINDOW_HEIGHT - grid_pixel_size) // 2 + self.grid_y_offset
            
            # Get distances for visualization
            distances = self.entity.get_manhattan_distances(self.coin, self.CELLS)
            
            # Create a mock genome object for visualization
            mock_genome = type('obj', (), {'fitness': self.score})

            # Draw scene
            draw_scene(
                self.screen, 
                self.GAME_DECISION_LIMIT - self.steps,
                distances, 
                self.CELLS, 
                [self.entity], 
                {self.entity: mock_genome},
                [self.coin], 
                grid_pixel_size, 
                cell_pixel_size, 
                grid_x, 
                grid_y
            )
            
            pygame.display.flip()
            #pygame.time.wait(100)  # Increased delay to 500ms for better visualization

            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    
    def close(self):
        if self.render_mode == "human":
            pygame.quit()