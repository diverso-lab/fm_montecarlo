from montecarlo_framework.models import Problem 

from montecarlo_framework.models.feature_model import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses import ConfigurationState, ValidConfigurationState


class ValidMinimumConfigurationState(ValidConfigurationState):

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return ValidMinimumConfigurationState(configuration)

    def reward(self) -> float:
        n = len(self.configuration.fm.fm_model.get_features()) - len(self.configuration.get_selected_features())
        if not self.configuration.is_valid_configuration():
            return -(n*n)
        return n


class FindAllValidMinimumConfigurationState(ValidConfigurationState):

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return FindAllValidMinimumConfigurationState(configuration, self.problem)


class ValidMinConfigProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Valid minimum configuration'

    def __init__(self, initial_state: ConfigurationState):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> ConfigurationState:
        return self.initial_state
