import pygame
from entity import Entity

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game Optimization Simulation")

# set up variables
CELLS = 5

# draws grid lines
def draw_grid(screen, grid_size, cell_size):
    for x in range(0, grid_size, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, grid_size))
    for y in range(0, grid_size, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (grid_size, y))

# main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

    # ensures the grid_size is an exact multiple
    # of cell_size so the cells aren't cut off
    grid_pixel_size = WINDOW_HEIGHT * 0.8
    cell_pixel_size = int(grid_pixel_size // CELLS)
    grid_pixel_size = cell_pixel_size*CELLS

    # center the grid
    grid_x = (WINDOW_WIDTH - grid_pixel_size) // 2
    grid_y = (WINDOW_HEIGHT - grid_pixel_size) // 2

    screen.fill((255, 255, 255))

    grid_surface = pygame.Surface((grid_pixel_size, grid_pixel_size))
    draw_grid(grid_surface, grid_pixel_size, cell_pixel_size)
    screen.blit(grid_surface, (grid_x, grid_y))

    pygame.display.flip()

pygame.quit()
