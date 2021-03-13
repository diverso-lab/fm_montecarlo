import random
from abc import abstractmethod
from montecarlo4fms.problems.state_as_configuration.models import ValidConfigurationState
from montecarlo4fms.problems.state_as_configuration.actions import SelectRandomFeature


class RandomConfigurationState(ValidConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return RandomConfigurationState(config, self.data)

    def get_actions(self) -> list:
        select_random_feature_action = SelectRandomFeature(self.data.fm)
        if not select_random_feature_action.is_applicable(self.configuration):
            self.applicable_actions = []
        else:
            self.applicable_actions = [select_random_feature_action]
        return self.applicable_actions

    def is_terminal(self) -> bool:
        return self.data.nof_features == len(self.configuration.get_selected_elements()) or not self.get_actions()

    def reward(self) -> float:
        return 1 if self.is_valid_configuration else -1
