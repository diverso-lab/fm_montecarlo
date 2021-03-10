import time
import argparse
import cProfile
from typing import Callable, List

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper, FMGodelization, fm_utils

from montecarlo4fms.algorithms import MonteCarloAlgorithms

from montecarlo4fms.problems.state_as_configuration.actions import ActionsList
from montecarlo4fms.problems.state_as_configuration.models import DefectiveConfigurationState
from montecarlo4fms.problems import ProblemData

from experiments_config import INPUT_PATH, OUTPUT_RESULTS_FILE

input_fm_name = "wget"
iterations = 10
exploration_weight = 0.5
initial_configuration_features = []


def problem1():
    print("Problem 1 (simulated): Finding defective configurations.")
    print("-----------------------------------------------")



def algorithm(montecarlo, initial_state):
    print(f"Running algorithm with {str(montecarlo)}...")
    n = 0
    state = initial_state
    print(f"step: ", end='', flush=True)
    while not state.is_terminal(): #state.reward() <= 0 and state.get_actions():
        print(f"{n},", end='', flush=True)
        state = montecarlo.run(state)
        n += 1
    print("Done!")
    return montecarlo, state, n

def run_problem(run: int, montecarlo, initial_state):
    print(f"Running problem...")
    start = time.time()
    montecarlo, state, n = algorithm(montecarlo, initial_state)
    end = time.time()
    print(f"Result state: {state}")

    print(f"Writing results to file {OUTPUT_RESULTS_FILE}...")
    with open(OUTPUT_RESULTS_FILE, 'a+') as file:
        file.write(f"{run}, {str(montecarlo)}, {montecarlo.stopping_condition.get_value()}, {end-start}, {len(state.configuration.elements)}, {state.is_valid_configuration}, {state.reward()}, {len(montecarlo.tree)}, {iterations*n}, {str([str(f) for f in state.configuration.get_selected_elements()])}\n")

    print("Finished!")

def problem_configuration(input_fm_name: str, iterations: int, exploration_weight: float, initial_configuration_features: List['str'], state_type: Callable, montecarlo_algorithm: Callable):
    print("Setting up the problem...")

    input_fm = INPUT_PATH + input_fm_name + ".xml"

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    print(f"Transforming to CNF model...")
    aafms = AAFMsHelper(fm)
    print(f"CNF model with {len(aafms.formula)} clauses.")

    print(f"Creating set of actions...")
    actions = ActionsList(fm)
    print(f"{actions.get_nof_actions()} actions.")

    problem_data = ProblemData(fm, aafms, actions)

    print(f"Creating initial state (configuration)...")
    if initial_configuration_features:
        print(f"|-> Parsing features...")
        list_features = [fm.get_feature_by_name(f) for f in initial_configuration_features]
        print(f"|-> Auto-selecting parents of features...")
        selections = list_features.copy()
        for f in list_features:
            selections.extend(fm_utils.select_parent_features(f))
        selections.extend(list_features)
        initial_config = FMConfiguration(elements={s: True for s in selections})
    else:
        initial_config = FMConfiguration(elements=dict())

    initial_state = state_type(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print(f"Configuring MonteCarlo algorithm...")
    montecarlo = montecarlo_algorithm(iterations=iterations, exploration_weight=exploration_weight)

    print("Problem setted up.")

    return montecarlo, initial_state

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem 1 (simulated): Finding defective configurations.')
    parser.add_argument('-r', '--run', dest='run', type=int, required=True, help='Number of the run.')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=True, help='Number of iterations for MCTS.')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=True, help='Exploration weight constant for UCT MCTS.')
    parser.add_argument('-fm', '--feature_model',  dest='feature_model', type=str, required=True, help='Input feature model name located in folder "input_fms/" in FeatureIDE format (.xml).')
    args = parser.parse_args()

    main(input_fm_name=args.feature_model, run=args.run, iterations=args.iterations, exploration_weight=args.exploration_weight)
