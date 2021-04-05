from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState
#from montecarlo4fms.problems.state_as_configuration.actions import SelectRandomFeature
from evaluation.jhipster import jhipster


class FailureConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.failures = None
        self.evaluated = False
        self.z = None

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return FailureConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        #return (self.is_valid_configuration and self.configuration not in self.data.sample) or not self.get_actions()
        return self.is_valid_configuration or not self.find_successors()

    def reward(self) -> float:
        if self.z is None:
            if not self.is_valid_configuration:
                z = -1
            elif self.data.sample[self]:
                z = -1
            else:
                #jhipster_config = jhipster.filter_configuration(self.configuration, self.data.jhipster_configurations)
                #self.failures = jhipster.contains_failures(jhipster_config)
                z = 1 if self.data.jhipster_configurations[self.configuration] else -1
                self.evaluated = True
            self.z = z
        return self.z

    # def get_actions(self) -> list:
    #     select_random_feature_action = SelectRandomFeature(self.data.fm)
    #     if not select_random_feature_action.is_applicable(self.configuration):
    #         self.applicable_actions = []
    #     else:
    #         self.applicable_actions = [select_random_feature_action]
    #     return self.applicable_actions
