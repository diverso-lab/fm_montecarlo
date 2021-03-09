from montecarlo4fms.problems.state_as_configuration.models import ValidConfigurationState


class ValidMinimumConfigurationState(ValidConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return ValidMinimumConfigurationState(config, self.data)

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        n = len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())
        return n
