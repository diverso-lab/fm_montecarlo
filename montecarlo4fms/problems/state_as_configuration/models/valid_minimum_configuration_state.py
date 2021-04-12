from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState


class ValidMinimumConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return ValidMinimumConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        n = len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())
        #n = len(self.configuration.get_selected_elements())
        if not self.is_valid_configuration:
            return -(n*n)
        return n

    