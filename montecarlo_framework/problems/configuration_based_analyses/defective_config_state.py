from montecarlo_framework.models import Problem
from montecarlo_framework.models.feature_model import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses import ConfigurationState


PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']


class DefectiveConfigurationState(ConfigurationState):

    def __init__(self, configuration: FMConfiguration, problem: Problem = None) -> None:
        super().__init__(configuration)
        self.problem = problem

    def set_problem(self, problem: Problem) -> None:
        self.problem = problem

    def heuristic(self) -> float:
        return 0

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return DefectiveConfigurationState(configuration, self.problem)

    def reward(self) -> float:
        if not self.configuration.is_valid_configuration():
            return -1
        else:
            nof_errors = self.count_errors()
            return nof_errors if nof_errors > 0 else -1

    def count_errors(self) -> int:
        packages_with_errors = []
        linux_feature = self.configuration.fm.get_feature_by_name("Linux")
        win_feature = self.configuration.fm.get_feature_by_name("Win")
        if linux_feature in self.configuration.get_selected_features():
            packages_with_errors = [f for f in self.configuration.get_selected_features() if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
        elif win_feature in self.configuration.get_selected_features():
            packages_with_errors = [f for f in self.configuration.get_selected_features() if f.name in PACKAGES_WITH_ERRORS_IN_WIN]
        return len(packages_with_errors)


class FindingDefectiveConfigProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Finding defective configurations in the AAFM Framework'

    def __init__(self, initial_state: ConfigurationState):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> ConfigurationState:
        return self.initial_state