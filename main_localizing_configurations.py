import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.state_as_configuration.models import DefectiveSimulatedConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import ActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms


# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

# PARAMETERS
input_fm_name = "aafms_framework_simple_impl"
iterations = 100
exploration_weight = 0.5
#initial_config_features = []
initial_config_features = ['AAFMFramework', 'Metamodels', 'CNFModel', 'AutomatedReasoning', 'Solvers', 'Packages', 'DepMng', 'pip', 'setuptools', 'System', 'Linux']


def main():
    print("Problem 1 (simulated): Finding defective configurations.")
    print("-----------------------------------------------")

    print("Setting up the problem...")

    input_fm = INPUT_PATH + input_fm_name + ".xml"

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    print(f"Transforming to CNF model...")
    aafms = AAFMsHelper(fm)

    print(f"Creating set of actions...")
    actions = ActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms, actions)

    print(f"Creating initial state (configuration)...")
    initial_config = FMConfiguration(elements={fm.get_feature_by_name(f) : True for f in initial_config_features})
    initial_state = DefectiveSimulatedConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print("Problem setted up.")

    print(f"Configuring MonteCarlo algorithm...")
    montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    print(f"{type(montecarlo).__name__} with {iterations} iterations, and {exploration_weight} exploration weight.")

    print("Running algorithm...")

    n = 0
    state = initial_state
    while state.reward() <= 0 and state.get_actions():
        print(f"Input state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")
        time_start = time.time()
        new_state = montecarlo.run(state)
        time_end = time.time()
        print(f"Execution time for Step {n}: {time_end - time_start} seconds.")
        montecarlo.print_MC_values(state)

        state = new_state
        n += 1

    print(f"Final state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")

    print("Finished!")

if __name__ == '__main__':
    start = time.time()
    cProfile.run("main()")
    end = time.time()
    print(f"Total Time: {end-start} seconds")
