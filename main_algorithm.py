import argparse
import cProfile
import os.path

from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.problems import Problem1s


# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

# PARAMETERS
input_fm_name = "aafms_framework_simple_impl"
iterations = 1
exploration_weight = 0.5
initial_config = []
montecarlo_algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
input_fm = INPUT_PATH + input_fm_name + ".xml"


def main(run: int):
    problem = Problem1s(input_fm, initial_config, montecarlo_algorithm)
    print(f"Initial state: {problem.get_initial_state()}")
    problem.solve()
    state = problem.get_result_state()
    print(f"Result state: {state}")

    if run > 0:
        write_stats(run, problem.get_stats())

def write_stats(run, stats):
    headers = list(stats.keys())
    headers.sort()

    if not os.path.exists(OUTPUT_RESULTS_FILE):
         head = 'Run,' + ','.join(headers) + '\n'
         with open(OUTPUT_RESULTS_FILE, 'a+') as file:
             file.write(head)

    values = [f'"{stats[h]}"' if type(stats[h]) == str else str(stats[h]) for h in headers]
    values = str(run) + ',' + ','.join(values) + '\n'
    with open(OUTPUT_RESULTS_FILE, 'a+') as file:
        file.write(values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MonteCarlo evaluation.')
    parser.add_argument('-r', '--run', dest='run', type=int, required=False, help='Execute the program indicating the id of the current run.')
    parser.add_argument('-p', '--profile', dest='profile', action='store_true', required=False, help='Execute the program with cProfile.')
    args = parser.parse_args()

    if args.profile:
        cProfile.run("main(run=0)")
    elif args.run:
        main(run=args.run)
    else:
        parser.print_help()
