import argparse
import cProfile
import os.path

from montecarlo4fms.models import SearchSpace
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.algorithms import RandomStrategy
from montecarlo4fms.algorithms.stopping_conditions import IterationsStoppingCondition
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.problems.state_as_configuration.models import ConfigurationStateDecision, ValidMinimumConfigurationState
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper, fm_utils
from montecarlo4fms.problems.state_as_configuration.actions import ActionsList

# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

# PARAMETERS
#input_fm_name = "aafms_framework_simple_impl"
input_fm_name = "pizzas"
ITERATIONS = 100
exploration_weight = 0.5
#initial_configuration_features = ['Solvers']
initial_configuration_features = []
MAX_FEATURES = 63
#montecarlo_algorithm = MonteCarloAlgorithms.uct_iterations_maxchild_random_expansion(iterations=iterations, exploration_weight=exploration_weight)
#montecarlo_algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=iterations)
#montecarlo_algorithm = RandomStrategy(IterationsStoppingCondition(iterations=iterations))
input_fm = INPUT_PATH + input_fm_name + ".xml"


def main():
    print(f"Loading feature model: {input_fm} ...")
    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")
    print(fm)

    print(f"Transforming to CNF model...")
    aafms = AAFMsHelper(fm)
    configurations = aafms.get_configurations()
    print(f"#Configurations: {len(configurations)}")
    configs_n = {c : len(c.elements) for c in configurations}
    frequency = {}
    for c in configs_n.keys():
        frequency[len(c.elements)] = frequency.get(len(c.elements), 0) + 1

    for f in frequency:
        print(f"{f}: {frequency[f]} -> {frequency[f] / len(configurations) * 100}")
    #print(f"CNF model with {len(aafms.formula)} clauses.")

    for c in configurations:
        print(f"config: {str(c)} -> {aafms.is_valid_configuration(c)}")

    print(f"Creating set of actions...")
    actions = ActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms, actions)

    print(f"Creating initial state (configuration)...")
    if initial_configuration_features:
        print(f"|-> Parsing features...")
        list_features = [fm.get_feature_by_name(f) for f in initial_configuration_features]
        print(f"|-> Auto-selecting parents of features...")
        selections = list_features.copy()
        for f in list_features:
            selections.extend(fm_utils.select_parent_features(f))
        selections.extend(list_features)
        initial_config = FMConfiguration(elements={s: True for s in selections})
    else:
        initial_config = FMConfiguration(elements=dict())

    #initial_state = ConfigurationStateDecision(configuration=initial_config, decision=fm.get_feature_by_name('Solvers'), data=problem_data)
    #initial_state = ConfigurationStateDecision(configuration=initial_config, decision=None, data=problem_data)
    initial_state = ValidMinimumConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    montecarlo_algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=ITERATIONS, exploration_weight=exploration_weight)

    ##########################################
    state = initial_state
    while not state.is_terminal(): #state.reward() <= 0 and state.find_successors():
        new_state = montecarlo_algorithm.run(state)
        montecarlo_algorithm.print_MC_values(state)
        state = new_state

    print(f"Result state: {state} -> {state.reward()}")
    print(f"#Features: {len(state.configuration.get_selected_elements())}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MonteCarlo evaluation.')
    #parser.add_argument('-r', '--run', dest='run', type=int, required=False, help='Execute the program indicating the id of the current run.')
    parser.add_argument('-p', '--profile', dest='profile', action='store_true', required=False, help='Execute the program with cProfile.')
    args = parser.parse_args()

    if args.profile:
        cProfile.run("main(run=0,iterations=ITERATIONS_PROFILE)")
    else:
        main()
