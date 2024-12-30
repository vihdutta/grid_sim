import math
import pygame

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
        self.locations_visited = set()

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

        self.locations_visited.add((self.x, self.y))
        self.__constrain_to_bounds(CELLS)


    def reward_for_closer(self, coin):
        prev_dist = math.sqrt(math.pow(self.last_x - coin.x, 2) + math.pow(self.last_y - coin.y, 2))
        curr_dist = math.sqrt(math.pow(self.x - coin.x, 2) + math.pow(self.y - coin.y, 2))
        
        moved_farther = curr_dist > prev_dist
        revisited = (self.x, self.y) in self.locations_visited
        if (moved_farther or revisited):
            self.__punish(moved_farther, revisited)

        x_diff = abs(self.x - coin.x)
        y_diff = abs(self.y - coin.y)

        if x_diff == 0 and y_diff == 0:
            return 5.0  # coin collected

        manhattan_distance = x_diff + y_diff

        if x_diff == y_diff:  # diagonal neighbors get less points (as you can't get to target diagonally)
            return 1 / (manhattan_distance + 1)
        else:  # direct neighbors
            return 1 / manhattan_distance
        
    def __punish(self, moved_farther, revisited):
        punishment = 0
        if moved_farther:
            self.moved_farther_times += 1
            punishment += self.moved_farther_times * 1.5
        if revisited:
            self.revisited_times += 1
            punishment += self.revisited_times * 1.5
        return punishment


    def __constrain_to_bounds(self, CELLS):
        self.x = max(1, min(self.x, CELLS-1))
        self.y = max(1, min(self.y, CELLS-1))
    
class Coin(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

    
