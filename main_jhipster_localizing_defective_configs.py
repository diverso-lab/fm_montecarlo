import time
import random
import cProfile
from functools import reduce
from collections import defaultdict

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.state_as_configuration.models import FailureConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.utils import Heatmap, HeatmapFull
from montecarlo4fms.utils import MCTSStatsIts, MCTSStats

from evaluation.jhipster import jhipster

# CONSTANTS
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"
HEATMAP_FILEPATH = "heatmap_loc_def_configs.csv"
HEATMAP_PATH = OUTPUT_RESULTS_PATH + "heatmaps/"
STATS_PATH = OUTPUT_RESULTS_PATH + "stats/"

# PARAMETERS
#iterations = 100
exploration_weight = 0
initial_config_features = []
#initial_config_features = ['AAFMFramework', 'Metamodels', 'CNFModel', 'AutomatedReasoning', 'Solvers', 'Packages', 'DepMng', 'pip', 'setuptools', 'System', 'Linux']


def main(iterations: int):
    print("Problem 1 (simulated): Finding defective configurations.")
    print("-----------------------------------------------")

    print("Setting up the problem...")

    print(f"Loading feature model: {jhipster.FM_FILE} ...")
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")
    print(fm)
     # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    #all_configurations = aafms_helper.get_configurations()
    #print(f"#AllConfigs: {len(all_configurations)}")

    print(f"Creating set of actions...")
    actions = TreeActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms_helper, actions)

    # Read the jhipster configurations as a dict of FMConfiguration -> bool (failure)
    jhipster_configurations = jhipster.read_jHipster_feature_model_configurations()
    problem_data.jhipster_configurations = jhipster_configurations
    problem_data.sample = defaultdict(bool)

    print(f"Creating initial state (configuration)...")
    if initial_config_features:
        initial_config = FMConfiguration(elements={fm.get_feature_by_name(f) : True for f in initial_config_features})
    else:
        initial_config = FMConfiguration()

    initial_state = FailureConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print("Problem setted up.")

    print(f"Configuring MonteCarlo algorithm...")
    #montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    montecarlo = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=iterations)
    print(f"{type(montecarlo).__name__} with {iterations} iterations, and {exploration_weight} exploration weight.")

    print("Running algorithm...")

    n = 0
    state = initial_state
    mcts_stats = MCTSStats()
    total_time_start = time.time()
    state = montecarlo.run(state)
    # while state.reward() <= 0 and state.get_actions(): #not state.is_terminal(): # state.reward() <= 0 and state.get_actions():
    #     #print(f"Input state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")
    #     time_start = time.time()
    #     new_state = montecarlo.run(state)
    #     time_end = time.time()

    #     # heat map
    #     # heatmap = Heatmap(fm, montecarlo.tree, montecarlo.Q, montecarlo.N, state)
    #     # heatmap.extract_feature_knowledge()
    #     # heatmap.serialize(HEATMAP_PATH + 'jhipster/jhipster-step' + str(n) + '.csv')
    #     # stats
    #     #mcts_stats.add_step(n, montecarlo.tree, state, new_state, iterations, montecarlo.n_evaluations, montecarlo.n_positive_evaluations, time_end-time_start)    
    #     #montecarlo.n_evaluations = 0
    #     #montecarlo.n_positive_evaluations = 0

    #     state = new_state
    #     n += 1
    #mcts_stats.serialize(STATS_PATH + 'jhipster/jhipster-step-it' + str(iterations) + '.csv')

    total_time_end = time.time()
   
    
    print(f"Final state {n}: {str(state)} -> valid={state.is_valid_configuration}, R={state.reward()}")

    print(f"#Terminal states Visits {montecarlo.terminal_nodes_visits}")
    print(f"#Terminal states Evaluations {len(montecarlo.states_evaluated)}")
    print(f"#Rewards calls {montecarlo.nof_reward_function_calls}")
    
    #heatmap = HeatmapFull(fm, montecarlo.tree, montecarlo.Q, montecarlo.N)
    #heatmap.extract_feature_knowledge()
    #heatmap.serialize(HEATMAP_FILEPATH)
    #montecarlo.print_heat_map(fm)
    #montecarlo.print_MC_search_tree()
    print("Finished!")

    montecarlo.name = str(montecarlo)
    return n, montecarlo, total_time_end-total_time_start

def random_sampling(sample_size: int) -> set:
    jhipster_configurations = jhipster.read_jHipster_feature_model_configurations()

    start = time.time()
    configs_sample = random.sample(list(jhipster_configurations.keys()), sample_size)
    execution_time = time.time() - start 
    alg = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=0, exploration_weight=0)
    alg.name = 'Random Sampling'
    alg.tree = None
    alg.n_evaluations = len(configs_sample)
    alg.n_positive_evaluations = len([x for x in configs_sample if jhipster_configurations[x]])

    return 1, alg, execution_time

if __name__ == '__main__':
    start = time.time()
    #cProfile.run("main()")

    mcts_stats_its = MCTSStatsIts()
    EV_RND_SAMPLING = [37, 105, 83, 123, 419, 245, 625, 396, 177, 194, 505]
    #for i, it in enumerate([x*10 for x in range(10+1)]):
    #for it in [1, 100, 250, 500, 750, 1000]:
    for i, it in enumerate([x*250 for x in range(20+1)]):
    #for it in [1, 250, 500, 750, 1000]:
    #for it in [33, 680, 904, 908, 1079]:
        if it == 0: 
            it = 1

        n, alg, exec_time = main(it)   
        #n, alg, exec_time = random_sampling(it)   
        alg.name = 'flat Monte Carlo'
        alg.tree = None
        mcts_stats_its.add_step(alg.name, n, alg.tree, it, alg.n_evaluations, alg.n_positive_evaluations, exec_time)
    mcts_stats_its.serialize(STATS_PATH + 'jhipster/jhipster-its.csv')
    end = time.time()
    print(f"Total Time: {end-start} seconds")
