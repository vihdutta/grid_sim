import pygame
SPEED = 5

class Entity:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
        self.size = size
        self.color = color

    def move(self, direction):
        self.last_x = self.x
        self.last_y = self.y

        if direction == 0:  # up
            self.y -= SPEED
        elif direction == 1:  # down
            self.y += SPEED
        elif direction == 2:  # left
            self.x -= SPEED
        elif direction == 3:  # right
            self.x += SPEED

    def constrain_to_bounds(self, WIDTH, HEIGHT):
        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def check_collision(self, coin):
        return pygame.Rect(self.x, self.y, self.size, self.size).colliderect(
            pygame.Rect(coin.x, coin.y, coin.size, coin.size))
    
class Coin:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size