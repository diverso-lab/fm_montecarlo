from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState


class NFeaturesConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return NFeaturesConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        return len(self.configuration.get_selected_elements()) == self.data.n_features or not self.get_actions()

    def reward(self) -> float:
        return 1 if self.is_valid_configuration else -1
