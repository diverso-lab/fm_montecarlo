import os
import argparse
import csv
import statistics
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from typing import List

from experiments_config import OUTPUT_SUMMARY_FILE, OUTPUT_RESULTS_PATH


def read_files(filespath: List['str']) -> dict:
    data = {}
    n = 0
    for filepath in filespath:
        with open(filepath, newline='') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',', skipinitialspace=True)
            for row in reader:
                n += 1
                data[n] = row
    return data

def calc_stats(values: list) -> dict:
    stats = {}
    stats['min'] = min(values)
    stats['max'] = max(values)
    stats['median'] = statistics.median(values)
    stats['mean'] = statistics.mean(values)
    stats['std'] = statistics.stdev(values)
    return stats

def get_stats(data: dict) -> dict:
    stats = {}
    stats['Runs'] = len(data['Time'])

    n_valid_configs = len([r for r in data if bool(data['Valid Config'])])
    n_invalid_configs = len([r for r in data if not bool(data['Valid Config'])])

    stats['n_valid_configs'] = n_valid_configs
    stats['n_invalid_configs'] = n_invalid_configs

    features = data['Features in Config']
    stats['Features'] = calc_stats(features)
    stats['Rewards'] = calc_stats(data['Reward'])
    stats['Nodes'] = calc_stats(data['Nodes'])
    stats['Times'] = calc_stats(data['Time'])


    return stats

