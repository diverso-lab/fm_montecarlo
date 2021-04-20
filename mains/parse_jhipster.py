import time
import os
import random
import cProfile
import csv
import itertools
import statistics
from typing import Set
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from montecarlo4fms.problems.state_as_configuration.actions import TreeActionsList, RandomActionsList
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from montecarlo4fms.problems.state_as_configuration.models import ValidMinimumConfigurationState, ValidConfigurationState, FailureConfigurationState, FailureCS
from montecarlo4fms.problems import ProblemData
from montecarlo4fms.algorithms import RandomStrategy
from montecarlo4fms.algorithms.stopping_conditions import IterationsStoppingCondition

from evaluation.jhipster import jhipster


# PARAMS
#SAMPLES = [x for x in range(0, 2750, 250)]
#MCTS_ITERATIONS = 10
#MCTS_EXPLORATION_WEIGHT = 0.5
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "defective_comparison.csv"
OUTPUT_RESULTS_FILE2 = OUTPUT_RESULTS_PATH + "defective_comparison_stepByStep.csv"

# def get_minimum_valid_configuration(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper') -> 'FMConfiguration':
#     actions = TreeActionsList(fm)

#     problem_data = ProblemData(fm, aafms_helper, actions)
#     #mcts = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=10, exploration_weight=0.5)
#     mcts = RandomStrategy(IterationsStoppingCondition(iterations=MCTS_ITERATIONS))
#     state = ValidMinimumConfigurationState(FMConfiguration(elements={}), data=problem_data)
#     while not state.is_terminal():
#         state = mcts.run(state)
#         mcts.print_MC_values(state)
#     print(f"Reward: {state.reward()}")
#     return state.configuration

