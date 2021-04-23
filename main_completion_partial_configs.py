import sys
import os
import time
import argparse
from functools import reduce

from montecarlo4fms.aafm.models.fm_configuration import FMConfiguration
from montecarlo4fms.aafm.models.feature_model import FeatureModel,  Feature

from montecarlo4fms.aafm.fileformats.featureide_parser import FeatureIDEParser
from montecarlo4fms.aafm.fileformats.cnf_reader import CNFReader
from montecarlo4fms.aafm.utils.aafms_helper import AAFMsHelper
import montecarlo4fms.aafm.utils.fm_utils

from montecarlo4fms.problems.state_as_configuration.models import ValidConfigurationState, ValidMinimumConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms, MonteCarloTreeSearch
from montecarlo4fms.utils import Heatmap
from montecarlo4fms.utils import Heatmap, HeatmapFull
from montecarlo4fms.utils import MCTSStats, MCTSStatsIts


# CONSTANTS
OUTPUT_RESULTS_PATH = "output_results/"
HEATMAP_PATH = OUTPUT_RESULTS_PATH + "heatmaps/"
STATS_PATH = OUTPUT_RESULTS_PATH + "stats/"


def main(algorithm, simulations: int, input_fm: str, input_cnf_model: str=None, initial_config_features: list[str]=[], minimum: bool=False):
    print("Problem: Completion of partial configurations.")
    print("----------------------------------------------")

    print("Setting up the problem...")
    
    print("Creating output folders...")
    if not os.path.exists(OUTPUT_RESULTS_PATH):
        os.makedirs(OUTPUT_RESULTS_PATH)
    if not os.path.exists(HEATMAP_PATH):
        os.makedirs(HEATMAP_PATH)
    if not os.path.exists(STATS_PATH):
        os.makedirs(STATS_PATH)

    base = os.path.basename(input_fm)
    input_fm_name = os.path.splitext(base)[0]

    print(f"Loading feature model: {input_fm} ...")
    fide_parser = FeatureIDEParser(input_fm, no_read_constraints=(input_cnf_model is not None))
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    if input_cnf_model is not None:
        # Read the feature model as CNF model with complex constraints
        cnf_reader = CNFReader(input_cnf_model)
        cnf_model = cnf_reader.transform()
    else:
        cnf_model = None
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)

    print(f"Creating set of actions...")
    actions = TreeActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms_helper, actions)

    print(f"Creating initial state (configuration)...")
    if initial_config_features:
        elements = {}
        for feature in [fm.get_feature_by_name(f) for f in initial_config_features]:
            elements[feature] = True
            for p in fm_utils.select_parent_features(feature):
                elements[p] = True
        initial_config = FMConfiguration(elements=elements)
    else:
        initial_config = FMConfiguration()

    if minimum:
        initial_state = ValidMinimumConfigurationState(configuration=initial_config, data=problem_data)
    else:
        initial_state = ValidConfigurationState(configuration=initial_config, data=problem_data)

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
    while not state.is_terminal():
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
            algorithm.tree = {} 

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

    # Heat for the whole process (not sure about its utility)
    if isinstance(algorithm, MonteCarloTreeSearch):  
        heatmap = HeatmapFull(fm, algorithm.tree, algorithm.Q, algorithm.N)
        heatmap.extract_feature_knowledge()
        heatmap.serialize(HEATMAP_PATH + input_fm_name + "-full.csv")

    print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem: Completion of partial configurations.')
    parser.add_argument('-fm', '--featuremodel', dest='featuremodel', type=str, required=True, help='Input feature model in FeatureIDE format.')
    parser.add_argument('-cnf', '--featuremodel_cnf', dest='featuremodel_cnf', type=str, required=False, help='Input feature model in CNF with FeatureIDE (textual) format (required for complex constraints).')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=False, default=100, help='Number of iterations for MCTS (default 100).')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, default=0.5, help='Exploration weight constant for UCT Algorithm (default 0.5).')
    parser.add_argument('-m', '--method', dest='method', type=str, required=False, default="MCTS", help='Monte Carlo algorithm to be used ("MCTS" for the UCT Algorithm (default), "Greedy" for GreedyMCTS, "flat" for basic Monte Carlo).')
    parser.add_argument('-min', '--minimum', dest='minimum', action='store_true', required=False, help='Minimize number of features in configurations.')
    parser.add_argument('-f', '--features', dest='features', type=str, nargs='*', required=False, help='Initial feature selections (initial configuration).')
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
        algorithm = MonteCarloAlgorithms.greedy_iterations_maxchild(iterations=args.iterations)
    elif args.method == 'flat':
        algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=args.iterations)

    if args.features is None:
        features = []
    else:
        features = args.features

    main(algorithm, args.iterations, args.featuremodel, args.featuremodel_cnf, features, args.minimum)
