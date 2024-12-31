import neat.nn.feed_forward
import pygame
import math
import neat
import os
import pickle
from helpers.sim_objects import Entity, Coin
from helpers.draw import draw_scene, generate_unique_positions
from testing import run_test_ai

# set up variables
RENDER = False
DELAY = 1000
CELLS = 5
GAME_DECISION_LIMIT = 2 * (CELLS-1) # lowest amount of steps to get from any point a to b

ENTITIES = 1
COINS = 1

ENTITY_COLOR = (50, 175, 50)
COIN_COLOR = (255, 230, 10)

location_movements = {0:"up", 1:"down", 2:"left", 3:"right"}

def get_distance_to_closest_wall(entity, CELLS):
    distance_up = entity.y
    distance_down = CELLS - entity.y - 1
    distance_left = entity.x
    distance_right = CELLS - entity.x - 1

    return min(distance_up, distance_down, distance_left, distance_right)

def get_manhattan_distances(entity, coin, CELLS):
    def valid_position(x, y, CELLS):
        return 1 <= x <= CELLS and 1 <= y <= CELLS
    
    # Calculate up
    if valid_position(entity.x, entity.y - 1, CELLS):
        up = abs(entity.x - coin.x) + abs(entity.y - 1 - coin.y)
    else:
        up = float('inf')
    
    # Calculate down
    if valid_position(entity.x, entity.y + 1, CELLS):
        down = abs(entity.x - coin.x) + abs(entity.y + 1 - coin.y)
    else:
        down = float('inf')
    
    # Calculate left
    if valid_position(entity.x - 1, entity.y, CELLS):
        left = abs(entity.x - 1 - coin.x) + abs(entity.y - coin.y)
    else:
        left = float('inf')
    
    # Calculate right
    if valid_position(entity.x + 1, entity.y, CELLS):
        right = abs(entity.x + 1 - coin.x) + abs(entity.y - coin.y)
    else:
        right = float('inf')
    
    return up, down, left, right


def train_ai(genome, config):
    with open("sim_log.txt", "a") as log_file:
        log_file.write("(game starts)\n")
    entity_positions = generate_unique_positions(ENTITIES, CELLS)
    coin_positions = generate_unique_positions(COINS, CELLS, existing_positions=entity_positions)
    entities = [Entity(x, y, ENTITY_COLOR) for x, y in entity_positions]
    coins = [Coin(x, y, COIN_COLOR) for x, y in coin_positions]
    entity_map = {entities[0]: genome}

    if RENDER:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Game Optimization Simulation")
        WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    scale_factor = 1.0
    dragging = False
    grid_x_offset = 0
    grid_y_offset = 0
    last_mouse_pos = (0, 0)
    
    running = True
    decisions = 0
    while running:
        net = neat.nn.FeedForwardNetwork.create(genome, config)

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
        distances = get_manhattan_distances(entities[0], coins[0], CELLS)
        if RENDER:
            cell_pixel_size = max(1, int(WINDOW_HEIGHT * 0.8 // CELLS * scale_factor))
            grid_pixel_size = cell_pixel_size * CELLS

            grid_x = (WINDOW_WIDTH - grid_pixel_size) // 2 + grid_x_offset
            grid_y = (WINDOW_HEIGHT - grid_pixel_size) // 2 + grid_y_offset

            draw_scene(screen, distances, CELLS, entities, entity_map, coins, grid_pixel_size, cell_pixel_size, grid_x, grid_y)
            pygame.display.flip()

        output1 = net.activate((
            distances[0],
            distances[1],
            distances[2],
            distances[3],
        ))

        if RENDER:
            pygame.time.wait(DELAY)

        bad_move = entities[0].move(output1.index(max(output1[:4])), distances, CELLS)
        with open("sim_log.txt", "a") as log_file:
            log_file.write(f"Entity 1 position: ({entities[0].x}, {entities[0].y}), score: {entities[0].score}\n")
            log_file.write(f"Coin position: ({coins[0].x}, {coins[0].y})\n")

        scored = False
        for entity in entities:
            closer_score = entity.reward_for_closer(coins[0])
            entity.score += closer_score
            genome.fitness += closer_score

            if (entity.x == coins[0].x and entity.y == coins[0].y):
                scored = True

        if scored:
            #print("SCORED")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("SCORED\n")
                log_file.write("(game ends with a win!)\n")
            break

        elif bad_move:
            entities[0].score -= 1
            genome.fitness -= 1
            #print("BAD MOVE")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("BAD MOVE\n")
                log_file.write("(game ends)\n")
            break

        elif decisions > GAME_DECISION_LIMIT:
            #print("GAME_DECISION_LIMIT REACHED")
            with open("sim_log.txt", "a") as log_file:
                log_file.write("GAME_DECISION_LIMIT REACHED\n")
                log_file.write("(game ends)\n")
            break

        decisions += 1
    if RENDER:
        pygame.quit()

def eval_genomes(genomes, config):
    for (_, genome) in (genomes):
        genome.fitness = 0
        train_ai(genome, config)

def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-899')
    p = neat.Population(config)
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(1))
    winner = p.run(eval_genomes, 10)

    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

def test_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner.fitness = 0
    train_ai(winner, config) # placeholder until i have a test ai

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)
    # for i in range(1000):
    #     print(f"Test {i+1}")
    #     test_ai(config)