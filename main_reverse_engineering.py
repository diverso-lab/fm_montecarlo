import sys
import os
import argparse
import random
from functools import reduce
from pathlib import Path


from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from famapy.metamodels.bdd_metamodel.operations import BDDProductDistributionBF
from famapy.metamodels.fm_metamodel.transformations.uvl_writter import UVLWriter
from famapy.metamodels.fm_metamodel.models import FeatureModel

from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, TimeStoppingCondition, NoneStoppingCondition
from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import Algorithm, AlgorithmFactory
from montecarlo_framework.problems.fm_based_analyses import FMState, ReverseEngineeringProblem
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.models.feature_model import fm_utils
from montecarlo_framework.utils import utils
from montecarlo_framework.utils.algorithm_logger import RESULTS


PRECISION = 4
GENERATED_FMS_PATH = "results/generated_fms/"

def main(input_model: str, 
         algorithm: Algorithm, 
         stats_name: str):
    print(f'Loading {input_model} feature model...')

    # Load feature model
    feature_model = FeatureIDEReader(input_model).transform()
    
    # Initialize metamodels (FM, SAT, BDD)
    fm = FM(feature_model)  # FM is a helper class

    # Initial state and problem
    configurations = fm.get_configurations()
    initial_state = FMState(FeatureModel(None), configurations)
    problem = ReverseEngineeringProblem(initial_state)
    
    print(f'Initial state: {initial_state}')

    # Run algorithm runs times
    solutions = []
    print(f'Running 1 execution of algorithm "{algorithm.get_name()}" with {stopping_condition} as stopping condition...')
    algorithm.initialize()
    solution = algorithm.run(problem)  # Run the algorithm
    print('Search finished.')

    state = solution.terminal_node.state
    print(f"Final State: {state}")

    # Get configurations
    path = GENERATED_FMS_PATH + state.feature_model.root.name + "." + UVLWriter.get_destination_extension()
    Path(GENERATED_FMS_PATH).mkdir(parents=True, exist_ok=True)
    print(f"Serializing generated feature model in UVL format in {path}")
    uvl_writter = UVLWriter(path=path, source_model=state.feature_model)
    uvl_writter.transform()

    # Get configurations
    print("Generating configurations of the extracted feature model...")
    aafms_helper = FM(state.feature_model)
    new_configurations = aafms_helper.get_configurations()
    
    print("Results:")
    print(f"#Features: {len(state.feature_model.get_features())}")
    print(f"#Configurations: {len(new_configurations)}")
    print(f"#Expected configurations: {len(configurations)}")

    relaxed_value = reduce(lambda count, c: count + (aafms_helper.is_valid_configuration(c)), configurations, 0)
    deficit_value = reduce(lambda count, c: count + (c not in new_configurations), configurations, 0)
    surplus_value = reduce(lambda count, c: count + (c not in configurations), new_configurations, 0)
    print(f"Input configurations captured (Relaxed objective function): {relaxed_value}")
    print(f"Deficit of configurations: {deficit_value}")
    print(f"Irrelevant configurations: {surplus_value}")
    print(f"Mininal difference (MinDiff) objective function (deficit_value + surplus_value): {deficit_value} + {surplus_value} = {deficit_value+surplus_value}")
    print(f"Final objective function (Relaxed - MinDiff): {relaxed_value - (deficit_value+surplus_value)}")

    #print(f"Execution time: {total_time_end-total_time_start}")

    print('Finished.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem: Reverse engineering of feature models.')
    parser.add_argument('-s', '--seed', dest='seed', type=int, required=False, default=None, help='Seed to initialize the random generator (default None), setup only for replication purposes.')
    parser.add_argument('-fm', '--featuremodel', dest='feature_model', type=str, required=True, help='Input feature model in FeatureIDE format.')
    parser.add_argument('-alg', '--algorithm', dest='algorithm', type=str, required=False, default="mcts", help='Algorithm to be used ("mcts" for the UCT Algorithm (default), "greedy" for GreedyMCTS, "flat" for basic Monte Carlo, "random" for Random strategy, "astar" for A*).')
    parser.add_argument('-sc', '--stopping_condition', dest='stopping_condition', type=str, required=False, default=None, help='Stopping condition for the algorithm: "iter" for iterations, or "time". (default: the algorithm runs until a solution is found).')
    parser.add_argument('-sv', '--stopping_value', dest='stopping_value', type=int, required=False, default=None, help='Value for the stopping condition: number of iterations for "iter" or seconds for "time".')
    parser.add_argument('-mc_sc', '--mc_stopping_condition', dest='mc_stopping_condition', type=str, required=False, default='sim', help='Stopping condition for each decision in MonteCarlo algorithms: "sim" for simulations (default) or "time".')
    parser.add_argument('-mc_sv', '--mc_stopping_value', dest='mc_stopping_value', type=int, required=False, default=None, help='Stopping value for each decision in Monte Carlo algorithms: number of simulations for "sim" (default 100) or seconds for "time" (default 1 s).')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, default=0.5, help='Exploration weight constant for UCT Algorithm (default 0.5).')
    parser.add_argument('-p', '--parallel', dest='parallel', action='store_true', required=False, help='User parallel version of the algorithm if available (algorithm supported: "flat").')
    args = parser.parse_args()

    if args.seed is not None:
        # Initialize the random module
        print(f'Initialized random module with seed {args.seed}')
        random.seed(args.seed)

    # Stopping condition for the algorithm
    stopping_condition = NoneStoppingCondition()
    if args.stopping_condition is not None and args.stopping_condition.lower() not in ['iter', 'time']:
        print(f"ERROR: invalid stopping condition for algorithm.")
        parser.print_help()
        sys.exit()
    elif args.stopping_condition is not None:
        if args.stopping_value is None:
            print(f"ERROR: a stopping value must be specified for the stopping condition.")    
            parser.print_help()
            sys.exit()
        elif args.stopping_value <= 0:
            print(f"ERROR: the stopping value (iterations or seconds) must be positive.")
            parser.print_help()
            sys.exit()
        else:
            if args.stopping_condition.lower() == 'iter':
                stopping_condition = IterationsStoppingCondition(iterations=args.stopping_value)
            elif args.stopping_condition.lower() == 'time':
                stopping_condition = TimeStoppingCondition(seconds=args.stopping_value)
        
    # Stopping condition for Monte Carlo decisions
    mc_stopping_condition = None
    if args.mc_stopping_condition.lower() not in ['sim', 'time']:
        print(f"ERROR: invalid stopping condition for Monte Carlo decisions.")
        parser.print_help()
        sys.exit()
    else:
        if args.mc_stopping_value is not None and args.mc_stopping_value <= 0:
            print(f"ERROR: the stopping value (simulations or seconds) for Monte Carlo decisions must be positive.")
            parser.print_help()
            sys.exit()
        else:
            if args.mc_stopping_condition.lower() == 'sim':
                mc_stopping_value = 100 if args.mc_stopping_value is None else args.mc_stopping_value
                mc_stopping_condition = IterationsStoppingCondition(iterations=mc_stopping_value)
            elif args.mc_stopping_condition.lower() == 'time':
                mc_stopping_value = 1 if args.mc_stopping_value is None else args.mc_stopping_value
                mc_stopping_condition = TimeStoppingCondition(seconds=mc_stopping_value)

    if args.exploration_weight < 0 or args.exploration_weight > 1:
        print(f"ERROR: the exploration weight constant must be in range [0,1].")
        parser.print_help()
        sys.exit()

    algorithm_name = args.algorithm.lower()
    if algorithm_name not in ['mcts', 'greedy', 'flat', 'random', 'astar']:
        print(f"ERROR: Algorithm not recognized.")
        parser.print_help()
        sys.exit()

    if algorithm_name == 'random':
        algorithm = AlgorithmFactory.random_strategy(stopping_condition=stopping_condition)
        stats_name = 'RandomStrategy'
    elif algorithm_name == 'astar':
        algorithm = AlgorithmFactory.a_star_search(stopping_condition=stopping_condition)
        stats_name = 'AStarSearch'
    elif algorithm_name == 'mcts':
        algorithm = AlgorithmFactory.uct_mcts_maxchild(stopping_condition=stopping_condition, mc_stopping_condition=mc_stopping_condition, exploration_weight=args.exploration_weight)
        stats_name = 'UCTMCTS'
    elif algorithm_name == 'greedy':
        algorithm = AlgorithmFactory.greedy_mcts_maxchild(stopping_condition=stopping_condition, mc_stopping_condition=mc_stopping_condition)
        stats_name = 'GreedyMCTS'
    elif algorithm_name == 'flat':
        if args.parallel:
            algorithm = AlgorithmFactory.parallel_flat_montecarlo_maxchild(stopping_condition=stopping_condition, mc_stopping_condition=mc_stopping_condition)
            stats_name = 'ParallelFlatMonteCarlo'
        else:
            algorithm = AlgorithmFactory.flat_montecarlo_maxchild(stopping_condition=stopping_condition, mc_stopping_condition=mc_stopping_condition)
            stats_name = 'FlatMonteCarlo'
    else:
        print(f"ERROR: Algorithm not recognized.")
        parser.print_help()
        sys.exit()

    main(input_model=args.feature_model, 
         algorithm=algorithm,
         stats_name=stats_name)