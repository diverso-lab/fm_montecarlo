"""
This script calculates the probabilities of finding valid configurations in the configuration search space of a given feature model.
"""

import random
import itertools
import statistics
from typing import Set
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.problems.state_as_configuration.models import NFeaturesConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import RandomActionsList, TreeActionsList
from montecarlo4fms.problems import ProblemData


# CONSTANTS
INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "probabilities.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"
HEADER_OUTPUT_FILE = ['Strategy', 'FM', '#Features', '#Configs', '#ValidConfigs', '#ValidDistinctConfigs', '#Simulations', '#Evaluations', 'Probability']

# PARAMETERS
input_fm_name = "model_simple_paper_excerpt_simpleCTCs"

def write_results(n_features, results):
    with open(OUTPUT_RESULTS_FILE, 'a+') as file: 
        file.write(', '.join([results['#Strategy'], input_fm_name, str(n_features), str(results['#Configs']), str(results['#ValidConfigs']), str(results['#ValidDistinctConfigs']), str(results['#Simulations']), str(results['#Evaluations']), str(results['Probability'])])+'\n')

def calculate_real_probabilities(fm: 'FeatureModel', configurations: Set['Configuration']) -> dict:
    """Calculate the real probabilities of finding a valid configuration with a specific number of features."""
    features = fm.get_features()
    n_features = len(features)

    result = {}
    print(f"step: ", end='', flush=True)    
    for nof in range(n_features+1):
        print(f"{nof},", end='', flush=True)
        result[nof] = {}
        result[nof]['#Configs'] = len(list(itertools.combinations(features, nof)))
        configs_with_nof = sum(map(lambda c : len(c.get_selected_elements()) == nof, configurations))
        result[nof]['#ValidConfigs'] = configs_with_nof
        result[nof]['#ValidDistinctConfigs'] = configs_with_nof
        result[nof]['#Simulations'] = 1
        result[nof]['#Evaluations'] = 0
        result[nof]['Probability'] = result[nof]['#ValidConfigs']/result[nof]['#Configs'] * 100
        result[nof]['#Strategy'] = 'Real distribution'

        write_results(nof, result[nof])   
    
    return result


def get_random_configuration_with_nof(fm: 'FeatureModel', nof: int) -> 'FMConfiguration':
    """Find a random configuration of the feature model with the specific number of features."""
    config = FMConfiguration(elements={})
    possible_features = [f for f in fm.get_features()]
    while len(config.get_selected_elements()) < nof:
        random_feature = random.choice(possible_features)
        possible_features.remove(random_feature)
        config.add_element(random_feature)
    return config

def calculate_montecarlo_probabilities(fm: 'FeatureModel', simulations: int) -> dict:
    """Calculate the probabilities of finding valid configurations using montecarlo trivial simulations."""
    features = fm.get_features()
    n_features = len(features)
    aafms = AAFMsHelper(fm)

    result = {}   
    print(f"step: ", end='', flush=True)  
    for nof in range(n_features+1):   
        print(f"{nof},", end='', flush=True) 
        n_valid_configs = 0
        valid_configs = set()
        for _ in range(simulations):
            config = get_random_configuration_with_nof(fm, nof)
            if aafms.is_valid_configuration(config):
                valid_configs.add(config)
                n_valid_configs += 1
        result[nof] = {}
        result[nof]['#Configs'] = len(list(itertools.combinations(features, nof)))
        result[nof]['#ValidConfigs'] = n_valid_configs
        result[nof]['#ValidDistinctConfigs'] = len(valid_configs)
        result[nof]['#Simulations'] = simulations
        result[nof]['#Evaluations'] = simulations
        result[nof]['Probability'] = result[nof]['#ValidConfigs']/result[nof]['#Simulations'] * 100
        result[nof]['#Strategy'] = "Random (" + str(simulations) + ")"

        write_results(nof, result[nof])
    
    return result


def get_montecarlo_configuration(montecarlo_algorithm: 'MonteCarlo', initial_state: 'State') -> 'FMConfiguration':
    state = initial_state 
    while not state.is_terminal():
        state = montecarlo_algorithm.run(state)
    return state.configuration

