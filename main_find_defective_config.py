import sys
import os
import argparse
import random
from collections import defaultdict 

from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from famapy.metamodels.bdd_metamodel.operations import BDDProductDistributionBF

from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, TimeStoppingCondition, NoneStoppingCondition
from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import Algorithm, AlgorithmFactory
from montecarlo_framework.problems.configuration_based_analyses import DefectiveConfigurationState, FindingDefectiveConfigProblem, JHipsterDefectiveConfigurationState, JHipsterFindingDefectiveConfigProblem
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.models.feature_model import fm_utils
from montecarlo_framework.utils import utils
from montecarlo_framework.utils.algorithm_logger import RESULTS
from montecarlo_framework.problems.configuration_based_analyses import jhipster_utils


PRECISION = 4


def main(runs: int, 
         input_model: str, 
         algorithm: Algorithm, 
         features_names: list[str], 
         use_core_features: bool,
         stats_name: str):
    print(f'Loading {input_model} feature model...')

    # Load feature model
    if input_model == 'aafm-excerpt':
        input_fm = 'models/aafms_framework_excerpt-namesAdapted.xml'
    elif input_model == 'aafm':
        input_fm = 'models/aafms_framework-namesAdapted.xml'
    elif input_model == 'jhipster':
        input_fm = 'models/jHipster.xml'

    feature_model = FeatureIDEReader(input_fm).transform()
    
    # Initialize metamodels (FM, SAT, BDD)
    fm = FM(feature_model)  # FM is a helper class

    # Initial state and problem
    if use_core_features:
        core_features = fm_utils.get_core_features(feature_model)
    else:
        core_features = []
    configuration = fm_utils.initialize_configuration(feature_model, features_names)
    selected_features = list(set(core_features + [f for f in configuration.elements]))
    unselected_features = list(set(feature_model.get_features()) - set(selected_features))
    selected_variables = [fm.sat_model.variables[f.name] for f in selected_features]
    unselected_variables = [-fm.sat_model.variables[f.name] for f in unselected_features]
    initial_config = FMConfiguration(fm, selected_features, unselected_features, selected_variables, unselected_variables)

    if input_model in ['aafm-excerpt', 'affm']:
        initial_state = DefectiveConfigurationState(initial_config)
        problem = FindingDefectiveConfigProblem(initial_state)
    elif input_model == 'jhipster':
        initial_state = JHipsterDefectiveConfigurationState(initial_config)
        problem = JHipsterFindingDefectiveConfigProblem(initial_state)
        initial_state.set_problem(problem)

         # Read the jhipster configurations as a dict of FMConfiguration -> bool (failure)
        jhipster_configurations = jhipster_utils.read_jHipster_feature_model_configurations()
        problem.jhipster_configurations = jhipster_configurations
        problem.sample = defaultdict(bool)

    print(f'Initial state: {initial_state}')

    # Run algorithm runs times
    solutions = []
    print(f'Running {runs} executions of algorithm "{algorithm.get_name()}" with {stopping_condition} as stopping condition...')
    print('  |run: ', end='', flush=True)
    for r in range(runs):
        algorithm.initialize()
        print(f'{r+1} ', end='', flush=True)
        solutions.append(algorithm.run(problem))  # Run the algorithm
    print()
    print('Search finished.')

    # Get valid solutions:
    valid_solutions = [s for s in solutions if s.terminal_node.state.is_valid()]
    print(f'Valid solutions: {len(valid_solutions)}/{runs} ({round(len(valid_solutions)/runs * 100, 2)}%)')

    # Get the best solution
    if valid_solutions:
        best_solution = max(valid_solutions, key=lambda s: s.terminal_node.state.reward())

        # Print out the best solution
        print(f'One of the solutions with defects found from {runs} executions:')
        for step, node in enumerate(best_solution.get_solution_path()):
            state, action = node
            print(f' |Step {step}: {str(action)} -> {str(state)}')
        print(f'#Features: {len(best_solution.terminal_node.state.configuration.get_selected_features())}')
        print(f'#Decisions: {len(best_solution.get_solution_path()) - 1}')
        print(f'#Defects: {best_solution.terminal_node.state.reward()}')

        # Get the solutions with defects
        solutions_with_defects = [sol.terminal_node.state for sol in valid_solutions if sol.terminal_node.state.reward() > 0]
        print(f'#Solutions with defects (sols with defects/sols): {len(solutions_with_defects)}/{len(valid_solutions)} ({round(len(solutions_with_defects)/len(valid_solutions) * 100, 2)}%)')
    
        # Best solutions without duplicates (with different terminal nodes)
        best_solution_states = set(solutions_with_defects)
        best_solutions_duplicates = [sol for sol in solutions if sol.terminal_node.state in best_solution_states]
        best_solutions = []
        states = set()
        for sol in best_solutions_duplicates:
            state = sol.terminal_node.state
            if state in best_solution_states and state not in states:
                best_solutions.append(sol)
                states.add(state)

        print(f'#Different solutions with defects (diffs/sols): {len(best_solutions)}/{len(valid_solutions)} ({round(len(best_solutions)/len(valid_solutions) * 100, 2)}%)')

    # Get statistics
    stats = AlgorithmStats.get_stats(stats_name)
    execution_times = [s[AlgorithmStats.TIME_STR] for s in stats]
    memory_consumptions = [s[AlgorithmStats.MEMORY_STR] for s in stats]
    features_in_solutions = [len(s[AlgorithmStats.SOLUTION_STR].configuration.get_selected_features()) for s in stats]
    decisions = [s[AlgorithmStats.STEPS_STR] for s in stats]

    # Get statistics for best solutions
    # best_stats = []
    # for sol in best_solutions:
    #     best_stats.extend(AlgorithmStats.get_best_solutions_stats(sol))
    # execution_times = [stats[AlgorithmStats.TIME_STR] for stats in best_stats]
    print('Statistics summary:')
    print('-------------------')
    nof_features = utils.get_summary_stastistics(features_in_solutions, PRECISION)
    print('#Features:')
    print(f' |median: {nof_features[utils.MEDIAN]}')
    print(f' |mean: {nof_features[utils.MEAN]}')
    print(f' |stdev: {nof_features[utils.STDEV]}')
    nof_decisions = utils.get_summary_stastistics(decisions, PRECISION)
    print('#Decisions:')
    print(f' |median: {nof_decisions[utils.MEDIAN]}')
    print(f' |mean: {nof_decisions[utils.MEAN]}')
    print(f' |stdev: {nof_decisions[utils.STDEV]}')
    execution_time = utils.get_summary_stastistics(execution_times, PRECISION)
    print('Execution time:')
    print(f' |median: {execution_time[utils.MEDIAN]} s')
    print(f' |mean: {execution_time[utils.MEAN]} s')
    print(f' |stdev: {execution_time[utils.STDEV]} s')
    memory_consumption = utils.get_summary_stastistics(memory_consumptions, PRECISION)
    print('Memory consumption:')
    print(f' |median: {memory_consumption[utils.MEDIAN]} MB')
    print(f' |mean: {memory_consumption[utils.MEAN]} MB')
    print(f' |stdev: {memory_consumption[utils.STDEV]} MB')

    print(f'Experiment total execution time: {AlgorithmStats.get_total_execution_time(PRECISION)} s.')

    # Serialize results
    fm_name = input_model[input_model.rfind('/')+1:input_model.rfind('.')]
    stats_filename = f'{fm_name}_{stats_name}_{stopping_condition}'
    if isinstance(algorithm, MonteCarloAlgorithm):
        mc_stopping_condition = algorithm.get_decision_stopping_condition()
        stats_filename += f'_{mc_stopping_condition}'
    stats_filename += '.csv'
    
    AlgorithmStats.serialize(stats_name, os.path.join(RESULTS, stats_filename))

    print('Finished.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem: Finding defective configurations.')
    parser.add_argument('-s', '--seed', dest='seed', type=int, required=False, default=None, help='Seed to initialize the random generator (default None), setup only for replication purposes.')
    parser.add_argument('-r', '--runs', dest='runs', type=int, required=False, default=1, help='Number of executions (default 1).')
    parser.add_argument('-fm', '--featuremodel', dest='feature_model', type=str, required=True, help='Input feature model: "aafm-excerpt" (default), "aafm" or "jhipster".')
    parser.add_argument('-alg', '--algorithm', dest='algorithm', type=str, required=False, default="flat", help='Algorithm to be used ("mcts" for the UCT Algorithm (default), "greedy" for GreedyMCTS, "flat" for basic Monte Carlo, "random" for Random strategy, "astar" for A*).')
    parser.add_argument('-sc', '--stopping_condition', dest='stopping_condition', type=str, required=False, default=None, help='Stopping condition for the algorithm: "iter" for iterations, or "time". (default: the algorithm runs until a solution is found).')
    parser.add_argument('-sv', '--stopping_value', dest='stopping_value', type=int, required=False, default=None, help='Value for the stopping condition: number of iterations for "iter" or seconds for "time".')
    parser.add_argument('-mc_sc', '--mc_stopping_condition', dest='mc_stopping_condition', type=str, required=False, default='sim', help='Stopping condition for each decision in MonteCarlo algorithms: "sim" for simulations (default) or "time".')
    parser.add_argument('-mc_sv', '--mc_stopping_value', dest='mc_stopping_value', type=int, required=False, default=None, help='Stopping value for each decision in Monte Carlo algorithms: number of simulations for "sim" (default 100) or seconds for "time" (default 1 s).')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=False, default=0.5, help='Exploration weight constant for UCT Algorithm (default 0.5).')
    parser.add_argument('-f', '--features', dest='features', type=str, nargs='*', required=False, help='Initial feature selections (initial configuration).')
    parser.add_argument('-c', '--core', dest='core_features', action='store_true', required=False, help='Use core features as initial configuration state.')
    parser.add_argument('-p', '--parallel', dest='parallel', action='store_true', required=False, help='User parallel version of the algorithm if available (algorithm supported: "flat").')
    args = parser.parse_args()

    if args.seed is not None:
        # Initialize the random module
        print(f'Initialized random module with seed {args.seed}')
        random.seed(args.seed)

    if args.runs <= 0:
        print(f"ERROR: the number of executions (runs) must be positive.")
        parser.print_help()
        sys.exit()

    if args.feature_model.lower() not in ['aafm-excerpt', 'aafm', 'jhipster']:
        print(f"ERROR: Feature model not recognized. Use: 'aafm-excerpt', 'aafm', or 'jhipster'.")
        parser.print_help()
        sys.exit()

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

    if args.algorithm.lower() not in ['mcts', 'greedy', 'flat', 'random', 'astar']:
        print(f"ERROR: Algorithm not recognized.")
        parser.print_help()
        sys.exit()

    algorithm_name = args.algorithm.lower()
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

    if args.features is None:
        features = []
    else:
        features = args.features

    main(runs=args.runs,
         input_model=args.feature_model.lower(), 
         algorithm=algorithm, 
         features_names=features,
         use_core_features=args.core_features,
         stats_name=stats_name)