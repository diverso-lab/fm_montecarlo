from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState
from evaluation.jhipster import jhipster

class FailureConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.failures = None

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return FailureConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        return (self.is_valid_configuration and self.configuration not in self.data.sample) or not self.get_actions()

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        if self.configuration in self.data.sample:
            return -1
        if self.failures is None:
            jhipster_config = jhipster.filter_configuration(self.configuration, self.data.jhipster_configurations)
            self.failures = jhipster.contains_failures(jhipster_config)
        return 1 if self.failures else -1
