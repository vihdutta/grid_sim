import gymnasium as gym
from gymnasium.envs.registration import register
from game_env import GameEnv
from agent import Agent
import argparse

# Register the custom environment
register(
    id='GameEnv-v0',
    entry_point='game_env:GameEnv',
)

def main():
    parser = argparse.ArgumentParser(description='Train or test DQN agent.')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'],
                      help='train: train the model, test: run the trained model')
    parser.add_argument('--episodes', type=int, default=10,
                      help='number of episodes to test (only used in test mode)')
    args = parser.parse_args()

    # Create the agent
    agent = Agent(hyperparameter_set='game-dqn')
    
    if args.mode == 'train':
        # Train the agent
        print("Starting training...")
        agent.run(is_training=True)
    else:
        # Test the trained agent
        print(f"\nTesting trained agent for {args.episodes} episodes...")
        for episode in range(args.episodes):
            print(f"\nEpisode {episode + 1}")
            agent.run(is_training=False, render=True)

if __name__ == "__main__":
    main()