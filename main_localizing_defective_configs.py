import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.state_as_configuration.models import DefectiveSimulatedConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.utils import Heatmap


# CONSTANTS
INPUT_PATH = "evaluation/aafmsPythonFramework/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"
HEATMAP_FILEPATH = "heatmap_loc_def_configs.csv"

# PARAMETERS
#input_fm_name = "aafms_framework_simple_impl"
input_fm_name = "model_simple_paper_excerpt"
input_fm_cnf_name = "model_simple_paper_excerpt-cnf"
# input_fm_name = "model_paper"
# input_fm_cnf_name = "model_paper-cnf"
iterations = 10
exploration_weight = 0.5
initial_config_features = []
#initial_config_features = ['AAFMFramework', 'Metamodels', 'CNFModel', 'AutomatedReasoning', 'Solvers', 'Packages', 'DepMng', 'pip', 'setuptools', 'System', 'Linux']


def main():
    print("Problem 1 (simulated): Finding defective configurations.")
    print("-----------------------------------------------")

    print("Setting up the problem...")

    input_fm = INPUT_PATH + input_fm_name + ".xml"

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

     # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(INPUT_PATH + input_fm_cnf_name + ".txt")
    cnf_model = cnf_reader.transform()
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    #all_configurations = aafms_helper.get_configurations()
    #print(f"#AllConfigs: {len(all_configurations)}")

    print(f"Creating set of actions...")
    actions = TreeActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms_helper, actions)

    print(f"Creating initial state (configuration)...")
    if initial_config_features:
        initial_config = FMConfiguration(elements={fm.get_feature_by_name(f) : True for f in initial_config_features})
    else:
        initial_config = FMConfiguration()

    initial_state = DefectiveSimulatedConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print("Problem setted up.")

    print(f"Configuring MonteCarlo algorithm...")
    montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    print(f"{type(montecarlo).__name__} with {iterations} iterations, and {exploration_weight} exploration weight.")

    print("Running algorithm...")

    n = 0
    state = initial_state
    while not state.is_terminal(): # state.reward() <= 0 and state.get_actions():
        #print(f"Input state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")
        #time_start = time.time()
        state = montecarlo.run(state)
        #time_end = time.time()
        #print(f"Execution time for Step {n}: {time_end - time_start} seconds.")
        #montecarlo.print_MC_values(state)
        montecarlo.print_MC_search_tree()
        n += 1

    print(f"Final state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")

    print(f"#Terminal states Visits {montecarlo.terminal_nodes_visits}")
    print(f"#Terminal states Evaluations {len(montecarlo.states_evaluated)}")
    print(f"#Rewards calls {montecarlo.nof_reward_function_calls}")
    
    heatmap = Heatmap(fm, montecarlo.tree, montecarlo.Q, montecarlo.N)
    heatmap.extract_feature_knowledge()
    heatmap.serialize(HEATMAP_FILEPATH)
    #montecarlo.print_heat_map(fm)
    montecarlo.print_MC_search_tree()
    print("Finished!")

if __name__ == '__main__':
    start = time.time()
    #cProfile.run("main()")
    main()
    end = time.time()
    print(f"Total Time: {end-start} seconds")
