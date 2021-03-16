import random
from abc import abstractmethod
from montecarlo4fms.models import State

PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']

class ConfigurationStateDecision(State):

    def __init__(self, configuration: 'FMConfiguration', feature: 'Feature', data: 'ProblemData'):
        self.configuration = configuration
        self.feature = feature
        self.data = data
        self.hash_value = None
        self.successors = []
        self.applicable_actions = []
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.errors = None

    def find_successors(self) -> list:
        if not self.successors:
            successors = []
            for a in self.get_actions():
                configurations = a.executions(self.configuration)
                for c in configurations:
                    feature = (c.get_selected_elements() - self.configuration.get_selected_elements()).pop()
                    new_state = self.configuration_transition_function(c, feature)
                    successors.append(new_state)
            self.successors = successors
        return self.successors

    def find_random_successor(self) -> 'State':
        action = random.choice(self.get_actions())
        config = action.execute(self.configuration)
        feature = (config.get_selected_elements() - self.configuration.get_selected_elements()).pop()
        return self.configuration_transition_function(config, feature)

    def configuration_transition_function(self, config: 'FMConfiguration', feature: 'Feature') -> 'State':
        return ConfigurationStateDecision(config, feature, self.data)

    def get_actions(self) -> list:
        if not self.applicable_actions:
            applicable_actions = []
            if not self.configuration.get_selected_elements():
                applicable_actions.extend(self.data.actions.get_actions()[None])

            elif self.feature:
                applicable_actions.extend([a for a in self.data.actions.get_actions()[self.feature]['Mandatory'] if a.is_applicable(self.configuration)])
                applicable_actions.extend([a for a in self.data.actions.get_actions()[self.feature]['Optional'] if a.is_applicable(self.configuration)])

            if not applicable_actions:
                for feature in self.configuration.get_selected_elements():
                    applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Mandatory'] if a.is_applicable(self.configuration)])
                    applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Optional'] if a.is_applicable(self.configuration)])

            self.applicable_actions = applicable_actions
        return self.applicable_actions

    def state_transition_function(self, action: 'Action') -> 'State':
        config = action.execute(self.configuration)
        feature = (config.get_selected_elements() - self.configuration.get_selected_elements()).pop()
        return self.configuration_transition_function(config, feature)

    def __hash__(self) -> int:
        if not self.hash_value:
            t = (tuple(self.configuration.get_selected_elements()), self.feature)
            self.hash_value = hash(t)
        return self.hash_value

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration and s1.feature == s2.feature

    def __str__(self) -> str:
        return str(self.configuration) + "Decision: " + str(self.feature)

    def is_terminal(self) -> bool:
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        else:
            return len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())    
        # if not self.is_valid_configuration:
        #     return -1
        # if not self.errors:
        #     self.errors = self.count_errors()
        # if self.errors <= 0:
        #     return -1
        #
        # n = len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())
        # return n * self.errors

    def count_errors(self) -> int:
        packages_with_errors = []
        linux_feature = self.data.fm.get_feature_by_name("Linux")
        win_feature = self.data.fm.get_feature_by_name("Win")
        if linux_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
        elif win_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_WIN]
        return len(packages_with_errors)
