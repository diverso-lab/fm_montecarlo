import time
import os
import sys
import argparse
from functools import reduce

from montecarlo4fms.aafm.models.fm_configuration import FMConfiguration
from montecarlo4fms.aafm.models.feature_model import FeatureModel,  Feature
from montecarlo4fms.aafm.fileformats.featureide_parser import FeatureIDEParser
from montecarlo4fms.aafm.fileformats.uvl_writter import UVLWritter
from montecarlo4fms.aafm.fileformats.cnf_reader import CNFReader
from montecarlo4fms.aafm.utils.aafms_helper import AAFMsHelper

from montecarlo4fms.problems.reverse_engineering.models import FMState
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.utils import MCTSStatsRE


# CONSTANTS
OUTPUT_RESULTS_PATH = "output_results/"
HEATMAP_PATH = OUTPUT_RESULTS_PATH + "heatmaps/"
STATS_PATH = OUTPUT_RESULTS_PATH + "stats/"
GENERATED_FMS_PATH = OUTPUT_RESULTS_PATH + "generated_fms/"


def main(algorithm, simulations: int, input_fm: str, input_cnf_model: str=None):
    print("Problem: Reverse engineering of feature models.")
    print("-----------------------------------------------")

    base = os.path.basename(input_fm)
    input_fm_name = os.path.splitext(base)[0]

    print("Setting up the problem...")

    print("Creating output folders...")
    if not os.path.exists(HEATMAP_PATH):
        os.makedirs(HEATMAP_PATH)
    if not os.path.exists(STATS_PATH):
        os.makedirs(STATS_PATH)
    if not os.path.exists(GENERATED_FMS_PATH):
        os.makedirs(GENERATED_FMS_PATH)

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm, no_read_constraints=(input_cnf_model is not None))
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    if input_cnf_model is not None:
        # Read the feature model as CNF model with complex constraints
        cnf_reader = CNFReader(input_cnf_model)
        cnf_model = cnf_reader.transform()
    else:
        cnf_model = None
    
    # Get configurations
    print("Generating configurations of the feature model...")
    aafms_helper = AAFMsHelper(fm, cnf_model)
    configurations = aafms_helper.get_configurations()
    print(f"#Configurations: {len(configurations)}")

    print(f"Creating initial state (empty feature model)...")
    initial_state = FMState(FeatureModel(None), configurations)

    print("Problem setted up.")

    print(f"Running algorithm {str(algorithm)}...")
    
    # Stats
    mcts_stats_re = MCTSStatsRE(STATS_PATH + input_fm_name + "-ReverseEngineering.log")

    n = 0
    state = initial_state
    total_time_start = time.time()
    while not state.is_terminal():
        print(f"State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")
        start_time = time.time()
        new_state = algorithm.run(state)
        end_time = time.time()
        
        mcts_stats_re.add_step(n, algorithm.tree, algorithm.Q, algorithm.N, state, new_state, simulations, end_time-start_time)
        state = new_state
        n += 1

    total_time_end = time.time()
    print("Algorithm finished.")
    print(f"Final State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")

    # Get configurations
    path = GENERATED_FMS_PATH + state.feature_model.root.name + "." + UVLWritter.get_destination_extension()
    print(f"Serializing generated feature model in UVL format in {path}")
    uvl_writter = UVLWritter(path=path, source_model=state.feature_model)
    uvl_writter.transform()

    # Get configurations
    print("Generating configurations of the extracted feature model...")
    aafms_helper = AAFMsHelper(state.feature_model)
    new_configurations = aafms_helper.get_configurations()
    
    print("Results:")
    print(f"#Features: {len(state.feature_model.get_features())} -> {[str(f) for f in state.feature_model.get_features()]}")
    print(f"#Configurations: {len(new_configurations)}")

    relaxed_value = reduce(lambda count, c: count + (aafms_helper.is_valid_configuration(c)), configurations, 0)
    deficit_value = reduce(lambda count, c: count + (c not in new_configurations), configurations, 0)
    surplus_value = reduce(lambda count, c: count + (c not in configurations), new_configurations, 0)
    print(f"Input configurations captured (Relaxed objective function): {relaxed_value}")
    print(f"Deficit of configurations: {deficit_value}")
    print(f"Irrelevant configurations: {surplus_value}")
    print(f"Mininal difference (MinDiff) objective function (deficit_value + surplus_value): {deficit_value} + {surplus_value} = {deficit_value+surplus_value}")
    print(f"Final objective function (Relaxed - MinDiff): {relaxed_value - (deficit_value+surplus_value)}")
    print(f"Execution time: {total_time_end-total_time_start}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem: Reverse engineering of feature models.')
    parser.add_argument('-fm', '--featuremodel', dest='featuremodel', type=str, required=True, help='Input feature model in FeatureIDE format.')
    parser.add_argument('-cnf', '--featuremodel_cnf', dest='featuremodel_cnf', type=str, required=False, help='Input feature model in CNF with FeatureIDE (textual) format (required for complex constraints).')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=False, default=100, help='Number of iterations for MCTS (default 100).')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, default=0.5, help='Exploration weight constant for UCT Algorithm (default 0.5).')
    parser.add_argument('-m', '--method', dest='method', type=str, required=False, default="MCTS", help='Monte Carlo algorithm to be used ("MCTS" for the UCT Algorithm (default), "Greedy" for GreedyMCTS, "flat" for basic Monte Carlo).')
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
        algorithm = MonteCarloAlgorithms.greedy_iterations_maxchild(iterations=args.iterations, exploration_weight=0)
    elif args.method == 'flat':
        algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=args.iterations)

    main(algorithm, args.iterations, args.featuremodel, args.featuremodel_cnf)