def calculate_mtcs_probabilities(fm: 'FeatureModel', simulations: int, mcts_iterations: int, mcts_ew: float, actions: 'ActionsList') -> dict:
    features = fm.get_features()
    n_features = len(features)
    aafms = AAFMsHelper(fm)
    problem_data = ProblemData(fm, aafms, actions)

    result = {}  
    print(f"step: ", end='', flush=True)  
    for nof in range(n_features+1):    
        print(f"{nof},", end='', flush=True)
        problem_data.n_features = nof
        n_valid_configs = 0
        valid_configs = set()
        for _ in range(simulations):
            mcts = MonteCarloAlgorithms.uct_iterations_maxchild(mcts_iterations, mcts_ew)
            initial_state = NFeaturesConfigurationState(FMConfiguration(elements={}), problem_data)
            config = get_montecarlo_configuration(mcts, initial_state)
            if aafms.is_valid_configuration(config):
                valid_configs.add(config)
                n_valid_configs += 1
        result[nof] = {}
        result[nof]['#Configs'] = len(list(itertools.combinations(features, nof)))
        result[nof]['#ValidConfigs'] = n_valid_configs
        result[nof]['#ValidDistinctConfigs'] = len(valid_configs)
        result[nof]['#Simulations'] = simulations
        result[nof]['#Evaluations'] = mcts_iterations * nof * simulations
        result[nof]['Probability'] = result[nof]['#ValidConfigs']/result[nof]['#Simulations'] * 100
        result[nof]['#Strategy'] = str(mcts) + "(" + str(result[nof]['#Evaluations']) + ")"

        write_results(nof, result[nof])

    return result


def plot_valid_configurations(fig, data):
    fig.set_title("Valid configurations with N features")
    fig.set_xlabel("N features")
    fig.set_ylabel("#Valid distinct confis")

    x = list(data.keys())
    #valid_configs = [data[nof]['#ValidConfigs'] for nof in data]
    y = [data[nof]['#ValidDistinctConfigs'] for nof in data]
    
    fig.plot(x, y, label=data[0]['#Strategy'])
    # text = [str(data[nof]['#Evaluations']) for nof in data]
    # for i, t in enumerate(text):
    #     fig.annotate(t, (x[i], y[i]))
    fig.legend(loc="best")

def plot_features_probabilities(fig, data):
    fig.set_title("Probability of finding a valid configuration with N features")
    fig.set_xlabel("N features")
    fig.set_ylabel("Probability (%)")

    x_values = list(data.keys())
    #valid_configs = [data[nof]['#ValidConfigs'] for nof in data]
    y_values = [data[nof]['Probability'] for nof in data]

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
        
    fig.plot(x_values, y_values, label=data[0]['#Strategy'])
    fig.legend(loc="best")

def plot_results(lof_results: list):
    fig, axs = plt.subplots(2, 2)
    for results in lof_results:
        plot_features_probabilities(axs[0,0], results)
    
    for results in lof_results:
        plot_valid_configurations(axs[0,1], results)

    fig.tight_layout()
    plt.show()

def main():
    with open(OUTPUT_RESULTS_FILE, 'w+') as file:
        file.write(', '.join(HEADER_OUTPUT_FILE)+'\n')

    input_fm = INPUT_PATH + input_fm_name + ".xml"
    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    print(f"#Features: {len(fm.get_features())}")
    print(f"#Relations: {len(fm.get_relations())}")
    print(f"#Constraints: {len(fm.get_constraints())}")

    aafms = AAFMsHelper(fm)
    configurations = aafms.get_configurations()
    products = aafms.get_products()
    print(f"#Valid configs: {len(configurations)}")
    print(f"#Valid products: {len(products)}")
    print(f"Search space size: {2**len(fm.get_features())}")
    print(f"Probability of finding a valid config randomly (1/2^|F|): {1/2**len(fm.get_features()) * 100} %")


    print("Calculating real probabilities.")
    r1 = calculate_real_probabilities(fm, configurations)
    print("\nCalculating MonteCarlo probabilities.")
    r2 = calculate_montecarlo_probabilities(fm, simulations=1000)
    print("\nCalculating MCTS probabilities.")
    actions = RandomActionsList(fm)
    r3 = calculate_mtcs_probabilities(fm, simulations=100, mcts_iterations=100, mcts_ew=0.5, actions=actions)
    print("\nCalculating MCTS probabilities.")
    actions = TreeActionsList(fm)
    r4 = calculate_mtcs_probabilities(fm, simulations=100, mcts_iterations=100, mcts_ew=0.5, actions=actions)
    
    print()

    plot_results([r1, r2, r3, r4])

if __name__ == '__main__':
    main()
