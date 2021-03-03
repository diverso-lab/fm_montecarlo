import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.defective_configurations.models import ConfigurationState, ConfigurationStateRelations
from montecarlo4fms.algorithms import MonteCarloAlgorithms


INPUT_PATH = "montecarlo4fms/problems/defective_configurations/input_fms/"
OUTPUT_PATH = "montecarlo4fms/problems/defective_configurations/output_fms/"
FM_NAME = "aafms_framework"

def main():
    print("Localizing defective configurations problem")

    # Read the feature model
    fide_parser = FeatureIDEParser(INPUT_PATH + FM_NAME + ".xml")
    fm = fide_parser.transform()

    print(f"#Features: {len(fm.get_features())} -> {[str(f) for f in fm.get_features()]}")

    aafms_helper = AAFMsHelper(fm)
    core_features = aafms_helper.get_core_features()
    print(f"#core-features: {len(core_features)} -> {[str(f) for f in core_features]}")
    # config_test = FMConfiguration({fm.get_feature_by_name('Pizza'): True})
    # valid = aafms_helper.is_valid_configuration(config_test)
    # print(f"config: {valid} -> {[str(f) for f in config_test.elements]}")


    iterations = 10
    montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations)
    print(f"Running {type(montecarlo).__name__} with {iterations} iterations.")

    initial_state = ConfigurationStateRelations(FMConfiguration(), fm)

    n = 0
    state = initial_state
    while not state.is_terminal():
        print(f"State {n}: {[str(f) for f in state.configuration.elements if state.configuration.elements[f]]} -> {state.reward()}")
        new_state = montecarlo.run(state)
        montecarlo.print_MC_values(state)
        state = new_state
        n += 1

    print(f"Final State {n}: {[str(f) for f in state.configuration.elements if state.configuration.elements[f]]} -> {state.reward()}")

if __name__ == '__main__':
    start = time.time()
    cProfile.run("main()")
    end = time.time()
    print(f"Time: {end-start} seconds")
