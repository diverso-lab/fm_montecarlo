import cProfile
import random
import numpy as np
import matplotlib.pyplot as plt

from famapy.core.models import Configuration
from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from famapy.metamodels.bdd_metamodel.operations import BDDProductDistributionBF


from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import FlatMonteCarlo, UCTMCTS, AStarSearch
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.problems.configuration_based_analyses.valid_min_config import ValidMinimumConfigurationState, FindAllValidMinimumConfigurationState, ValidMinConfigProblem
from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.models.feature_model import fm_utils


#INPUT_MODEL = 'models/linux-2.6.33.3.xml'
#INPUT_MODEL = 'models/aafms_framework-namesAdapted.xml'
INPUT_MODEL = 'models/pizzas.xml'
#INPUT_MODEL = 'models/jHipster.xml'
#INPUT_MODEL = 'models/WeaFQAs.xml'

INITIAL_CONFIGURATION_FEATURES = {}

def plot_product_distribution(fm: FM, configurations: list[FMConfiguration] = None):
    # Calcualte the product distribution with BDD
    dist = BDDProductDistributionBF().execute(fm.bdd_model).get_result()
    print(f'Product Distribution: {dist}')

    # Create data for the PD
    x = range(len(fm.fm_model.get_features())+1)
    y = dist

    # Create data for configurations
    x_configs = [len(c.get_selected_features()) for c in configurations]
    y_configs = [x_configs.count(e) for e in x_configs]

    # Set labels
    plt.title("Product distribution")
    plt.xlabel("#Features")
    plt.ylabel("#Products")

    # Plot PD
    plt.plot(x, y, color='black', label='PD')  # line plot
    plt.fill_between(x, y, color='grey')  # area plot

    # Plot configurations
    plt.scatter(x_configs, y_configs, color='red', marker='o', label='Configurations')  # dot plot
    
    # Plot legend
    plt.legend(loc="best")

    # Show figure
    plt.show()
    #image_filename = 'pd_temp.png'
    #plt.savefig(image_filename)
    return plt

def main():
    # Initialize the random module
    random.seed(0)

    # Load feature model
    feature_model = FeatureIDEReader(INPUT_MODEL).transform()
    
    # Initialize metamodels (FM, SAT, BDD)
    fm = FM(feature_model)  # FM is a helper class

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
    print(f'Initial state: {initial_state}')
    print(f'Configurable features: {[str(f) for f in initial_state.configuration.configurable_features]}')
    
    problem = ValidMinConfigProblem(initial_state)

    # Get algorithm instance
    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=10)
    selection_criteria = MaxChild()
    alg = FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition)
    #alg = AStarSearch()

    # Run algorithm
    solution = alg.run(problem)

    # Print out the solution
    print('Solution:')
    for step, node in enumerate(solution.get_solution_path()):
        state, action = node
        print(f'Step {step}: {str(action)} -> {str(state)}')

    # Plot the product distribution
    #configurations = [state.configuration for state, _ in solution.get_solution_path()]
    #configuration = solution.get_solution_path()[-1][0].configuration
    #plot_product_distribution(fm, [configuration])

    #MonteCarloStats.serialize('flat_montecarlo_steps', 'output.csv')
    #MonteCarloStats.serialize('UCTMCTS', 'output2.csv')
    print(f'Execution time: {AlgorithmStats.stats["flat_montecarlo_stats"][1][AlgorithmStats.TIME_STR]}')

if __name__ == '__main__':
    #cProfile.run('main()')
    main()