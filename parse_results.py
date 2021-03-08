import argparse
import csv
import statistics
import matplotlib.pyplot as plt
from typing import List

OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

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

    n_valid_configs = len([r for r in data if data['Valid Config']])
    n_invalid_configs = len([r for r in data if not data['Valid Config']])

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

def draw_scatter_plot_features(data: dict):
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

    plt.scatter(x, y, s=sizes, c=colors)
    #plt.colorbar();  # show color scale
    plt.show()

def parse_results(filespath: List['str'], output_file: str = OUTPUT_SUMMARY_FILE):
    data = read_files(filespath)

    iterations = {int(data[n]['Iterations']) for n in data}
    data_iterations = {}
    for i in iterations:
        data_iterations[i] = get_data_for_iterations(data, i)

    with open(output_file, 'w+') as file:
        file.write("Iterations, Runs, Valid Configs, Invalid configs, Features min, Features max, Features median, Features mean, Features std, Rewards min, Rewards max, Rewards median, Rewards mean, Rewards std, Nodes min, Nodes max, Nodes median, Nodes mean, Nodes std, Times min, Times max, Times median, Times mean, Times std\n")

        for it in data_iterations.keys():
            stats = data_iterations[it]['stats']
            f_stats = stats['Features']
            r_stats = stats['Rewards']
            n_stats = stats['Nodes']
            t_stats = stats['Times']
            file.write(f"{it}, {stats['Runs']}, {stats['n_valid_configs']}, {stats['n_invalid_configs']}, {f_stats['min']}, {f_stats['max']}, {f_stats['median']}, {f_stats['mean']}, {f_stats['std']}, {r_stats['min']}, {r_stats['max']}, {r_stats['median']}, {r_stats['mean']}, {r_stats['std']}, {n_stats['min']}, {n_stats['max']}, {n_stats['median']}, {n_stats['mean']}, {n_stats['std']}, {t_stats['min']}, {t_stats['max']}, {t_stats['median']}, {t_stats['mean']}, {t_stats['std']}\n")

    draw_scatter_plot_features(data_iterations)

    # # Scatter plot
    # iterations = [int(data[r]['Iterations']) for r in data]
    # frequency = {}
    # for f in features:
    #     frequency[f] = frequency.get(f, 0) + 1
    # x = iterations
    # y = features
    # colors = ['blue' if data[r]['Valid Config'] == 'True' else 'red' for r in data]
    # sizes = [frequency[f] for f in features]
    #
    # plt.scatter(x, y, s=sizes, c=colors)
    # #plt.colorbar();  # show color scale
    # plt.show()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse results file from MonteCarlo framework.')
    parser.add_argument('--files', dest='filespath', required=True, nargs='+', help='Input files path with the results.')
    args = parser.parse_args()

    parse_results(args.filespath)
