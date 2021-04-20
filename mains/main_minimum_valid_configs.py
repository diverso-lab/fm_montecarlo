import time
import cProfile
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.state_as_configuration.models import ValidMinimumConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.utils import Heatmap, HeatmapFull
from montecarlo4fms.utils import MCTSStats


# CONSTANTS
INPUT_PATH = "evaluation/aafmsPythonFramework/"
OUTPUT_RESULTS_PATH = "output_results/min_valid_config/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"
HEATMAP_FILEPATH = "heatmap_min_valid_configs.csv"

# PARAMETERS
#N_RUNS = 1
#input_fm_name = "aafms_framework_simple_impl"
#input_fm_name = "model_simple_paper_excerpt"
#input_fm_cnf_name = "model_simple_paper_excerpt_deadF-cnf"
input_fm_name = "model_paper"
input_fm_cnf_name = "model_paper-cnf"
#iterations = 100
exploration_weight = 0.5
#initial_config_features = ['AAFMFramework', 'Solvers', 'Glucose']
initial_config_features = []
#initial_config_features = ['AAFMFramework', 'Metamodels', 'CNFModel', 'AutomatedReasoning', 'Solvers', 'Packages', 'DepMng', 'pip', 'setuptools', 'System', 'Linux']
HEATMAP_PATH = OUTPUT_RESULTS_PATH + "heatmaps/"
STATS_PATH = OUTPUT_RESULTS_PATH + "stats/"


def main(run: int, iterations: int):
    print("Problem 2: Minimum valid configurations.")
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

    initial_state = ValidMinimumConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print("Problem setted up.")

    print(f"Configuring MonteCarlo algorithm...")
    #montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    montecarlo = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=iterations)
    print(f'"{montecarlo}" with {iterations} iterations, and {exploration_weight} exploration weight.')

    print("Running algorithm...")

    n = 0
    mcts_stats = MCTSStats()
    state = initial_state
    start = time.time()
    while not state.is_terminal(): # state.reward() <= 0 and state.get_actions():
        #print(f"Input state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")
        time_start = time.time()
        new_state = montecarlo.run(state)
        time_end = time.time()

        # heat map
        # heatmap = Heatmap(fm, montecarlo.tree, montecarlo.Q, montecarlo.N, state)
        # heatmap.extract_feature_knowledge()
        # heatmap.serialize(HEATMAP_PATH + input_fm_name + "-step" + str(n) + ".csv")
        # stats
        #mcts_stats.add_step(n, montecarlo.tree, state, new_state, iterations, montecarlo.n_evaluations, montecarlo.n_positive_evaluations, time_end-time_start)
        montecarlo.n_evaluations = 0

        state = new_state
        n += 1
    end = time.time()
    #mcts_stats.serialize(STATS_PATH + input_fm_name + "-its" + str(iterations) + ".csv")
    print(f"Final state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")

    print(f"#Terminal states Visits {montecarlo.terminal_nodes_visits}")
    print(f"#Terminal states Evaluations {len(montecarlo.states_evaluated)}")
    print(f"#Rewards calls {montecarlo.nof_reward_function_calls}")
    print(f"Total Time: {end-start} seconds")    

    # heatmap = HeatmapFull(fm, montecarlo.tree, montecarlo.Q, montecarlo.N)
    # heatmap.extract_feature_knowledge()
    # heatmap.serialize(HEATMAP_FILEPATH)
    #montecarlo.print_heat_map(fm)
   # montecarlo.print_MC_search_tree()

    print(f"Writing results to file {OUTPUT_RESULTS_FILE}...")
    
    #montecarlo.tree = {}
    montecarlo.name = 'flat Monte Carlo'
    montecarlo.tree = []
    with open(OUTPUT_RESULTS_PATH + input_fm_name + ".csv", 'a+') as file:
        file.write(f'{run}, "{montecarlo.name}", {iterations}, {exploration_weight}, {end-start}, {len(state.configuration.get_selected_elements())}, {state.is_valid_configuration}, {state.reward()}, {len(montecarlo.tree)}, {iterations*n}\n') #, "{str([str(f) for f in state.configuration.get_selected_elements()])}"\n')

    print("Finished!")


if __name__ == '__main__':
    #cProfile.run("main()")
    with open(OUTPUT_RESULTS_PATH + input_fm_name + ".csv", 'w+') as file:
        file.write("Run, Algorithm, StoppingCondition, ExplorationWeight, ExecutionTime, Features, MedianFeatures, ValidConfig, Reward, Nodes, Simulations\n") #, Configuration\n")

    for it in [x*10 for x in range(10+1)]:
        if it == 0:
            it = 1
        for run in range(30):
            main(run=run, iterations=it)
    
    
