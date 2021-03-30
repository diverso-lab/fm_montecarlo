import random
from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState
#from montecarlo4fms.problems.state_as_configuration.actions import SelectRandomFeature
from evaluation.jhipster import jhipster


class FailureCS(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.evaluated = False
        self.z = None
        self._successors = None

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return FailureCS(config, self.data)

    def is_terminal(self) -> bool:
        #return (self.is_valid_configuration and self not in self.data.sample) or not self.find_successors()
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        if self.z is None:
            if not self.is_valid_configuration:
                z = -1
            elif self in self.data.sample:
                z = -1
            else:
                #jhipster_config = jhipster.filter_configuration(self.configuration, self.data.jhipster_configurations)
                #self.failures = jhipster.contains_failures(jhipster_config)
                z = 1 if self.data.jhipster_configurations[self.configuration] else -1
                self.evaluated = True
            self.z = z
        return self.z

    def find_successors(self) -> list:
        if self._successors is None:
            successors = []
            if not self.configuration.get_selected_elements():
                new_config = self.configuration.clone()
                new_config.add_element(self.data.fm.root)
                new_state = self.configuration_transition_function(new_config)
                successors.append(new_state)
            else:
                for feature in self.configuration.get_selected_elements():
                    for relation in feature.get_relations():
                        for child in relation.children:
                            if not self.configuration.contains(child):
                                new_config = self.configuration.clone()
                                new_config.add_element(child)
                                if self.data.aafms.is_valid_partial_configuration(new_config):
                                    new_state = self.configuration_transition_function(new_config)
                                    successors.append(new_state)
            self._successors = successors
        return self._successors

    def find_random_successor(self) -> 'State':
        features = list(self.configuration.get_selected_elements())
        random.shuffle(features)
        if not features:
            new_config = self.configuration.clone()
            new_config.add_element(self.data.fm.root)
            return self.configuration_transition_function(new_config)
        else:
            for feature in features:
                for relation in feature.get_relations():
                    for child in relation.children:
                        if not self.configuration.contains(child):
                            new_config = self.configuration.clone()
                            new_config.add_element(child)
                            if self.data.aafms.is_valid_partial_configuration(new_config):
                                return self.configuration_transition_function(new_config)
        return None

    # def get_actions(self) -> list:
    #     select_random_feature_action = SelectRandomFeature(self.data.fm)
    #     if not select_random_feature_action.is_applicable(self.configuration):
    #         self.applicable_actions = []
    #     else:
    #         self.applicable_actions = [select_random_feature_action]
    #     return self.applicable_actions
