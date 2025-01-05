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
        # Move the entity based on the direction
        if direction == 0:  # up
            self.y -= 1
        elif direction == 1:  # down
            self.y += 1
        elif direction == 2:  # left
            self.x -= 1
        elif direction == 3:  # right
            self.x += 1
        elif direction == 4:  # up-left
            self.y -= 1
            self.x -= 1
        elif direction == 5:  # up-right
            self.y -= 1
            self.x += 1
        elif direction == 6:  # down-left
            self.y += 1
            self.x -= 1
        elif direction == 7:  # down-right
            self.y += 1
            self.x += 1
        

        hit_wall = self.__constrain_to_bounds(CELLS)
        moved_unoptimal_direction = direction not in [i for i, value in enumerate(distances[:4]) if value == min(distances[:4])]
        return hit_wall, moved_unoptimal_direction
    
    def get_manhattan_distances(self, coin, CELLS):
        # check if coin is straight in any direction
        up = 1 if self.x == coin.x and self.y > coin.y else 0
        down = 1 if self.x == coin.x and self.y < coin.y else 0
        left = 1 if self.y == coin.y and self.x > coin.x else 0
        right = 1 if self.y == coin.y and self.x < coin.x else 0
        up_left = 1 if self.x > coin.x and self.y > coin.y else 0
        up_right = 1 if self.x < coin.x and self.y > coin.y else 0
        down_left = 1 if self.x > coin.x and self.y < coin.y else 0
        down_right = 1 if self.x < coin.x and self.y < coin.y else 0
        
        # distances to nearest wall (more like next to wall: true or false)
        dist_up_wall = 1 if self.y - 1 == 0 else 0
        dist_down_wall = 1 if CELLS - self.y == 0 else 0
        dist_left_wall = 1 if self.x - 1 == 0 else 0
        dist_right_wall = 1 if CELLS - self.x else 0
        
        return (up, down, left, right, up_left, up_right, down_left, down_right, dist_up_wall, dist_down_wall, dist_left_wall, dist_right_wall)

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