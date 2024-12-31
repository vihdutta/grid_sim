import neat.nn.feed_forward
import pygame
import neat
import os
import pickle
from helpers.sim_objects import Entity, Coin
from helpers.draw import draw_scene, generate_unique_positions

# set up variables
RENDER = True
DELAY = 1000
CELLS = 5
GAME_DECISION_LIMIT = 2 * (CELLS-1) # lowest amount of steps to get from any point a to b
ENTITIES = 1
COINS = 1
ENTITY_COLOR = (50, 175, 50)
COIN_COLOR = (255, 230, 10)

location_movements = {0:"up", 1:"down", 2:"left", 3:"right"}

def train_ai(genome, config):
    entity_positions = generate_unique_positions(ENTITIES, CELLS)
    coin_positions = generate_unique_positions(COINS, CELLS, existing_positions=entity_positions)
    entities = [Entity(x, y, ENTITY_COLOR) for x, y in entity_positions]
    coins = [Coin(x, y, COIN_COLOR) for x, y in coin_positions]
    entity_map = {entities[0]: genome} # just using 1 entity for now

    if RENDER:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Game Optimization Simulation")
        WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    scale_factor = 1.0
    grid_x_offset = 0
    grid_y_offset = 0
    
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

        # ensures the grid_size is an exact multiple
        # of cell_size so the cells aren't cut off
        distances = entities[0].get_manhattan_distances(coins[0], CELLS)
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

        hit_wall, moved_unoptimal_direction = entities[0].move(output1.index(max(output1[:4])), distances, CELLS)
        #print(f"Entity moved {location_movements[output1.index(max(output1[:4]))]}")

        closer_score = entities[0].reward_for_closer(coins[0])
        entities[0].score += closer_score
        genome.fitness += closer_score

        if closer_score == 1:
            #print("SCORE!")
            break
        elif hit_wall or moved_unoptimal_direction:
            entities[0].score -= 1
            genome.fitness -= 1
            #print("HIT WALL OR MOVED UNOPTIMAL DIRECTION")
            break
        elif decisions > GAME_DECISION_LIMIT:
            #print("DECISION LIMIT REACHED")
            break

        decisions += 1
    if RENDER:
        pygame.quit()

def eval_genomes(genomes, config):
    for (_, genome) in (genomes):
        genome.fitness = 0
        train_ai(genome, config)

def run_neat(config):
    p = neat.Population(config)
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 100)

    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

def test_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner.fitness = 0
    train_ai(winner, config) # placeholder until i have a proper test ai

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