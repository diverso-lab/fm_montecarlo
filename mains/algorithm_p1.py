import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.defective_configurations.models import ConfigurationState, ConfigurationStateRelations
from montecarlo4fms.algorithms import MonteCarloAlgorithms

RESULT_FILE = "output_results/p1_results.txt"
INPUT_PATH = "input_fms/"
FM_NAME = "aafms_framework_simple_impl"

def algorithm(montecarlo, initial_state):

    n = 0
    state = initial_state
    print(f"step ", end='', flush=True)
    while state.reward() <= 0 and state.get_actions():
        print(f"{n}.", end='', flush=True)
        new_state = montecarlo.run(state)
        state = new_state
        n += 1
    return state, montecarlo

def main():
    print("Problem 1: Localizing defective configurations.")
    print("-----------------------------------------------")

    with open(RESULT_FILE, 'w+') as file:
        file.write("Run, Algorithm, Iterations, Time, Features, Reward, Nodes, Configuration\n")

    fide_parser = FeatureIDEParser(INPUT_PATH + FM_NAME + ".xml")
    fm = fide_parser.transform()

    runs = 3
    iterations = 100
    for r in range(1,runs+1):
        montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations)
        initial_state = ConfigurationStateRelations(configuration=FMConfiguration(), feature_model=fm, aafms_helper=AAFMsHelper(fm))

        print(f"Run {r} for {type(montecarlo).__name__} with {iterations} iterations.")
        start = time.time()
        state, montecarlo = algorithm(montecarlo, initial_state)
        end = time.time()
        print(f"Done!")

        with open(RESULT_FILE, 'a+') as file:
            file.write(f"{r}, {type(montecarlo).__name__}, {iterations}, {end-start}, {len(state.configuration.elements)}, {state.reward()}, {len(montecarlo.tree)}, {[str(f) for f in state.configuration.elements if state.configuration.elements[f]]}\n")

if __name__ == '__main__':
    cProfile.run("main()")
