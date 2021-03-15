import time
from typing import List

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper, fm_utils
from montecarlo4fms.problems import Problem, ProblemData
from montecarlo4fms.problems.state_as_configuration.actions import ActionsList
from montecarlo4fms.algorithms import MonteCarloTreeSearch


class ConfigurationProblem(Problem):

    def __init__(self, input_fm_filepath: str, initial_configuration_features: List['str']):
        self.initial_state = self.problem_configuration(input_fm_filepath, initial_configuration_features)
        self.result_state = None
        self.stats = dict()

    def problem_configuration(self, input_fm_filepath: str, initial_configuration_features: List['str']):
        print(f"Setting up problem '{self.get_problem_name()}'...")

        print(f"Loading feature model: {input_fm_filepath} ...")
        fide_parser = FeatureIDEParser(input_fm_filepath)
        fm = fide_parser.transform()
        print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

        print(f"Transforming to CNF model...")
        aafms = AAFMsHelper(fm)
        #print(f"CNF model with {len(aafms.formula)} clauses.")

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

        initial_state = self.get_state_type()(configuration=initial_config, data=problem_data)
        print(f"Initial state: {initial_state}")
        print("Problem setted up.")
        return initial_state

    def solve(self):
        print(f"Running algorithm...")
        n = 0
        state = self.get_initial_state()
        print(f"step: ", end='', flush=True)
        start_time = time.time()
        while not state.is_terminal(): #state.reward() <= 0 and state.get_actions():
            print(f"{n},", end='', flush=True)
            state = self.get_montecarlo_algorithm().run(state)
            n += 1
        end_time = time.time()
        print("Done!")
        self.result_state = state
        self.stats['AlgorithmSteps'] = n
        self.stats['ExecutionTime'] = end_time - start_time

    def get_initial_state(self):
        return self.initial_state

    def get_result_state(self):
        if not self.result_state:
            raise Exception("Call the solve() method first.")
        return self.result_state

    def get_stats(self):
        if not self.get_result_state():
            raise Exception("Call the solve() method first.")

        self.stats['Algorithm'] = str(self.get_montecarlo_algorithm())
        self.stats['StoppingCondition'] = self.get_montecarlo_algorithm().stopping_condition.get_value()
        self.stats['ValidConfiguration'] = self.get_result_state().is_valid_configuration
        self.stats['Reward'] = self.get_result_state().reward()
        self.stats['#Features'] = len(self.get_result_state().configuration.get_selected_elements())
        self.stats['#TotalIterationsExecuted'] = self.get_montecarlo_algorithm().get_iterations_executed()
        self.stats['Configuration'] = str([str(f) for f in self.get_result_state().configuration.get_selected_elements()])
        if isinstance(self.get_montecarlo_algorithm(), MonteCarloTreeSearch):
            self.stats['#TotalNodes'] = sum(len(nodes) for nodes in self.get_montecarlo_algorithm().tree.values()) + 1 # the initial node
            self.stats['#NodesExplored'] = len(self.get_montecarlo_algorithm().tree.keys())
        else:
            self.stats['#TotalNodes'] = 0
            self.stats['#NodesExplored'] = 0


        return self.stats
