import random
from pysat.solvers import Glucose3
from famapy.metamodels.pysat_metamodel.transformations import FmToPysat
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.problems.state_as_configuration.models import RandomConfigurationState
from montecarlo4fms.problems import ProblemData

# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"

# PARAMETERS
input_fm_name = "aafms_framework_simple_impl"


def is_valid(config, cnf_model):
    g = Glucose3()
    for clause in cnf_model.cnf:
        g.add_clause(clause)
    config_names = (feature.name for feature in config.get_selected_elements())
    formula = ([clause[0]] if clause[1] in config_names else [-clause[0]] for clause in cnf_model.features.items())
    for f in formula:
        g.add_clause(f)
    return g.solve()

def main():
    input_fm = INPUT_PATH + input_fm_name + ".xml"
    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    aafms = AAFMsHelper(fm)

    # configs = aafms.get_configurations()
    # print(f"configs: {len(configs)}")
    # for c in configs:
    #     print(str(c))

    print("Running algorithm...")
    mc_iters = 1
    simulations = 10000
    for nof in range(len(fm.get_features())+1):
        valid_configs = 0
        for s in range(simulations):
            config = FMConfiguration(elements={})
            possible_features = [f for f in fm.get_features()]
            while len(config.get_selected_elements()) < nof:
                random_feature = random.choice(possible_features)
                possible_features.remove(random_feature)
                config.add_element(random_feature)
            if aafms.is_valid_configuration(config):
                valid_configs += 1

        print(f"Probability of valid configuration for {nof} features: {valid_configs} / {simulations} = {float(valid_configs)/simulations * 100} %")

if __name__ == '__main__':
    main()