def get_data_for_iterations(data: dict, iter: int) -> dict:
    new_data = {}
    new_data['Iterations'] = [int(data[n]['Iterations']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Features in Config'] = [int(data[n]['Features in Config']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Valid Config'] = [bool(data[n]['Valid Config']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Reward'] = [float(data[n]['Reward']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Time'] = [float(data[n]['Time']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Nodes'] = [int(data[n]['Nodes']) for n in data if int(data[n]['Iterations']) == iter]
    new_data['Configuration'] = [data[n]['Configuration'] for n in data if int(data[n]['Iterations']) == iter]

    new_data['stats'] = get_stats(new_data)

    return new_data

def draw_scatter_plot_features(fig, data: dict):
    fig.set_title("Min. nº features")
    fig.set_xlabel("Iterations")
    fig.set_ylabel("#Features")

    x = []
    y = []
    colors = []
    sizes = []
    for iter in data:
        x += data[iter]['Iterations']
        y += data[iter]['Features in Config']
        colors += ['blue' if valid else 'red' for valid in data[iter]['Valid Config']]

    frequency = {}
    for f in y:
        frequency[f] = frequency.get(f, 0) + 1
    sizes = [frequency[f] for f in y]

    fig.scatter(x, y, s=sizes, c=colors)

    # Median
    x1 = list(data.keys())
    x1.sort()
    y1 = [data[iter]['stats']['Features']['median'] for iter in x1]

    # Suaviza la recta
    model=make_interp_spline(x1, y1)
    xs=np.linspace(min(x1), max(x1), 500)
    ys=model(xs)

    fig.plot(xs, ys)

def draw_scatter_plot_nodes(fig, data: dict):
    fig.set_title("Nodes explored")
    fig.set_xlabel("Iterations")
    fig.set_ylabel("Nodes")

    x = []
    y = []
    colors = []
    sizes = []
    for iter in data:
        x += data[iter]['Iterations']
        y += data[iter]['Nodes']
        #colors += ['blue' if valid else 'red' for valid in data[iter]['Valid Config']]

    frequency = {}
    for f in y:
        frequency[f] = frequency.get(f, 0) + 1
    sizes = [frequency[f] for f in y]

    fig.scatter(x, y, s=sizes)

    # Median
    x1 = list(data.keys())
    x1.sort()
    y1 = [data[iter]['stats']['Nodes']['median'] for iter in x1]

    # Suaviza la recta
    model=make_interp_spline(x1, y1)
    xs=np.linspace(min(x1), max(x1), 500)
    ys=model(xs)

    fig.plot(xs, ys)


def draw_scatter_plot_rewards(fig, data: dict):
    fig.set_title("Rewards")
    fig.set_xlabel("Iterations")
    fig.set_ylabel("R(s)")

    x = []
    y = []
    colors = []
    sizes = []
    for iter in data:
        x += data[iter]['Iterations']
        y += data[iter]['Reward']
        colors += ['blue' if v > 0 else 'red' for v in data[iter]['Reward']]

    frequency = {}
    for f in y:
        frequency[f] = frequency.get(f, 0) + 1
    sizes = [frequency[f] for f in y]

    fig.scatter(x, y, s=sizes, c=colors)

    # Median
    x1 = list(data.keys())
    x1.sort()
    y1 = [data[iter]['stats']['Rewards']['median'] for iter in x1]

    # Suaviza la recta
    model=make_interp_spline(x1, y1)
    xs=np.linspace(min(x1), max(x1), 500)
    ys=model(xs)

    fig.plot(xs, ys)


def draw_scatter_plot_times(fig, data: dict):
    fig.set_title("Execution time")
    fig.set_xlabel("Iterations")
    fig.set_ylabel("Time (s)")

    x = []
    y = []
    colors = []
    sizes = []
    for iter in data:
        x += data[iter]['Iterations']
        y += data[iter]['Time']

    frequency = {}
    for f in y:
        frequency[f] = frequency.get(f, 0) + 1
    sizes = [frequency[f] for f in y]

    fig.scatter(x, y, s=sizes)

    # Median
    x1 = list(data.keys())
    x1.sort()
    y1 = [data[iter]['stats']['Times']['median'] for iter in x1]

    # Suaviza la recta
    model=make_interp_spline(x1, y1)
    xs=np.linspace(min(x1), max(x1), 500)
    ys=model(xs)

    fig.plot(xs, ys)

def plot_results(data):
    fig, axs = plt.subplots(2, 2)
    draw_scatter_plot_rewards(axs[0,0], data)
    draw_scatter_plot_features(axs[1,0], data)
    draw_scatter_plot_nodes(axs[0,1], data)
    draw_scatter_plot_times(axs[1,1], data)
    fig.tight_layout()
    plt.show()

def parse_results(filespath: List['str'], output_file: str = OUTPUT_SUMMARY_FILE):
    data = read_files(filespath)

    iterations = {int(data[n]['Iterations']) for n in data}
    data_iterations = {}
    for i in iterations:
        data_iterations[i] = get_data_for_iterations(data, i)

    with open(output_file, 'w+') as file:
        file.write("Iterations, Runs, Valid Configs, Invalid configs, Features min, Features max, Features median, Features mean, Features std, Rewards min, Rewards max, Rewards median, Rewards mean, Rewards std, Nodes min, Nodes max, Nodes median, Nodes mean, Nodes std, Times min, Times max, Times median, Times mean, Times std\n")

        its = list(data_iterations.keys())
        its.sort()
        for it in its:
            stats = data_iterations[it]['stats']
            f_stats = stats['Features']
            r_stats = stats['Rewards']
            n_stats = stats['Nodes']
            t_stats = stats['Times']
            file.write(f"{it}, {stats['Runs']}, {stats['n_valid_configs']}, {stats['n_invalid_configs']}, {f_stats['min']}, {f_stats['max']}, {f_stats['median']}, {f_stats['mean']}, {f_stats['std']}, {r_stats['min']}, {r_stats['max']}, {r_stats['median']}, {r_stats['mean']}, {r_stats['std']}, {n_stats['min']}, {n_stats['max']}, {n_stats['median']}, {n_stats['mean']}, {n_stats['std']}, {t_stats['min']}, {t_stats['max']}, {t_stats['median']}, {t_stats['mean']}, {t_stats['std']}\n")


    plot_results(data_iterations)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Parse results file from MonteCarlo framework.')
    # parser.add_argument('--files', dest='filespath', required=True, nargs='+', help='Input files path with the results.')
    # args = parser.parse_args()
    #filespath = args.filespath
    parser = argparse.ArgumentParser(description='Parse results file from MonteCarlo framework.')
    parser.add_argument('-p', '--prefix', dest='prefix', required=True, help='Prefix of the input files path with the results.')
    args = parser.parse_args()

    files = [OUTPUT_RESULTS_PATH + f for f in os.listdir(OUTPUT_RESULTS_PATH) if f.startswith(args.prefix)]

    parse_results(files)
