import random 
import sys

import pytest

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
 
# setting path
sys.path.append('.')

from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import FlatMonteCarlo, AStarSearch, Algorithm
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.models.feature_model.fm_configuration import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses.valid_min_config_state import ValidMinimumConfigurationState, FindAllValidMinimumConfigurationState, ValidMinConfigProblem


# INDEX: ATTRIBUTE
# 0 filename
# 1 seed for random initialization
# 2 iterations for Montecarlo algorithm
# 3 expected minimum nof features in best solutions
# 4 expected nof solutions 
# 5 expected solution
MODELS = [('pizzas', 0, 10, 7, 12, ['Pizza', 'CheesyCrust', 'Size', 'Big', 'Dough', 'Neapolitan', 'Topping', 'Salami']),
          ('pizzas', 2021, 10, 7, 12, ['Pizza', 'Dough', 'Size', 'Normal', 'Neapolitan', 'Topping', 'Mozzarella']),
          ('pizzas', 2022, 10, 7, 12, ['Pizza', 'Dough', 'Size', 'Normal', 'Neapolitan', 'Topping', 'Salami']),
          ('pizzas', 0, 100, 7, 12, ['Pizza', 'Size', 'Normal', 'Dough', 'Neapolitan', 'Topping', 'Mozzarella']),
          ('pizzas', 2021, 100, 7, 12, ['Pizza', 'Size', 'Normal', 'Dough', 'Sicilian', 'Topping', 'Mozzarella']),
          ('pizzas', 2022, 100, 7, 12, ['Pizza', 'Size', 'Dough', 'Normal', 'Sicilian', 'Topping', 'Salami']),
          ('GPL', 0, 10, 7, 1, ['GPL', 'Weight', 'Driver', 'GraphType', 'Benchmark', 'Directed', 'Undirected', 'Search', 'Algorithms', 'Prim']),
          ('GPL', 2021, 10, 7, 1, ['GPL', 'Driver', 'Benchmark', 'Search', 'GraphType', 'Directed', 'Weight', 'Algorithms', 'Num']),
          ('GPL', 2022, 10, 7, 1, ['GPL', 'Weight', 'GraphType', 'Driver', 'Undirected', 'Benchmark', 'Algorithms', 'Prim']),
          ('GPL', 0, 100, 7, 1, ['GPL', 'Driver', 'Search', 'GraphType', 'Directed', 'Benchmark', 'DFS', 'Algorithms', 'Cycle']),
          ('GPL', 2021, 100, 7, 1, ['GPL', 'Driver', 'Benchmark', 'Search', 'Weight', 'GraphType', 'DFS', 'Directed', 'Algorithms', 'SCC']),
          ('GPL', 2022, 100, 7, 1, ['GPL', 'Search', 'Driver', 'GraphType', 'Benchmark', 'DFS', 'Weight', 'Directed', 'Algorithms', 'Num']),
          ('wget', 0, 10, 2, 1, ['wget', 'base']),
          ('wget', 2021, 10, 2, 1, ['wget', 'base']),
          ('wget', 2022, 10, 2, 1, ['wget', 'base']),
          ('wget', 0, 100, 2, 1, ['wget', 'base']),
          ('wget', 2021, 100, 2, 1, ['wget', 'base']),
          ('wget', 2022, 100, 2, 1, ['wget', 'base']),
          ('jHipster', 0, 10, 11, 4, ['JHipster', 'Generator', 'Server', 'Database', 'Authentication', 'MicroserviceApplication', 'Uaa', 'MongoDB', 'TestingFrameworks', 'Gatling', 'Docker', 'BackEnd', 'Maven', 'Cucumber']),
          ('jHipster', 2021, 10, 11, 4, ['JHipster', 'Libsass', 'Database', 'Cassandra', 'TestingFrameworks', 'Generator', 'Docker', 'ClusteredSession', 'Gatling', 'BackEnd', 'Cucumber', 'Application', 'Gradle', 'Authentication', 'JWT', 'MicroserviceGateway', 'Protractor']),
          ('jHipster', 2022, 10, 11, 4, ['JHipster', 'TestingFrameworks', 'ClusteredSession', 'Generator', 'InternationalizationSupport', 'SocialLogin', 'Gatling', 'SpringWebSockets', 'Authentication', 'Libsass', 'HTTPSession', 'Cucumber', 'BackEnd', 'Gradle', 'Database', 'MongoDB', 'Protractor', 'Application', 'Monolithic'])
]

