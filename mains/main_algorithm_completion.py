import argparse
import cProfile
import os.path

from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.algorithms import RandomStrategy
from montecarlo4fms.algorithms.stopping_conditions import IterationsStoppingCondition
from montecarlo4fms.problems import Problem3

# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

# PARAMETERS
input_fm_name = "aafms_framework_simple_impl"
RUNS = 30
ITERATIONS = [1]+[x*10 for x in range(1,10+1)]
ITERATIONS_PROFILE = 100
exploration_weight = 0.5
initial_config = ['Glucose']
#montecarlo_algorithm = MonteCarloAlgorithms.uct_iterations_maxchild_random_expansion(iterations=iterations, exploration_weight=exploration_weight)
#montecarlo_algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=iterations)
#montecarlo_algorithm = RandomStrategy(IterationsStoppingCondition(iterations=iterations))
input_fm = INPUT_PATH + input_fm_name + ".xml"


def main(run: int, iterations: int):
    montecarlo_algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    problem = Problem3(input_fm, initial_config, montecarlo_algorithm)
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

    #stats['Algorithm'] = "UCT MTCS [AlgSC=valid&errors]"
    values = [f'"{stats[h]}"' if type(stats[h]) == str else str(stats[h]) for h in headers]
    values = str(run) + ',' + ','.join(values) + '\n'
    with open(OUTPUT_RESULTS_FILE, 'a+') as file:
        file.write(values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MonteCarlo evaluation.')
    #parser.add_argument('-r', '--run', dest='run', type=int, required=False, help='Execute the program indicating the id of the current run.')
    parser.add_argument('-p', '--profile', dest='profile', action='store_true', required=False, help='Execute the program with cProfile.')
    args = parser.parse_args()

    if args.profile:
        cProfile.run("main(run=0,iterations=ITERATIONS_PROFILE)")
    else:
        for it in ITERATIONS:
            for run in range(1, RUNS+1):
                main(run=run, iterations=it)
