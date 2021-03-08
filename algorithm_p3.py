import time
import cProfile
from typing import List, Callable

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.defective_configurations.models import ConfigurationStateCompletion

def algorithm(montecarlo, initial_state):
    n = 0
    state = initial_state
    print(f"step ", end='', flush=True)
    while not state.is_terminal(): #state.reward() <= 0 and state.get_actions():
        print(f"{n}.", end='', flush=True)
        state = montecarlo.run(state)
        n += 1
    return state, montecarlo

def main(input_fm: str, output_results_file: str, required_features_names: List['str'] = [], montecarlo_algorithm: Callable = None, runs: int = 1, iterations: int = None, exploration_weight: float = None):
    print("Problem 3: Completion of partial configurations.")
    print("-----------------------------------------------")

    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    aafms_helper = AAFMsHelper(fm)

    if required_features_names:
        required_features = [fm.get_feature_by_name(f) for f in required_features_names]
    else:
        required_features = aafms_helper.get_core_features()

    with open(output_results_file, 'w+') as file:
        file.write("Run, Algorithm, Iterations, Time, Features in Config, Valid Config, Reward, Nodes, Configuration\n")

    for r in range(1,runs+1):
        montecarlo = montecarlo_algorithm(iterations=iterations, exploration_weight=exploration_weight)
        initial_state = ConfigurationStateCompletion(configuration=FMConfiguration(), feature_model=fm, aafms_helper=aafms_helper, required_features=required_features)

        print(f"Run {r} for {type(montecarlo).__name__} with {iterations} iterations.")
        start = time.time()
        state, montecarlo = algorithm(montecarlo, initial_state)
        end = time.time()
        print(f"Done!")

        with open(output_results_file, 'a+') as file:
            file.write(f"{r}, {type(montecarlo).__name__}, {iterations}, {end-start}, {len(state.configuration.elements)}, {state.is_valid_configuration}, {state.reward()}, {len(montecarlo.tree)}, {str([str(f) for f in state.configuration.elements if state.configuration.elements[f]])}\n")

if __name__ == '__main__':
    cProfile.run("main()")
