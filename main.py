import pygame
import random
import math
import neat
import os
from helpers.sim_objects import Entity, Coin

pygame.init()
pygame.font.init()
pygame.display.set_caption("Game Optimization Simulation")

# set up variables
CELLS = 5

ENTITIES = 2
COINS = 1

ENTITY_COLOR = (50, 175, 50)
COIN_COLOR = (255, 230, 10)

entities = [Entity(random.randint(1, CELLS), random.randint(1, CELLS), ENTITY_COLOR) for _ in range(ENTITIES)]
coins = [Coin(random.randint(1, CELLS), random.randint(1, CELLS), COIN_COLOR) for _ in range(COINS)]

# draws grid lines
def draw_grid(screen, grid_pixel_size, cell_pixel_size):
    for x in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, grid_pixel_size))
    for y in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (grid_pixel_size, y))

def draw_scene(screen, grid_pixel_size, cell_pixel_size, grid_x, grid_y):
    screen.fill((255, 255, 255))
    
    grid_surface = pygame.Surface((grid_pixel_size, grid_pixel_size))
    draw_grid(grid_surface, grid_pixel_size, cell_pixel_size)
    screen.blit(grid_surface, (grid_x, grid_y))

    # font = pygame.font.SysFont("Futura", 30)
    # label = font.render(f"{CELLS}x{CELLS} grid", 1, (0, 0, 0))
    # screen.blit(label, (10, 10))

    for entity in entities:
        entity.draw(screen, cell_pixel_size, grid_x, grid_y)
    for coin in coins:
        coin.draw(screen, cell_pixel_size, grid_x, grid_y)

def train_ai(entities, genome1, genome2, config):
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    scale_factor = 1.0
    dragging = False
    grid_x_offset = 0
    grid_y_offset = 0
    last_mouse_pos = (0, 0)
    
    running = True
    while running:
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            if event.type == pygame.MOUSEWHEEL:
                scale_factor += event.y / 10
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                    grid_x_offset += dx
                    grid_y_offset += dy
                    last_mouse_pos = event.pos            

            output1 = net1.activate((
                entities[1].x,
                entities[1].y,
                math.sqrt(math.pow(entities[0].x - coins[0].x, 2) + math.pow(entities[0].y - coins[0].y, 2))
            ))

            output2 = net2.activate((
                entities[1].x,
                entities[1].y,
                math.sqrt(math.pow(entities[1].x - coins[0].x, 2) + math.pow(entities[1].y - coins[0].y, 2))
            ))

            entities[0].move(max(output1), CELLS)
            entities[1].move(max(output2), CELLS)

        # ensures the grid_size is an exact multiple
        # of cell_size so the cells aren't cut off
        cell_pixel_size = max(1, int(WINDOW_HEIGHT * 0.8 // CELLS * scale_factor))
        grid_pixel_size = cell_pixel_size * CELLS

        grid_x = (WINDOW_WIDTH - grid_pixel_size) // 2 + grid_x_offset
        grid_y = (WINDOW_HEIGHT - grid_pixel_size) // 2 + grid_y_offset

        draw_scene(screen, grid_pixel_size, cell_pixel_size, grid_x, grid_y)
        pygame.display.flip()

        for entity in entities:
            if entity.score > 0:
                calculate_fitness(genome1, genome2)
                running = False
    pygame.quit()

def calculate_fitness(genome1, genome2):
    pass

def eval_genomes(genomes, config):
    for i, (_, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for (_, genome2) in genomes[i+1:]:
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness

            train_ai(entities, genome1, genome2, config)

def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-x')
    p = neat.Population(config)
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    run_neat(config)