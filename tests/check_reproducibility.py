import random 

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader

from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import FlatMonteCarlo, AStarSearch
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.models.feature_model.fm_configuration import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses.valid_min_config_state import ValidMinimumConfigurationState, FindAllValidMinimumConfigurationState, ValidMinConfigProblem


INPUT_MODEL = 'input_fms/pizzas.xml'

INITIAL_CONFIGURATION_FEATURES = {}

def main():
    random.seed(2021)

    feature_model = FeatureIDEReader(INPUT_MODEL).transform()
    fm = FM(feature_model)

    initial_config = FMConfiguration(Configuration(elements=INITIAL_CONFIGURATION_FEATURES), fm)
    initial_state = ValidMinimumConfigurationState(initial_config)
    print(f'Initial state: {initial_state}')

    problem = ValidMinConfigProblem(initial_state)
    #initial_state.set_problem(problem)

    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=100)

    selection_criteria = MaxChild()
    alg = FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition)
    #alg = AStarSearch()

    solution = alg.run(problem)

    print('Solution:')
    for step, node in enumerate(solution.get_solution_path()):
        state, action = node
        print(f'Step {step}: {str(action)} -> {str(state)}')

if __name__ == '__main__':
    main()