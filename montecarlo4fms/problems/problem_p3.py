from typing import List
from montecarlo4fms.problems import ConfigurationProblem
from montecarlo4fms.problems.state_as_configuration.models import ValidMinimumConfigurationState

class Problem3(ConfigurationProblem):

    def __init__(self, input_fm_filepath: str, initial_configuration_features: List['str'], montecarlo_algorithm):
        super().__init__(input_fm_filepath, initial_configuration_features)
        self.montecarlo_algorithm = montecarlo_algorithm

    def get_problem_name(self):
        return "Completion of partial configurations"

    def get_montecarlo_algorithm(self):
        return self.montecarlo_algorithm

    def get_state_type(self):
        return ValidMinimumConfigurationState
