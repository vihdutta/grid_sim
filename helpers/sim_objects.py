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

    def move(self, direction, CELLS):
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

        self.__constrain_to_bounds(CELLS)
        self.locations_visited[(self.x, self.y)] += 1

    def reward_for_closer(self, coin):
        prev_dist = math.sqrt(math.pow(self.last_x - coin.x, 2) + math.pow(self.last_y - coin.y, 2))
        curr_dist = math.sqrt(math.pow(self.x - coin.x, 2) + math.pow(self.y - coin.y, 2))
        
        moved_farther = curr_dist > prev_dist
        revisited = self.locations_visited[(self.x, self.y)] > 1
        same_location = self.last_x == self.x and self.last_y == self.y
        if (moved_farther or revisited or same_location):
            return self.__punish(moved_farther, revisited, same_location)

        x_diff = abs(self.x - coin.x)
        y_diff = abs(self.y - coin.y)

        if x_diff == 0 and y_diff == 0:
            return 10.0  # coin collected

        manhattan_distance = x_diff + y_diff

        if x_diff == y_diff:  # diagonal neighbors get less points (as you can't get to target diagonally)
            return 1 / (manhattan_distance + 1)
        else:  # direct neighbors
            return 1 / manhattan_distance
        
    def __punish(self, moved_farther, revisited, same_location):
        punishment = 0
        if moved_farther:
            #print("MOVED FARTHER")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("MOVED FARTHER\n")
            self.moved_farther_times += 1
            punishment += self.moved_farther_times * 2
        if revisited:
            #print("REVISITED")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("REVISITED\n")
            self.revisited_times += 1
            punishment += self.revisited_times * 2
        if same_location:
            #print("DIDN'T MOVE")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("DIDN'T MOVE\n")
            self.same_location_times += 1
            punishment += self.same_location_times * 2
        return -punishment

    def __constrain_to_bounds(self, CELLS):
        self.x = max(1, min(self.x, CELLS-1))
        self.y = max(1, min(self.y, CELLS-1))
        
    def coords(self):
        print(f"Current coords: ({self.x}, {self.y})")

class Coin(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)