INPUT_MODELS_FOLDER = 'input_fms/'
EXTENSION = '.xml'


def get_model(model_name: str) -> FM:
    feature_model = FeatureIDEReader(INPUT_MODELS_FOLDER + model_name + EXTENSION).transform()
    return FM(feature_model)

@pytest.mark.parametrize("model_name, seed, iterations, expected_solution", [[m[0], m[1], m[2], m[5]] for m in MODELS])
def test_reproducibility_flatmc(model_name: str, seed: int, iterations: int, expected_solution: list[int]):
    """Test reproducibility for Flat Montecarlo by setting up a random seed.
    
    The solution should return the same sequence of (state, action).
    Args:
        model_name: Name of the feature model file.
        seed: Seed to initialize the random module.
        iterations: Number of iterations for the algorithm's stopping condition.
        expected_solution: List of features' names in the order to be taken.
    """

    # Set random seed
    random.seed(seed)

    # Load feature model
    model = get_model(model_name)

    # Get algorithm instance
    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=iterations)
    selection_criteria = MaxChild()
    algorithm = FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition)

    # Initial state and problem
    initial_config = FMConfiguration(Configuration(elements={}), model)
    initial_state = ValidMinimumConfigurationState(initial_config)
    problem = ValidMinConfigProblem(initial_state)

    # Run algorithm
    solution = algorithm.run(problem)

    # Check length of solution (number of decisions)
    assert len(solution.get_solution_path()) == len(expected_solution) + 1

    # Check decision ordering
    for step, node in enumerate(solution.get_solution_path()):
        _, action = node
        assert action is None or action.feature.name == expected_solution[step-1]
    
    # Check terminal state (the solution)
    features = [f.name for f in solution.terminal_node.state.configuration.get_selected_features()]
    assert features == expected_solution

@pytest.mark.parametrize("model_name, iterations, expected_nof_solutions, expected_nof_features", [[m[0], m[2], m[4], m[3]] for m in MODELS[3:6] + MODELS[15:18]])
def test_completeness_flatmc(model_name, iterations, expected_nof_solutions, expected_nof_features):
    """Test completeness for Flat Montecarlo.
    
    The search should return all possible solutions.
    Args:
        model_name: Name of the feature model file.
        iterations: Number of iterations for the algorithm's stopping condition.
        expected_nof_solutions: Number of solutions to be found.
        expected_nof_features: Number of features in each solution (must be the same in all solutions).
    """

    # Load feature model
    model = get_model(model_name)

    # Get algorithm instance
    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=iterations)
    selection_criteria = MaxChild()
    algorithm = FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition)

    # Initial state and problem
    initial_config = FMConfiguration(Configuration(elements={}), model)
    initial_state = ValidMinimumConfigurationState(initial_config)
    problem = ValidMinConfigProblem(initial_state)

    # Run algorithm
    solutions = set()
    while len(solutions) < expected_nof_solutions:
        solution = algorithm.run(problem)
        solutions.add(solution)
        problem.add_solution(solution)

    # Check number of solutions
    assert len(solutions) == expected_nof_solutions
    assert len(problem.get_solutions()) >= expected_nof_solutions

    # Check correct solutions
    for sol in solutions:
        assert len(sol.terminal_node.state.configuration.get_selected_features()) == expected_nof_features
