import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.defective_configurations.models import ConfigurationStateCompletion
from montecarlo4fms.algorithms import MonteCarloAlgorithms

RESULT_FILE = "output_results/p2_results"
INPUT_PATH = "input_fms/"
FM_NAME = "aafms_framework_simple_impl"

def algorithm(montecarlo, initial_state):

    n = 0
    state = initial_state
    print(f"step ", end='', flush=True)
    while not state.is_terminal(): #state.reward() <= 0 and state.get_actions():
        print(f"{n}.", end='', flush=True)
        state = montecarlo.run(state)
        n += 1
    return state, montecarlo

def main():
    print("Problem 1: Completion of partial configurations.")
    print("-----------------------------------------------")

    fide_parser = FeatureIDEParser(INPUT_PATH + FM_NAME + ".xml")
    fm = fide_parser.transform()

    required_features_names = ['Glucose']
    required_features = [fm.get_feature_by_name(f) for f in required_features_names]

    #ss = SearchSpace(initial_state=initial_state, max_depth=20)

    # PARAMETERS
    runs = 1
    iterations = 10
    exploration_weight = 0.5
    result_filepath = RESULT_FILE + "_" + str(iterations) + ".txt"

    with open(result_filepath, 'w+') as file:
        file.write("Run, Algorithm, Iterations, Time, Features in Config, Valid Config, Reward, Nodes, Configuration\n")


    for r in range(1,runs+1):
        montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
        initial_state = ConfigurationStateCompletion(configuration=FMConfiguration(), feature_model=fm, aafms_helper=AAFMsHelper(fm), required_features=required_features)

        print(f"Run {r} for {type(montecarlo).__name__} with {iterations} iterations.")
        start = time.time()
        state, montecarlo = algorithm(montecarlo, initial_state)
        end = time.time()
        print(f"Done!")

        with open(result_filepath, 'a+') as file:
            file.write(f"{r}, {type(montecarlo).__name__}, {iterations}, {end-start}, {len(state.configuration.elements)}, {state.is_valid_configuration}, {state.reward()}, {len(montecarlo.tree)}, {str([str(f) for f in state.configuration.elements if state.configuration.elements[f]])}\n")

if __name__ == '__main__':
    cProfile.run("main()")
