import argparse

import algorithm_p3
import parse_results
from montecarlo4fms.algorithms import MonteCarloAlgorithms


# Arguments
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

INPUT_FM = "aafms_framework_simple_impl"
REQUIRED_FEATURES_NAMES = ['Glucose']
RUNS = 3
ITERATIONS = [1, 5, 10, 25, 50, 100]
EXPLORATION_WEIGHT = 0.5
MONTECARLO_ALGORITHM = MonteCarloAlgorithms.uct_iterations_maxchild


def main():
    input_fm = INPUT_PATH + INPUT_FM + ".xml"

    output_files = []

    for i in ITERATIONS:
        output_fm = OUTPUT_RESULTS_PATH + INPUT_FM + "_results_" + str(i) + "iters.csv"
        output_files.append(output_fm)
        algorithm_p3.main(input_fm=input_fm, output_results_file=output_fm, required_features_names=REQUIRED_FEATURES_NAMES, montecarlo_algorithm=MONTECARLO_ALGORITHM, runs=RUNS, iterations=i, exploration_weight=EXPLORATION_WEIGHT)

    parse_results(output_files, OUTPUT_SUMMARY_FILE)

if __name__ == '__main__':
    main()

    #parser = argparse.ArgumentParser(description='MonteCarlo experiments.')
    #parser.add_argument('-r', '--runs', dest='runs', type=int, required=True, help='Number of runs.')
    #parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=True, help='Number of iterations for MCTS.')
    #parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, help='Exploration weight constant for UCT MCTS.')
    #parser.add_argument('-fm', '--feature_model',  dest='feature_model', type=str, required=True, help='Input feature model file (.xml) in FeatureIDE format.')
    #args = parser.parse_args()

    # if args.exploration_weight:
    #     exploration_weight = args.exploration_weight
    # else:
    #     exploration_weight = 0.5

    #main(input_fm=args.feature_model, runs=args.run, iterations=args.iterations, exploration_weight=exploration_weight)
