import pygame
import random

GRID_COLOR = (100, 100, 100)

def draw_grid(screen, grid_pixel_size, cell_pixel_size):
    for x in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, grid_pixel_size))
    for y in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (grid_pixel_size, y))


def draw_scene(screen, steps_left, distances, CELLS, entities, entity_map, coins, grid_pixel_size, cell_pixel_size, grid_x, grid_y):
    screen.fill((255, 255, 255))
    
    grid_surface = pygame.Surface((grid_pixel_size, grid_pixel_size))
    grid_surface.fill(GRID_COLOR)
    draw_grid(grid_surface, grid_pixel_size, cell_pixel_size)
    screen.blit(grid_surface, (grid_x, grid_y))

    font = pygame.font.SysFont("Futura", 30)

    grid_size_label = font.render(f"{CELLS}x{CELLS} grid", 1, (0, 0, 0))
    entity_fitness_label = font.render(f"entity 1 fitness: {round(entity_map[entities[0]].fitness, 2)}", 1, (0, 0, 0))
    entity_coordinates = font.render(f"entity 1 position: ({entities[0].x}, {entities[0].y})", 1, (0, 0, 0))
    entity_steps_left = font.render(f"entity 1 steps left: ({steps_left})", 1, (0, 0, 0))

    screen.blit(grid_size_label, (10, 10))
    screen.blit(entity_fitness_label, (10, 30))
    screen.blit(entity_coordinates, (10, 50))
    screen.blit(entity_steps_left, (150, 10))

    for entity in entities:
        entity.draw(screen, cell_pixel_size, grid_x, grid_y)
    for coin in coins:
        coin.draw(screen, cell_pixel_size, grid_x, grid_y)
    
    draw_manhattan_distances(screen, entities[0], coins[0], distances, CELLS, cell_pixel_size, grid_x, grid_y)

def draw_manhattan_distances(screen, entity, coin, distances, CELLS, cell_pixel_size, grid_x, grid_y):
    font = pygame.font.SysFont("Arial", 20)
    up, down, left, right, up_left, up_right, down_left, down_right = distances[:8]
    
    directions = {
        "up": (entity.x, entity.y - 1, up),
        "down": (entity.x, entity.y + 1, down),
        "left": (entity.x - 1, entity.y, left),
        "right": (entity.x + 1, entity.y, right),
        "up_left": (entity.x - 1, entity.y - 1, up_left),
        "up_right": (entity.x + 1, entity.y - 1, up_right),
        "down_left": (entity.x - 1, entity.y + 1, down_left),
        "down_right": (entity.x + 1, entity.y + 1, down_right),
    }

    
    for direction, (x, y, distance) in directions.items():
        color = (0, 255, 0) if distance == 1 else (255, 0, 0)

        pixel_x = grid_x + (x - 1) * cell_pixel_size
        pixel_y = grid_y + (y - 1) * cell_pixel_size
        pygame.draw.rect(screen, color, (pixel_x, pixel_y, cell_pixel_size, cell_pixel_size), 2)
        
        distance_text = font.render(str(distance), True, (0, 0, 0))
        screen.blit(distance_text, (pixel_x + cell_pixel_size // 2 - distance_text.get_width() // 2, pixel_y + cell_pixel_size // 2 - distance_text.get_height() // 2))

def generate_unique_positions(count, cells, existing_positions=set()):
    positions = set()
    while len(positions) < count:
        x, y = random.randint(1, cells), random.randint(1, cells)
        if (x, y) not in existing_positions:
            positions.add((x, y))
    return list(positions)