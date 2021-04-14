import argparse
import csv
import statistics
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 14})
import numpy as np
from scipy.interpolate import make_interp_spline


def read_file(filepath: 'str') -> dict:
    data = {}
    n = 0
    with open(filepath, newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',', skipinitialspace=True)
        for row in reader:
            n += 1
            data[n] = row
    return data


def get_xy_values(data: dict, x_field, x_type, y_field, y_type, filter_field, function_filter):
    """Return the x and y values filtered by the given field and value."""
    x = [x_type(data[row][x_field]) for row in data if function_filter(data[row][filter_field])]
    y = [y_type(data[row][y_field]) for row in data if function_filter(data[row][filter_field])]
    print(x,y)
    return x, y


def plot(fig, x_values, y_values, title="", x_label="", y_label="", line_label="", color='blue', style='-'):
    fig.set_title(title)
    fig.set_xlabel(x_label)
    fig.set_ylabel(y_label)

    colors = [color if v > 0 else 'red' for v in y_values]

    frequency = {}
    for f in y_values:
        frequency[f] = frequency.get(f, 0) + 1
    sizes = [frequency[f] for f in y_values]

    fig.scatter(x_values, y_values, s=sizes, c=colors)

    # # Median
    try:
        x_group = list(set(x_values))
        x_group.sort()
        y_group = []
        for x in x_group:
            y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
            y_group.append(statistics.median(y))

        # Smooth the line (suaviza la recta)
        model=make_interp_spline(x_group, y_group)
        xs=np.linspace(min(x_group), max(x_group), 500)
        ys=model(xs)
        fig.plot(xs, ys, label=line_label, color=color, linestyle=style)
    except:
        fig.plot(x_group, y_group, label=line_label, color=color, linestyle=style)

    fig.legend(loc="best")


def plot_rewards(fig, algorithms, data):
    for a in algorithms:
        x, y = get_xy_values(data, 'StoppingCondition', int, 'Reward', int, 'Algorithm', lambda x : a in x)
        plot(fig, x, y, 'Rewards', 'Iterations', 'R(s)', a, color=algorithms[a][0], style=algorithms[a][1])

def plot_features(fig, algorithms, data):
    for a in algorithms:
        x, y = get_xy_values(data, 'StoppingCondition', int, 'Features', int, 'Algorithm', lambda x : a in x)
        plot(fig, x, y, 'Number of features\n(Number of decisions)\n(Number of algorithm steps)', 'Simulations', 'Feature decisions', a, color=algorithms[a][0], style=algorithms[a][1])

def plot_times(fig, algorithms, data):
    for a in algorithms:
        x, y = get_xy_values(data, 'StoppingCondition', int, 'ExecutionTime', float, 'Algorithm', lambda x : a in x)
        plot(fig, x, y, 'Execution time\n(seconds)', 'Simulations', 'Time (s)', a, color=algorithms[a][0], style=algorithms[a][1])

def plot_nodes_evaluated(fig, algorithms, data):
    for a in algorithms:
        x, y = get_xy_values(data, 'StoppingCondition', int, '#TotalIterationsExecuted', int, 'Algorithm', lambda x : a in x)
        plot(fig, x, y, 'Total iterations executed\n(Total nodes evaluated)', 'Simulations', 'Nodes', a, color=algorithms[a][0], style=algorithms[a][1])

def plot_algorithm_steps(fig, algorithms, data):
    for a in algorithms:
        x, y = get_xy_values(data, 'StoppingCondition', int, 'AlgorithmSteps', int, 'Algorithm', lambda x : a in x)
        plot(fig, x, y, 'Number of algorithm steps\n(Number of decisions)', 'Simulations', 'Steps', a, color=algorithms[a][0], style=algorithms[a][1])

def plot_features_probabilities(fig, algorithms, data):
    for a in algorithms:
        x_values = [int(data[row]['Features']) for row in data if a in (data[row]['Algorithm'])]
        valid_configs = [data[row]['ValidConfiguration'] for row in data if a in (data[row]['Algorithm'])]

        x_group = list(set(x_values))
        x_group.sort()
        y_group = []
        for x in x_group:
            y_total = [valid_configs[i] for i in range(len(valid_configs)) if x_values[i] == x]
            y = [v for v in y_total if v == 'True']
            y_group.append(len(y) / len(y_total) * 100)

        fig.set_title("Probability of finding a valid configuration with N features")
        fig.set_xlabel("N Features")
        fig.set_ylabel("%")

        try:
            raise Exception
#            raise Exception
            # Smooth the line (suaviza la recta)
            # model=make_interp_spline(x_group, y_group)
            # xs=np.linspace(min(x_group), max(x_group), 500)
            # ys=model(xs)
            # fig.plot(xs, ys, label=a, color=algorithms[a])
        except:
            fig.plot(x_group, y_group, label=a, color=algorithms[a][0], ls=algorithms[a][1])

        fig.legend(loc="best")

def main(filepath):
    data = read_file(filepath)

    algorithms = {
                  'Greedy MCTS': ['green', 'dashed'],
                 # 'Random Strategy': 'green',
                #  'UCT MCTS Rnd Exp': 'green',
                  'flat Monte Carlo': ['red', 'dotted'],
                  'UCT Algorithm': ['blue', 'solid']}
                #  'Random Strategy': 'orange'}

    fig, axs = plt.subplots(2,2)
    plot_rewards(axs[0,0], algorithms, data)
    plot_features(axs[0,1], algorithms, data)
   # plot_nodes_evaluated(axs[1,0], algorithms, data)
    plot_times(axs[1,1], algorithms, data)
    #plot_features_probabilities(axs[0,0], algorithms, data)

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse the result file from MonteCarlo framework.')
    parser.add_argument('-f', '--file', dest='file', required=True, help='Input files path with the results.')
    args = parser.parse_args()

    main(args.file)
