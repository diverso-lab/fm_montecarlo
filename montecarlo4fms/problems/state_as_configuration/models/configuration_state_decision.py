import random
from abc import abstractmethod
from montecarlo4fms.models import State
from famapy.metamodels.fm_metamodel.models import FMConfiguration

PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']

class ConfigurationStateDecision(State):

    def __init__(self, configuration: 'FMConfiguration', decision: 'Feature', data: 'ProblemData'):
        if decision and not configuration.contains(decision):
            raise Exception("The decision feature must be included in the configuration.")
        self.configuration = configuration
        self.decision = decision
        self.data = data
        self.hash_value = None
        self.successors = []
        self.applicable_actions = []
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        #self.errors = None

    def find_successors(self) -> list:
        if not self.successors:
            if not self.configuration.get_selected_elements():
                root = self.data.fm.root
                self.successors = [ConfigurationStateDecision(FMConfiguration({root: True}), root, self.data)]
                return self.successors

            successors = []
            if self.decision:
                config_elements = self.configuration.get_selected_elements()
                for r in self.decision.get_relations():
                    if r.is_or():
                        possible_features = (set(r.children) - config_elements)
                        if possible_features:
                            for f in possible_features:
                                new_config = self.configuration.clone()
                                new_config.add_element(f)
                                new_state = ConfigurationStateDecision(new_config, None, self.data)
                                successors.append(new_state)
                    else:
                        if not any(c in config_elements for c in r.children):
                            random_child = random.choice(r.children)
                            new_config = self.configuration.clone()
                            new_config.add_element(random_child)
                            new_state = ConfigurationStateDecision(new_config, None, self.data)
                            successors.append(new_state)

            if not successors: # Either because there is not decision or there is not successors for the decision
                config_elements = self.configuration.get_selected_elements()
                for feature in config_elements:
                    for r in feature.get_relations():
                        if r.is_or():
                            possible_features = (set(r.children) - config_elements)
                            if possible_features:
                                for f in possible_features:
                                    new_config = self.configuration.clone()
                                    new_config.add_element(f)
                                    new_state = ConfigurationStateDecision(new_config, None, self.data)
                                    successors.append(new_state)
                        else:
                            if not any(c in config_elements for c in r.children):
                                random_child = random.choice(r.children)
                                new_config = self.configuration.clone()
                                new_config.add_element(random_child)
                                new_state = ConfigurationStateDecision(new_config, None, self.data)
                                successors.append(new_state)

            self.successors = successors
        return self.successors

    def find_random_successor(self) -> 'State':
        return random(self.find_successors())

    def state_transition_function(self, action: 'Action') -> 'State':
        pass

    def get_actions(self) -> list:
        pass

    def __hash__(self) -> int:
        if not self.hash_value:
            self.hash_value = hash(tuple(self.configuration.get_selected_elements()))
        return self.hash_value

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)

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

    # def count_errors(self) -> int:
    #     packages_with_errors = []
    #     linux_feature = self.data.fm.get_feature_by_name("Linux")
    #     win_feature = self.data.fm.get_feature_by_name("Win")
    #     if linux_feature in self.configuration.get_selected_elements():
    #         packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
    #     elif win_feature in self.configuration.get_selected_elements():
    #         packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_WIN]
    #     return len(packages_with_errors)
