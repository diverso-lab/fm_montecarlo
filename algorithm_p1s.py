import time
import argparse

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper, FMGodelization

from montecarlo4fms.algorithms import MonteCarloAlgorithms

from montecarlo4fms.problems.state_as_configuration.actions import ActionsList
from montecarlo4fms.problems.state_as_configuration.models import DefectiveConfigurationState
from montecarlo4fms.problems import ProblemData

from experiments_config import INPUT_PATH, OUTPUT_RESULTS_FILE


def algorithm(montecarlo, initial_state):
    n = 0
    state = initial_state
    print(f"step: ", end='', flush=True)
    while not state.is_terminal(): #state.reward() <= 0 and state.get_actions():
        print(f"{n},", end='', flush=True)
        state = montecarlo.run(state)
        n += 1
    print("Done!")
    return montecarlo, state

def main(input_fm_name, run, iterations, exploration_weight):
    print("Problem 1 (simulated): Finding defective configurations.")
    print("-----------------------------------------------")

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
    initial_config = FMConfiguration(elements=dict())
    initial_state = DefectiveConfigurationState(configuration=initial_config, data=problem_data)
    print(f"Initial state: {initial_state}")

    print("Problem setted up.")

    print(f"Configuring MonteCarlo algorithm...")
    montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=iterations, exploration_weight=exploration_weight)
    print(f"{type(montecarlo).__name__} with {iterations} iterations, and {exploration_weight} exploration weight.")

    print("Running algorithm...")
    start = time.time()
    montecarlo, state = algorithm(montecarlo, initial_state)
    end = time.time()
    print(f"Result state: {state}")

    print(f"Writing results to file {OUTPUT_RESULTS_FILE}...")
    with open(OUTPUT_RESULTS_FILE, 'a+') as file:
        file.write(f"{run}, {type(montecarlo).__name__}, {iterations}, {end-start}, {len(state.configuration.elements)}, {state.is_valid_configuration}, {state.reward()}, {len(montecarlo.tree)}, {str([str(f) for f in state.configuration.get_selected_elements()])}\n")

    print("Finished!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Problem 1 (simulated): Finding defective configurations.')
    parser.add_argument('-r', '--run', dest='run', type=int, required=True, help='Number of the run.')
    parser.add_argument('-it', '--iterations', dest='iterations', type=int, required=True, help='Number of iterations for MCTS.')
    parser.add_argument('-ew', '--exploration_weight', dest='exploration_weight', type=float, required=True, help='Exploration weight constant for UCT MCTS.')
    parser.add_argument('-fm', '--feature_model',  dest='feature_model', type=str, required=True, help='Input feature model name located in folder "input_fms/" in FeatureIDE format (.xml).')
    args = parser.parse_args()

    main(input_fm_name=args.feature_model, run=args.run, iterations=args.iterations, exploration_weight=args.exploration_weight)