def get_random_sample(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper', jhipster_configurations: dict, sample_size: int) -> set:
    actions = TreeActionsList(fm)
    problem_data = ProblemData(fm, aafms_helper, actions)
    problem_data.jhipster_configurations = jhipster_configurations

    alg = RandomStrategy(IterationsStoppingCondition(iterations=0))
    sample = defaultdict(bool)
    start = time.time()
    configs_sample = random.sample(list(jhipster_configurations.keys()), sample_size)
    execution_time = time.time() - start 
    for i, rnd_config in enumerate(configs_sample):
        print(f"{i}, ", end='', flush=True)   
        problem_data.sample = defaultdict(bool)
        #rnd_config = random.choice(list(jhipster_configurations.keys()))
        #sample[i] = FailureConfigurationState(rnd_config, data=problem_data)
        sample[FailureCS(rnd_config, data=problem_data)] = True
    alg.terminal_nodes_visits = len(sample)
    alg.states_evaluated = sample
    if not os.path.isfile(OUTPUT_RESULTS_FILE2):
        with open(OUTPUT_RESULTS_FILE2, 'w+') as file:
            file.write("Method, Sample size, Current Sample, Valid configs, Defective configs, Visit configs, Evaluated configs, Time (s)\n")
    with open(OUTPUT_RESULTS_FILE2, 'a+') as file:
        valid_configs = [s.configuration for s in sample if s.is_valid_configuration]
        defective_configs = [s.configuration for s in sample if s.reward() > 0]
        file.write(f'"Random Sampling", {sample_size}, {sample_size}, {len(valid_configs)}, {len(defective_configs)}, {alg.terminal_nodes_visits}, {len(alg.states_evaluated)}, {execution_time}, \n')

    return sample, alg


def get_sample_configurations(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper', jhipster_configurations: dict, sample_size: int, algorithm: 'MonteCarlo') -> set:
    actions = TreeActionsList(fm)
    problem_data = ProblemData(fm, aafms_helper, actions)

    problem_data.jhipster_configurations = jhipster_configurations
    sample = dict()
    results = dict()
    print(f"Sample: ", end='', flush=True)    
    #algorithm.initialize() # Initialize the algorithm as it is a new 'game match'.


    for i in range(sample_size):
        start = time.time()
        print(f"{i}, ", end='', flush=True)    
        problem_data.sample = sample
        #state = FailureCS(FMConfiguration(elements={}), data=problem_data)
        state = FailureConfigurationState(FMConfiguration(elements={}), data=problem_data)
        algorithm.initialize() # Initialize the algorithm as it is a new 'game match'.

        #mcts = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=mcts_iterations, exploration_weight=mcts_exploration_weight)
        #mcts = MonteCarloAlgorithms.uct_iterations_maxchild_random_expansion(iterations=mcts_iterations, exploration_weight=mcts_exploration_weight)
        #mcts = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=mcts_iterations)
        #mcts = RandomStrategy(IterationsStoppingCondition(iterations=mcts_iterations))
        while state.reward() <= 0 and state.find_successors(): #not state.is_terminal():
            state = algorithm.run(state)
        execution_time = time.time() - start
        if state.reward() > 0:
            if state not in sample:
                sample[state] = True
        if state not in results:
            results[state] = True


        if not os.path.isfile(OUTPUT_RESULTS_FILE2):
            with open(OUTPUT_RESULTS_FILE2, 'w+') as file:
                file.write("Method, Sample size, Current Sample, Valid configs, Defective configs, Visit configs, Evaluated configs, Time (s)\n")
        with open(OUTPUT_RESULTS_FILE2, 'a+') as file:
            valid_configs = [s.configuration for s in sample if s.is_valid_configuration]
            defective_configs = [s.configuration for s in sample if s.reward() > 0]
            file.write(f'"{str(algorithm)}", {sample_size}, {i+1}, {len(valid_configs)}, {len(defective_configs)}, {algorithm.terminal_nodes_visits}, {len(algorithm.states_evaluated)}, {execution_time}, \n')

    print(f"Final configuration ({len(state.configuration.elements)} features): {str(state)} -> Valid?={state.is_valid_configuration}, R={state.reward()}")
    
    print(f"#Terminal states Visits {algorithm.terminal_nodes_visits}")
    print(f"#Terminal states Evaluations {len(algorithm.states_evaluated)}")
    print(f"#Rewards calls {algorithm.nof_reward_function_calls}")
    #algorithm.print_MC_search_tree()
    #algorithm.print_heat_map(fm)
    return sample, algorithm


def main(samples_list: list, iterations: int, exploration_weight: float):
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Feature model loaded. Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")
    
    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)

    # Read the jhipster configurations as a dict of FMConfiguration -> bool (failure)
    jhipster_configurations = jhipster.read_jHipster_feature_model_configurations()

    if not os.path.isfile(OUTPUT_RESULTS_FILE):
        with open(OUTPUT_RESULTS_FILE, 'w+') as file:
            file.write("Method, Sample size, Valid configs, Defective configs, Visit configs, Evaluated configs, Time (s)\n")

    # Get sample of configurations
    for sample_size in samples_list:    
        start = time.time()
        algorithm = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
        #algorithm = MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=it)
        sample, algorithm = get_sample_configurations(fm, aafms_helper, jhipster_configurations, sample_size, algorithm)
        #sample, algorithm = get_random_sample(fm, aafms_helper, jhipster_configurations, sample_size)
        execution_time = time.time() - start

        #assert(len(sample) == sample_size)

        valid_configs = [s.configuration for s in sample if aafms_helper.is_valid_configuration(s.configuration)]
        defective_configs = [s.configuration for s in sample if s.reward() > 0]
        with open(OUTPUT_RESULTS_FILE, 'a+') as file:
            file.write(f'"{str(algorithm)}", {sample_size}, {len(valid_configs)}, {len(defective_configs)}, {algorithm.terminal_nodes_visits}, {len(algorithm.states_evaluated)}, {execution_time}, \n')

    #plot_results(OUTPUT_RESULTS_FILE)    

        # for s in sample:
        #     config = sample[s].configuration
        #     print(f"config {s}: {str(config)}, -> Valid?:{aafms_helper.is_valid_configuration(config)}, -> Errors?:{sample[s].reward() == 1}")

    # defective_configs = [s.configuration for s in sample.values() if s.reward() == 1]
    # print(f"Defective configs / sample size = {len(defective_configs)} / {len(sample)} = {len(defective_configs)/len(sample)} = {len(defective_configs)/len(sample) * 100} %")
    # print(f"#Distinct samples: {len(set(sample.values()))}")

    #print(f"#Configurations: {len(configurations)}")
    #config_names = ['JHipster', 'Generator', 'Authentication', 'BackEnd', 'Uaa', 'TestingFrameworks', 'Gatling', 'Maven', 'Docker', 'Server', 'MicroserviceApplication', 'Cucumber']
    
    #config_features = {fm.get_feature_by_name(f): True for f in config_names}
    #config1 = FMConfiguration(elements=config_features)
    #config1 = get_minimum_valid_configuration(fm, aafms_helper)
    #config1 = all_configs[0]
    #print(f"Valid config: {len(config1.get_selected_elements())} : {config1} -> {aafms_helper.is_valid_configuration(config1)}")

    # Read the jHipster configurations from the .csv file.
    #jhipster_configurations = jhipster.read_jHipster_configurations(jhipster.JHIPSTER_CONFIGS_FILE)  

    # if aafms_helper.is_valid_configuration(config1):
    #      jhipster_config = jhipster.filter_configuration(config1, jhipster_configurations)
         #print(f"Filtered config: {jhipster_config}")
    #     error = jhipster.contains_failures(jhipster_config)
    #     print(f"Errors?: {error}")
    # else:
    #     print("Configuración no válida!!")

    # errors = 0
    # for c in jhipster_configurations:
    #     if c['Build'] == 'KO' or c['Compile'] == 'KO':
    #         errors += 1
    # print(f"#Errors: {errors}")

    # jconfigs = jhipster.get_jhipster_configurations("HTTPSession", jhipster_configurations)
    # print(f"#Filter HTTPSession: {len(jconfigs)}")

    # jconfigs = jhipster.get_jhipster_configurations("Protractor", jconfigs)
    # print(f"#Filter Protractor: {len(jconfigs)}")

    # with open("filter_config.csv", 'w+') as ff:
    #     ff.write(str(jconfigs))
    
    # jconfigs = jhipster.get_jhipster_configurations("MicroserviceApplication", jconfigs)
    # print(f"#Filter MicroserviceApplication: {len(jconfigs)}")

    # values = set()
    # for c in jconfigs:
    #     values.add(c['applicationType'])
    # print(values)

    # values = set()
    # for c in configurations:
    #     values.add(c['Log.Build'])
    # print(values)

    # for f in configurations[0].keys():
    #     print(f"{f}: {configurations[0].get(f)}")

    # for f in jhipster_configurations[17267].keys():
    #     print(f"{f}: {jhipster_configurations[17267].get(f)}")

    # values = set()
    # for c in jhipster_configurations:
    #     values.add(c['hibernateCache'])
    # print(values)

def read_file(filepath: 'str') -> list:
    data = {}
    with open(filepath, newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',', skipinitialspace=True)
        for n, row in enumerate(reader, start=1):
            data[n] = row
    results = {}
    methods = {m['Method'] for m in data.values()}
    for m in methods:
        results[m] = [d for d in data.values() if d['Method'] == m]
    return results

def plot_efficiency(fig, method: str, data: list):   # data is a list of dict
    fig.set_title("Efficiency of finding defective configurations")
    fig.set_xlabel("Configurations evaluated")
    fig.set_ylabel("Efficiency (%) Defect./Sample size")

    x_values = [int(x['Evaluated configs']) for x in data]
    y_values = [float(y['Defective configs'])/float(y['Sample size'])*100 if float(y['Sample size']) > 0 else 0 for y in data]

    # x_group = list(set(x_values))
    # x_group.sort()
    # y_group = []
    # for x in x_group:
    #     y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
    #     y_group.append(statistics.median(y))

    # # Smooth the line (suaviza la recta)
    # model=make_interp_spline(x_group, y_group)
    # xs=np.linspace(min(x_group), max(x_group), 300)
    # ys=model(xs)
    # fig.plot(xs, ys, label=method)
        
    fig.plot(x_values, y_values, label=method)
    fig.legend(loc="best")

def plot_efficiency2(fig, method: str, data: list):   # data is a list of dict
    fig.set_title("Efficiency of finding defective configurations")
    fig.set_xlabel("Configurations evaluated")
    fig.set_ylabel("Efficiency (%) Defect./Total Defect.")

    x_values = [int(x['Evaluated configs']) for x in data]
    y_values = [float(y['Defective configs'])/9376 for y in data]

    # x_group = list(set(x_values))
    # x_group.sort()
    # y_group = []
    # for x in x_group:
    #     y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
    #     y_group.append(statistics.median(y))

    # # Smooth the line (suaviza la recta)
    # model=make_interp_spline(x_group, y_group)
    # xs=np.linspace(min(x_group), max(x_group), 500)
    # ys=model(xs)
    # fig.plot(xs, ys, label=data[0]['#Strategy'] + "(" + str(data[0]['#Simulations']) + ")")
        
    fig.plot(x_values, y_values, label=method)
    fig.legend(loc="best")

def plot_efficiency3(fig, method: str, data: list):   # data is a list of dict
    fig.set_title("Efficiency of finding defective configurations")
    fig.set_xlabel("Configurations evaluated")
    fig.set_ylabel("Efficiency (%) Defect./Evaluated.")

    x_values = [int(x['Evaluated configs']) for x in data]
    y_values = [float(y['Defective configs'])/float(y['Evaluated configs'])*100 if float(y['Evaluated configs']) > 0 else 0 for y in data]

    # x_group = list(set(x_values))
    # x_group.sort()
    # y_group = []
    # for x in x_group:
    #     y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
    #     y_group.append(statistics.median(y))

    # # Smooth the line (suaviza la recta)
    # model=make_interp_spline(x_group, y_group)
    # xs=np.linspace(min(x_group), max(x_group), 500)
    # ys=model(xs)
    # fig.plot(xs, ys, label=data[0]['#Strategy'] + "(" + str(data[0]['#Simulations']) + ")")
        
    fig.plot(x_values, y_values, label=method)
    fig.legend(loc="best")

def plot_efficiency4(fig, method: str, data: list):   # data is a list of dict
    fig.set_title("Efficiency of finding defective configurations")
    fig.set_xlabel("Configurations evaluated")
    fig.set_ylabel("Defective configurations")

    x_values = [int(x['Evaluated configs']) for x in data]
    y_values = [float(y['Defective configs']) for y in data]

    # x_group = list(set(x_values))
    # x_group.sort()
    # y_group = []
    # for x in x_group:
    #     y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
    #     y_group.append(statistics.median(y))

    # # Smooth the line (suaviza la recta)
    # model=make_interp_spline(x_group, y_group)
    # xs=np.linspace(min(x_group), max(x_group), 500)
    # ys=model(xs)
    # fig.plot(xs, ys, label=data[0]['#Strategy'] + "(" + str(data[0]['#Simulations']) + ")")
        
    fig.plot(x_values, y_values, label=method)
    fig.legend(loc="best")

def plot_efficiencyX(fig, method: str, data: list):   # data is a list of dict
    fig.set_title("Efficiency of finding defective configurations")
    fig.set_xlabel("Configurations evaluated")
    fig.set_ylabel("Defective configurations")

    x_values = [int(x['Evaluated configs']) for x in data]
    y_values = [float(y['Defective configs'])/float(y['Current Sample'])*100 if float(y['Current Sample']) > 0 else 0 for y in data]

    # x_group = list(set(x_values))
    # x_group.sort()
    # y_group = []
    # for x in x_group:
    #     y = [y_values[i] for i in range(len(y_values)) if x_values[i] == x]
    #     y_group.append(statistics.median(y))

    # # Smooth the line (suaviza la recta)
    # model=make_interp_spline(x_group, y_group)
    # xs=np.linspace(min(x_group), max(x_group), 500)
    # ys=model(xs)
    # fig.plot(xs, ys, label=data[0]['#Strategy'] + "(" + str(data[0]['#Simulations']) + ")")
        
    fig.plot(x_values, y_values, label=method)
    fig.legend(loc="best")

def plot_results(results: dict):
    fig, axs = plt.subplots(2, 2)
    for r in results.keys():
        plot_efficiency(axs[0,0], r, results[r])
    
    for r in results.keys():
        plot_efficiency2(axs[0,1], r, results[r])

    for r in results.keys():
        plot_efficiency3(axs[1,0], r, results[r])

    for r in results.keys():
        plot_efficiency4(axs[1,1], r, results[r])

    fig.tight_layout()
    plt.show()

def plot_results2(results: dict):
    fig, axs = plt.subplots(2, 2)
    for r in results.keys():
        plot_efficiencyX(axs[0,0], r, results[r])
    

    fig.tight_layout()
    plt.show()

def create_jhipster_configurations_failures_file():
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Feature model loaded. Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")

    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()

    # Read the jHipster configurations from the .csv file.
    jhipster_configurations = jhipster.read_jHipster_configurations()  

    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    all_configs = aafms_helper.get_configurations()


    with open(jhipster.JHIPSTER_CONFIGS_FAILURES_FILE, 'w+') as file:
        file.write("Config, Failure\n")

        print(f"Config: " , end='', flush=True)
        for i, c in enumerate(all_configs):
            print(f"{i}, ", end='', flush=True)
            print(str(c))
            jhipster_config = jhipster.filter_configuration(c, jhipster_configurations)
            error = jhipster.contains_failures(jhipster_config)
            file.write(f'"{str(c)}", {error}\n')

    print("Done!")

if __name__ == "__main__":
    # main(samples_list=[x for x in range(0, 2750, 250)], 
    #      montecarlo_algorithm=MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=1))
    LIST_ITERATIONS = [1]
    EXPLORATION_WEIGHT = 0.5
    LIST_SAMPLES = [x for x in range(0, 5100, 100)]

    # UCT MCTS
    # for it in LIST_ITERATIONS:
    #     cProfile.run("main(samples_list=[2340], iterations=it, exploration_weight=EXPLORATION_WEIGHT)")    

    results = read_file(OUTPUT_RESULTS_FILE)
    plot_results(results)

    results = read_file(OUTPUT_RESULTS_FILE2)
    plot_results2(results)
    #############################################################################################
    # flat MonteCarlo
    # for it in LIST_ITERATIONS:
    #     main(samples_list=LIST_SAMPLES,
    #          montecarlo_algorithm=MonteCarloAlgorithms.montecarlo_iterations_maxchild(iterations=it))

    # # UCT MCTS Rnd Exp
    # for it in LIST_ITERATIONS:
    #     main(samples_list=LIST_SAMPLES,
    #          montecarlo_algorithm=MonteCarloAlgorithms.uct_iterations_maxchild_random_expansion(iterations=it, exploration_weight=EXPLORATION_WEIGHT))    

    # # Greedy MCTS
    # for it in LIST_ITERATIONS:
    #     main(samples_list=LIST_SAMPLES,
    #          montecarlo_algorithm=MonteCarloAlgorithms.greedy_iterations_maxchild(iterations=it)) 

    # # Greedy MCTS Rnd Exp
    # for it in LIST_ITERATIONS:
    #     main(samples_list=LIST_SAMPLES,
    #          montecarlo_algorithm=MonteCarloAlgorithms.greedy_iterations_maxchild_random_expansion(iterations=it))  


    #create_jhipster_configurations_failures_file()
    