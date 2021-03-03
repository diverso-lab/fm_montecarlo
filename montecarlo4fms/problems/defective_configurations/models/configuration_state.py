import copy
import random
import subprocess
import os
from abc import abstractmethod

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action

PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']

class ActivateFeature(Action):
    """
    Add a feature to the configuration.
    """

    def __init__(self, feature: Feature):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Activate feature"

    def __str__(self) -> str:
        return "Act " + str(self.feature)

    def execute(self, state: 'State') -> 'State':
        #configuration = copy.deepcopy(state.configuration)
        elements = {f: state.configuration.elements[f] for f in state.configuration}
        elements[self.feature] = True
        return ConfigurationState(FMConfiguration(elements), state.feature_model)


class ConfigurationState(State):
    """
    A state is a configuration.
    """

    def __init__(self, configuration: FMConfiguration, feature_model: FeatureModel, aafms_helper: AAFMsHelper = None):
        self.configuration = configuration
        self.feature_model = feature_model
        self.actions = []
        if aafms_helper:
            self.aafms_helper = aafms_helper
        else:
            self.aafms_helper = AAFMsHelper(feature_model)
        self.undecided_features = list(set(self.feature_model.get_features()) - set(self.configuration.elements.keys()))
        self.is_valid_configuration = self.aafms_helper.is_valid_configuration(self.configuration)
        self.errors = None

    def find_random_successor(self) -> 'State':
        #activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        #feature = random.choice(activatable_candidate_features)
        feature = random.choice(self.undecided_features)
        return ActivateFeature(feature).execute(self)

    def get_actions(self) -> list:
        if self.actions:
            return self.actions

        actions = []
        activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        for feature in activatable_candidate_features:
            actions.append(ActivateFeature(feature))

        self.actions = actions
        return self.actions

    def is_terminal(self) -> bool:
        """A configuration is terminal if it is valid or no more features can be added."""
        return self.is_valid_configuration or not self.get_actions() #len([f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]) == 0 #self.get_actions()

    def reward(self) -> float:
        if self.errors:
            return self.errors
        if not self.is_valid_configuration:
            return -1

        packages_with_errors = []
        linux_feature = self.feature_model.get_feature_by_name("Linux")
        win_feature = self.feature_model.get_feature_by_name("Win")
        if linux_feature in self.configuration.elements:
            packages_with_errors = [f for f in self.configuration.elements if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
        elif win_feature in self.configuration.elements:
            packages_with_errors = [f for f in self.configuration.elements if f.name in PACKAGES_WITH_ERRORS_IN_WIN]

        return len(packages_with_errors)

    def __hash__(self) -> int:
        return hash(self.configuration)

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
