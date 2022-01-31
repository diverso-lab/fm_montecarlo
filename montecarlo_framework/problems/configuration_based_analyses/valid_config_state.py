from montecarlo_framework.models import Problem 

from montecarlo_framework.models.feature_model import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses import ConfigurationState


class ValidConfigurationState(ConfigurationState):

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return ValidConfigurationState(configuration)

    def heuristic(self) -> float:
        return 0

    def reward(self) -> float:
        return 1 if self.configuration.is_valid_configuration() else -1


class FindAllValidConfigurationState(ValidConfigurationState):

    def __init__(self, configuration: FMConfiguration, problem: Problem = None) -> None:
        super().__init__(configuration)
        self.problem = problem

    def set_problem(self, problem: Problem) -> None:
        self.problem = problem

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return FindAllValidConfigurationState(configuration, self.problem)

    def reward(self) -> float:
        if self.configuration in self.problem.get_solutions():
            return float("-inf")
        return super().reward()


class CompletionPartialConfigProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Completion of partial configuration'

    def __init__(self, initial_state: ConfigurationState):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> ConfigurationState:
        return self.initial_state
