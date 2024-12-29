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

    def move(self, direction):
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

    def constrain_to_bounds(self, cells):
        self.x = max(0, min(self.x, cells-1))
        self.y = max(0, min(self.y, cells-1))

    def check_collision(self, cell_size, coin):
        return pygame.Rect(self.x, self.y, cell_size, cell_size).colliderect(
            pygame.Rect(coin.x, coin.y, cell_size, cell_size))
    
class Coin(SimObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

    
