import random
from abc import abstractmethod
from montecarlo4fms.models import State


PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']


class VPState(State):

    def __init__(self, configuration: 'FMConfiguration', feature_vp: 'Feature', data: 'ProblemData'):
        self.configuration = configuration
        self.feature_vp = feature_vp
        self.data = data
        self._hash_value = None
        self._successors = None
        self.errors = None
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)

    def find_successors(self) -> list:
        if self._successors is None:
            successors = []
            if self.feature_vp is not None:
                for r in self.feature_vp.get_relations():
                    possible_features = (set(r.children) - self.configuration.get_selected_elements())
                    if possible_features:
                        for f in possible_features:
                            new_config = self.configuration.clone()
                            new_config.add_element(f)
                            if self.data.aafms.is_valid_partial_configuration(new_config):
                                new_state = VPState(new_config, None, self.data)
                                successors.append(new_state)
            else:
                for feature in self.configuration.get_selected_elements():
                    for r in feature.get_relations():
                        possible_features = set(r.children) - self.configuration.get_selected_elements()
                        if possible_features:
                            for f in possible_features:
                                new_config = self.configuration.clone()
                                new_config.add_element(f)
                                if self.data.aafms.is_valid_partial_configuration(new_config):
                                    new_state = VPState(new_config, None, self.data)
                                    successors.append(new_state)
            self._successors = successors
        return self._successors

    def find_random_successor(self) -> 'State':
        if self.feature_vp is not None:
            relations = self.feature_vp.get_relations()
            random.shuffle(relations)
            for r in relations:
                possible_features = list(set(r.children) - self.configuration.get_selected_elements())
                if possible_features:
                    random.shuffle(possible_features)
                    for f in possible_features:
                        new_config = self.configuration.clone()
                        new_config.add_element(f)
                        if self.data.aafms.is_valid_partial_configuration(new_config):
                            return VPState(new_config, None, self.data)
        else:
            features = list(self.configuration.get_selected_elements())
            random.shuffle(features)
            for feature in features:
                relations = feature.get_relations()
                random.shuffle(relations)
                for r in relations:
                    possible_features = list(set(r.children) - self.configuration.get_selected_elements())
                    if possible_features:
                        random.shuffle(possible_features)
                        for f in possible_features:
                            new_config = self.configuration.clone()
                            new_config.add_element(f)
                            if self.data.aafms.is_valid_partial_configuration(new_config):
                                return VPState(new_config, None, self.data)

    def state_transition_function(self, action: 'Action') -> 'State':
        pass

    def get_actions(self) -> list:
        pass

    def is_terminal(self) -> bool:
        return self.is_valid_configuration or self._successors == []

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        if self.errors is None:
            self.errors = self.count_errors()
            self.evaluated = True
        if self.errors <= 0:
            return -1
        return self.errors

    def count_errors(self) -> int:
        packages_with_errors = []
        linux_feature = self.data.fm.get_feature_by_name("Linux")
        win_feature = self.data.fm.get_feature_by_name("Win")
        if linux_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
        elif win_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_WIN]
        return len(packages_with_errors)

    def __hash__(self) -> int:
        if self._hash_value is None:
            self._hash_value = hash(self.configuration)
        return self._hash_value

    def __eq__(self, other: 'State') -> bool:
        return self.configuration == other.configuration

    def __str__(self) -> str:
        return str(self.configuration)
