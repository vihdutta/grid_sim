import neat.nn.feed_forward
import pygame
import random
import math
import neat
import os
import pickle
from helpers.sim_objects import Entity, Coin
from testing import run_test_ai

# set up variables
RENDER = True
DELAY = 100
CELLS = 5
GAME_DECISION_LIMIT = 2 * (CELLS-1) # lowest amount of steps to get from any point a to b

ENTITIES = 2
COINS = 1

ENTITY_COLOR = (50, 175, 50)
COIN_COLOR = (255, 230, 10)

def generate_unique_positions(count, cells, existing_positions=set()):
    positions = set()
    while len(positions) < count:
        x, y = random.randint(1, cells), random.randint(1, cells)
        if (x, y) not in existing_positions:
            positions.add((x, y))
    return list(positions)

# draws grid lines
def draw_grid(screen, grid_pixel_size, cell_pixel_size):
    for x in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, grid_pixel_size))
    for y in range(0, grid_pixel_size, cell_pixel_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (grid_pixel_size, y))

def draw_scene(screen, entities, entity_map, coins, grid_pixel_size, cell_pixel_size, grid_x, grid_y):
    screen.fill((255, 255, 255))
    
    grid_surface = pygame.Surface((grid_pixel_size, grid_pixel_size))
    draw_grid(grid_surface, grid_pixel_size, cell_pixel_size)
    screen.blit(grid_surface, (grid_x, grid_y))

    font = pygame.font.SysFont("Futura", 30)
    grid_size_label = font.render(f"{CELLS}x{CELLS} grid", 1, (0, 0, 0))
    genome1_fitness_label = font.render(f"entity 1 fitness: {round(entity_map[entities[0]].fitness, 2)}", 1, (0, 0, 0))
    genome2_fitness_label = font.render(f"entity 2 fitness: {round(entity_map[entities[1]].fitness, 2)}", 1, (0, 0, 0))
    screen.blit(grid_size_label, (10, 10))
    screen.blit(genome1_fitness_label, (10, 30))
    screen.blit(genome2_fitness_label, (10, 50))

    for entity in entities:
        entity.draw(screen, cell_pixel_size, grid_x, grid_y)
    for coin in coins:
        coin.draw(screen, cell_pixel_size, grid_x, grid_y)

def train_ai(genome1, genome2, config):
    with open("sim_log.txt", "a") as log_file:
        log_file.write("(game starts)\n")
    entity_positions = generate_unique_positions(ENTITIES, CELLS)
    coin_positions = generate_unique_positions(COINS, CELLS, existing_positions=entity_positions)
    entities = [Entity(x, y, ENTITY_COLOR) for x, y in entity_positions]
    coins = [Coin(x, y, COIN_COLOR) for x, y in coin_positions]
    entity_map = {entities[0]: genome1, entities[1]: genome2}

    if RENDER:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Game Optimization Simulation")
        WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    scale_factor = 1.0
    dragging = False
    grid_x_offset = 0
    grid_y_offset = 0
    last_mouse_pos = (0, 0)
    
    running = True
    decisions = 0
    while running:
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        if RENDER:
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

        # ensures the grid_size is an exact multiple
        # of cell_size so the cells aren't cut off
        if RENDER:
            cell_pixel_size = max(1, int(WINDOW_HEIGHT * 0.8 // CELLS * scale_factor))
            grid_pixel_size = cell_pixel_size * CELLS

            grid_x = (WINDOW_WIDTH - grid_pixel_size) // 2 + grid_x_offset
            grid_y = (WINDOW_HEIGHT - grid_pixel_size) // 2 + grid_y_offset

            draw_scene(screen, entities, entity_map, coins, grid_pixel_size, cell_pixel_size, grid_x, grid_y)
            pygame.display.flip()

        output1 = net1.activate((
            entities[0].x, entities[0].y,
            coins[0].x, coins[0].y,
            math.sqrt((entities[0].x - coins[0].x) ** 2 + (entities[0].y - coins[0].y) ** 2)
        ))

        output2 = net2.activate((
            entities[1].x, entities[1].y,
            coins[0].x, coins[0].y,
            math.sqrt((entities[1].x - coins[0].x) ** 2 + (entities[1].y - coins[0].y) ** 2)
        ))

        entities[0].move(output1.index(max(output1)), CELLS)
        entities[1].move(output2.index(max(output2)), CELLS)
        if RENDER:
            pygame.time.wait(DELAY)

        with open("sim_log.txt", "a") as log_file:
            log_file.write(f"Entity 1 position: ({entities[0].x}, {entities[0].y}), score: {entities[0].score}\n")
            log_file.write(f"Entity 2 position: ({entities[1].x}, {entities[1].y}), score: {entities[1].score}\n")
            log_file.write(f"Coin position: ({coins[0].x}, {coins[0].y})\n")

        scored = False
        less_than_0 = False
        for entity in entities:
            closer_score = entity.reward_for_closer(coins[0])
            entity.score += closer_score
            entity_map[entity].fitness += closer_score

            if (entity.x == coins[0].x and entity.y == coins[0].y):
                scored = True
            if entity.score < 0:
                less_than_0 = True

        if scored:
            #print("SCORED")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("SCORED\n")
                log_file.write("(game ends)\n")
            break
        if less_than_0:
            #print("LESS THAN 0")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("LESS THAN 0\n")
                log_file.write("(game ends)\n")
            break

        if decisions > GAME_DECISION_LIMIT:
            #print("GAME_DECISION_LIMIT REACHED")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("GAME_DECISION_LIMIT REACHED\n")
                log_file.write("(game ends)\n")
            break

        decisions += 1
    if RENDER:
        pygame.quit()

def eval_genomes(genomes, config):
    for i, (_, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for (_, genome2) in genomes[i+1:]:
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness

            train_ai(genome1, genome2, config)

def run_neat(config):
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint3-296')
    #p = neat.Population(config)
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))
    winner = p.run(eval_genomes, 2)

    with open(f"best.pickle", "wb") as f:
        pickle.dump(winner, f)

def test_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner.fitness = 0
    run_test_ai(winner, config)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    #run_neat(config)
    for i in range(10000):
        print(f"Test {i+1}")
        test_ai(config)