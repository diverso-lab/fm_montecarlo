import copy
import random
from abc import abstractmethod

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action


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
        configuration = copy.deepcopy(state.configuration)
        configuration.elements[self.feature] = True
        return ConfigurationState(configuration, state.feature_model)


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
        self.is_valid_configuration = self.aafms_helper.is_valid_configuration(self.configuration)

    def find_random_successor(self) -> 'State':
        activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        feature = random.choice(activatable_candidate_features)
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
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        return 1 if self.is_valid_configuration else -1

    def __hash__(self) -> int:
        return hash(self.configuration)

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
