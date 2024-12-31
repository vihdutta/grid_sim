import math
import pygame
from collections import defaultdict

class SimObject():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    # converts cell to pixel coordinates then draws to gui
    def draw(self, screen, cell_pixel_size, grid_x, grid_y):
        pixel_x = grid_x + (self.x - 1) * cell_pixel_size
        pixel_y = grid_y + (self.y - 1) * cell_pixel_size
        pygame.draw.rect(screen, self.color, (pixel_x, pixel_y, cell_pixel_size, cell_pixel_size))

class Entity(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.last_x = x
        self.last_y = y
        self.score = 0
        self.moved_farther_times = 0
        self.revisited_times = 0
        self.locations_visited = defaultdict(int)
        self.same_location_times = 0

    def move(self, direction, distances, CELLS):
        self.last_x = self.x
        self.last_y = self.y

        if direction == 0:  # up
            self.y -= 1
        elif direction == 1:  # down
            self.y += 1
        elif direction == 2:  # left
            self.x -= 1
        elif direction == 3:  # right
            self.x += 1

        hit_wall = self.__constrain_to_bounds(CELLS)
        self.locations_visited[(self.x, self.y)] += 1
        return hit_wall, distances.index(min(distances)) != direction

    def reward_for_closer(self, coin):
        prev_dist = abs(self.last_x - coin.x) + abs(self.last_y - coin.y)
        curr_dist = abs(self.x - coin.x) + abs(self.y - coin.y)
        # self.locations_visited[(self.x, self.y)] > 1
        # if curr_dist >= prev_dist or (self.last_x == self.x and self.last_y == self.y):
        #     return -1

        return 1 if curr_dist == 0 else 0

    def __constrain_to_bounds(self, CELLS):
        constrained = False
        if self.x < 1:
            self.x = 1
            constrained = True
        elif self.x > CELLS:
            self.x = CELLS
            constrained = True

        if self.y < 1:
            self.y = 1
            constrained = True
        elif self.y > CELLS:
            self.y = CELLS
            constrained = True

        return constrained
        
    def coords(self):
        print(f"Current coords: ({self.x}, {self.y})")

class Coin(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)