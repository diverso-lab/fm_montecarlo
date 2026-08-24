import argparse
import random
import sys 
import os

import matplotlib.pyplot as plt

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from flamapy.metamodels.bdd_metamodel.operations import BDDProductDistribution

from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import FlatMonteCarlo, UCTMCTS, GreedyMCTS, RandomStrategy, AStarSearch
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.problems.configuration_based_analyses.valid_min_config_state import ValidMinimumConfigurationState, ValidMinConfigProblem
from montecarlo_framework.models.feature_model import fm_utils


ALGORITHM = 'ALGORITHM'
COLOR = 'COLOR'
MARKER = 'MARKER'
ANNOTATION_XY_DISTANCE = 'ANNOTATION_XY_DISTANCE'

OUTPUT_RESULTS = 'results/min_valid_config/'


def plot_product_distribution(product_distribution: list[int]) -> None:
    # Create data for the PD
    x_pd = [features for features, _ in enumerate(product_distribution)]
    y_pd = product_distribution

    plt.plot(x_pd, y_pd, color='black')  # line plot
    plt.fill_between(x_pd, y_pd, color='grey')  # area plot
    

def plot_configurations(ax,
                        name: str,
                        color: str,
                        marker: str,
                        features: list[int], 
                        products: list[int], 
                        distinct_products: list[int],
                        annotation_xy_distance: tuple[int, int]) -> None:
    sizes = [p*10 for p in products]
    ax.scatter(features, distinct_products, color=color, marker=marker, s=sizes, label=name)
    for i, v in enumerate(features):
        ax.annotate(f'{distinct_products[i]}({products[i]})', 
                    (features[i], distinct_products[i]))
                    #textcoords="offset points", # how to position the text
                    #xytext=annotation_xy_distance, # distance from text to points (x,y)
                    #ha='center') # horizontal alignment can be left, right or center

def main(input_fm: str, iterations: int, runs: int):
    # Initialize the random module
    random.seed(0)

    # Load feature model
    feature_model = FeatureIDEReader(input_fm).transform()
    
    # Initialize metamodels (FM, SAT, BDD)
    fm = FM(feature_model)  # FM is a helper class

    fm.bdd_model = None
    # Serialize the product distribution
    if fm.bdd_model is not None:
        pd_op = BDDProductDistribution().execute(fm.bdd_model)
        pd_op.serialize(f'{OUTPUT_RESULTS + fm.fm_model.root.name.lower()}_product_distribution.csv')

        # Plot the product distribution
        # Set labels
        fig, ax = plt.subplots()
        plt.title("Product distribution")
        plt.xlabel("#Features")
        plt.ylabel("#Products")
        plot_product_distribution(pd_op.get_result())

    # Initial state and problem
    core_features = fm_utils.get_core_features(feature_model)
    selected_features = core_features
    unselected_features = list(set(feature_model.get_features()) - set(core_features))
    selected_variables = [fm.sat_model.variables[f.name] for f in selected_features]
    unselected_variables = [-fm.sat_model.variables[f.name] for f in unselected_features]

    #print(f'unselected features: {unselected_features}')
    #print(f'unselected variables: {unselected_variables}')
    initial_config = FMConfiguration(fm, selected_features, unselected_features, selected_variables, unselected_variables)
    
    initial_state = ValidMinimumConfigurationState(initial_config)
    problem = ValidMinConfigProblem(initial_state)

    # Get algorithm instances
    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=iterations)
    selection_criteria = MaxChild()

    algorithms = {}
    algorithms['Random strategy'] = {ALGORITHM: RandomStrategy(stopping_condition),
                                     COLOR: 'black',
                                     MARKER: 'o',
                                     ANNOTATION_XY_DISTANCE: (0, 0)}
    # algorithms['A Star'] = {ALGORITHM: AStarSearch(),
    #                         COLOR: 'yellow',
    #                         MARKER: 'x',
    #                         ANNOTATION_XY_DISTANCE: (0, 20)}
    algorithms['Flat Monte Carlo'] = {ALGORITHM: FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition),
                                      COLOR: 'red',
                                      MARKER: '*',
                                      ANNOTATION_XY_DISTANCE: (10, 0)}
    # algorithms['UCT MCTS (ew=0.5)'] = {ALGORITHM: UCTMCTS(stopping_condition, selection_criteria, iteration_stopping_condition),
    #                                    COLOR: 'blue',
    #                                    MARKER: 'o',
    #                                    ANNOTATION_XY_DISTANCE: (0, 20)}
    # algorithms['Greedy MCTS'] = {ALGORITHM: GreedyMCTS(stopping_condition, selection_criteria, iteration_stopping_condition),
    #                              COLOR: 'green',
    #                              MARKER: '+',
    #                              ANNOTATION_XY_DISTANCE: (-20, 0)}
    


    for alg in algorithms:
        print(f'Running {input_fm} for algorithm {alg}...')
        algorithm = algorithms[alg][ALGORITHM]

        # Run algorithm runs times
        solutions = []
        print('|-run:', end='', flush=True)
        for r in range(runs):
            print(f'{r},', end='', flush=True)
            solutions.append(algorithm.run(problem))
        print()

        # # Prepare the results and serialize them
        # configurations = [sol.get_solution_path()[-1][0].configuration for sol in solutions]
        # distinct_configs = set(configurations)
        
        # x_configs = [len(c.get_selected_features()) for c in configurations]
        # x_distinct_configs = [len(c.get_selected_features()) for c in distinct_configs]

        # x = list(set(x_distinct_configs))
        # y = [x_distinct_configs.count(e) for e in x]

        # frequency = {}
        # for f in x_configs:
        #     frequency[f] = frequency.get(f, 0) + 1
        # sizes = [frequency[f] for f in x]

        # filepath = f'{OUTPUT_RESULTS + fm.fm_model.root.name.lower()}_{algorithm.get_name().lower().replace(" ", "_")}.csv'
        # with open(filepath, mode='w', encoding='utf8') as file:
        #     file.write('Features, Products, Distinct Products\n')
        #     for i, _ in enumerate(x):
        #         file.write(f'{x[i]}, {sizes[i]}, {y[i]}\n')

        # if fm.bdd_model is not None:
        #     # Plot configurations
        #     plot_configurations(ax, alg, algorithms[alg][COLOR], algorithms[alg][MARKER], x, sizes, y, algorithms[alg][ANNOTATION_XY_DISTANCE])
    
    if fm.bdd_model is not None:
        plt.legend(loc="best")
        plt.savefig(f'{OUTPUT_RESULTS + fm.fm_model.root.name.lower()}.pdf')
        #plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem: Finding minimum valid configurations.')
    parser.add_argument('-fm', '--featuremodel', dest='featuremodel', type=str, required=True, help='Input feature model in FeatureIDE format.')
    parser.add_argument('-r', '--runs', dest='runs', type=int, required=False, default=30, help='Number of executions (default 30).')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=False, default=10, help='Number of iterations for Monte Carlo methods (default 10).')
    args = parser.parse_args()

    if args.runs <= 0:
        print(f"ERROR: the number of runs must be positive.")
        parser.print_help()
        sys.exit()

    if args.iterations <= 0:
        print(f"ERROR: the number of iterations must be positive.")
        parser.print_help()
        sys.exit()

    # Create output results folder
    os.makedirs(OUTPUT_RESULTS, exist_ok=True)

    main(args.featuremodel, args.iterations, args.runs)
