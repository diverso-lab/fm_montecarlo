from montecarlo_framework.models import Problem
from montecarlo_framework.models.feature_model import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses import ConfigurationState
from montecarlo_framework.problems.configuration_based_analyses import jhipster_utils


class JHipsterDefectiveConfigurationState(ConfigurationState):

    def __init__(self, configuration: FMConfiguration, problem: Problem = None) -> None:
        super().__init__(configuration)
        self.problem = problem

    def set_problem(self, problem: Problem) -> None:
        self.problem = problem

    def heuristic(self) -> float:
        return 0

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return JHipsterDefectiveConfigurationState(configuration, self.problem)

    def reward(self) -> float:
        if not self.configuration.is_valid_configuration():
            return -1
        elif self.configuration in self.problem.sample:
            return -1
        else:
            return 1 if self.problem.jhipster_configurations[self.configuration] else -1


class JHipsterFindingDefectiveConfigProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Finding defective configurations in the JHipster'

    def __init__(self, initial_state: ConfigurationState):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> ConfigurationState:
        return self.initial_state