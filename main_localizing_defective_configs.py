import sys
import time
import argparse
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper, fm_utils

from montecarlo4fms.models import VPState
from montecarlo4fms.problems.state_as_configuration.models import DefectiveSimulatedConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms, MonteCarloTreeSearch
from montecarlo4fms.utils import Heatmap
from montecarlo4fms.utils import MCTSStatsIts, MCTSStats


# CONSTANTS
INPUT_PATH = "evaluation/aafmsPythonFramework/"
OUTPUT_RESULTS_PATH = "output_results/"
HEATMAP_PATH = OUTPUT_RESULTS_PATH + "heatmaps/"
STATS_PATH = OUTPUT_RESULTS_PATH + "stats/"


def main(algorithm, simulations: int, input_fm_name: str, input_fm_cnf_name: str):
    print("Problem 1 (simulated): Finding defective configurations.")
    print("--------------------------------------------------------")

    print("Setting up the problem...")
    input_fm = INPUT_PATH + input_fm_name + ".xml"

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

     # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(INPUT_PATH + input_fm_cnf_name + ".txt")
    cnf_model = cnf_reader.transform()
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
   
    print(f"Creating set of actions...")
    actions = TreeActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms_helper, actions)

    print(f"Creating initial state (empty configuration)...")
    initial_config = FMConfiguration()
    initial_state = DefectiveSimulatedConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")
    print("Problem setted up.")

    print(f"Running algorithm {str(algorithm)}...")

    # Stats
    mcts_stats = MCTSStats()
    mcts_stats_its = MCTSStatsIts()

    n = 0
    total_evaluations = 0
    state = initial_state
    total_time_start = time.time()
    while state.reward() <= 0 and state.get_actions():
        print(f"Input state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")
        time_start = time.time()
        new_state = algorithm.run(state)
        time_end = time.time()

        if isinstance(algorithm, MonteCarloTreeSearch):  
            # Heat map (only for MCTS)
            heatmap = Heatmap(fm, algorithm.tree, algorithm.Q, algorithm.N, state)
            heatmap.extract_feature_knowledge()
            heatmap.serialize(HEATMAP_PATH + input_fm_name + "-step" + str(n) + ".csv")
        else:
            algorithm.tree = None 

        # Stats
        mcts_stats.add_step(n, algorithm.tree, state, new_state, simulations, algorithm.n_evaluations, algorithm.n_positive_evaluations, time_end-time_start)
        total_evaluations += algorithm.n_evaluations
        algorithm.n_evaluations = 0

        state = new_state
        n += 1
        
    total_time_end = time.time()
    print("Algorithm finished.")
    print(f"Final state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")

    # Stats
    print("Serializing results...")
    mcts_stats.serialize(STATS_PATH + input_fm_name + '-steps.csv')
    mcts_stats_its.add_step(str(algorithm), n, algorithm.tree, simulations, total_evaluations, algorithm.n_positive_evaluations, total_time_end-total_time_start)
    mcts_stats_its.serialize(STATS_PATH + input_fm_name + '-summary.csv')

    print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem 1: Finding defective configurations in the AAFMs Python Framework feature model.')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=False, default=100, help='Number of iterations for MCTS (default 100).')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, default=0.5, help='Exploration weight constant for UCT Algorithm (default 0.5).')
    #parser.add_argument('-s', '--sample', dest='sample', type=int, required=False, default=1, help='Maximum number of defective configurations to be searched (default 1).')
    parser.add_argument('-m', '--method', dest='method', type=str, required=False, default="MCTS", help='Monte Carlo algorithm to be used ("MCTS" for the UCT Algorithm (default), "Greedy" for GreedyMCTS, "flat" for basic Monte Carlo).')
    parser.add_argument('-e', '--excerpt', dest='excerpt', action='store_true', required=False, help='Running the problem with the excerpt running example instead of the complete feature model.')
    args = parser.parse_args()

    if args.exploration_weight < 0 or args.exploration_weight > 1:
        print(f"ERROR: the exploration weight constant must be in range [0,1].")
        parser.print_help()
        sys.exit()

    if args.iterations <= 0:
        print(f"ERROR: the number of iterations/simulations must be positive.")
        parser.print_help()
        sys.exit()

    if args.method not in ['MCTS', 'Greedy', 'flat']:
        print(f"ERROR: Algorithm not recognized.")
        parser.print_help()
        sys.exit()

    if args.method == 'MCTS':
        algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=args.iterations, exploration_weight=args.exploration_weight)
    elif args.method == 'Greedy':
        algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=args.iterations, exploration_weight=0)
    elif args.method == 'flat':
        algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=args.iterations)

    if args.excerpt:
        input_fm_name = "model_simple_paper_excerpt"
        input_fm_cnf_name = "model_simple_paper_excerpt-cnf"
    else:
        input_fm_name = "model_paper"
        input_fm_cnf_name = "model_paper-cnf"

    main(algorithm, args.iterations, input_fm_name, input_fm_cnf_name)
