import matplotlib.pyplot as plt

def parse_log(file_path):
    total_games = 0
    cumulative_wins = []
    wins = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            if '(game starts)' in line:
                total_games += 1
            if '(game ends with a win!)' in line:
                wins += 1
            cumulative_wins.append(wins)
    
    return cumulative_wins, total_games, wins

def plot_wins_vs_total(cumulative_wins, total_games):
    fig, ax = plt.subplots()
    ax.plot(range(1, total_games + 1), cumulative_wins[:total_games], 'b-', label='Wins')
    ax.set_xlim(0, total_games)
    ax.set_ylim(0, total_games)
    ax.set_xlabel('Total Games')
    ax.set_ylabel('Cumulative Wins')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    major_locator = max(1, total_games // 10)
    minor_locator = max(1, total_games // 20)
    ax.xaxis.set_major_locator(plt.MultipleLocator(major_locator))
    ax.yaxis.set_major_locator(plt.MultipleLocator(major_locator))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(minor_locator))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(minor_locator))
    ax.set_title('Cumulative Wins vs Total Games')
    ax.legend(loc='upper left')
    plt.show()

def calculate_average_rate(wins, total_games):
    return wins / total_games if total_games != 0 else 0

def main():
    log_file_path = 'sim_log.txt'
    cumulative_wins, total_games, wins = parse_log(log_file_path)
    average_rate = calculate_average_rate(wins, total_games)
    print(f"Average rate of winning: {average_rate:.2f} wins per game")
    plot_wins_vs_total(cumulative_wins, total_games)

if __name__ == '__main__':
    main()
