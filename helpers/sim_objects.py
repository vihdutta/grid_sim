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
        moved_unoptimal_direction = distances.index(min(distances)) != direction
        return hit_wall, moved_unoptimal_direction

    def reward_for_closer(self, coin):
        curr_dist = abs(self.x - coin.x) + abs(self.y - coin.y)
        return 1 if curr_dist == 0 else 0
    
    def get_manhattan_distances(self, coin, CELLS):
        def valid_position(x, y, CELLS):
            return 1 <= x <= CELLS and 1 <= y <= CELLS
        
        # calculate up
        if valid_position(self.x, self.y - 1, CELLS):
            up = abs(self.x - coin.x) + abs(self.y - 1 - coin.y)
        else:
            up = float('inf')
        
        # calculate down
        if valid_position(self.x, self.y + 1, CELLS):
            down = abs(self.x - coin.x) + abs(self.y + 1 - coin.y)
        else:
            down = float('inf')
        
        # calculate left
        if valid_position(self.x - 1, self.y, CELLS):
            left = abs(self.x - 1 - coin.x) + abs(self.y - coin.y)
        else:
            left = float('inf')
        
        # calculate right
        if valid_position(self.x + 1, self.y, CELLS):
            right = abs(self.x + 1 - coin.x) + abs(self.y - coin.y)
        else:
            right = float('inf')
        
        return up, down, left, right

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

class Coin(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)