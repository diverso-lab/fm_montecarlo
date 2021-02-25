import copy
import random
from abc import abstractmethod

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action


class SelectFeature(Action):
    """
    Add a feature to the configuration along with its tree dependencies.
    """

    def __init__(self, feature: Feature):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Select normal feature"

    def __str__(self) -> str:
        return "Select feature " + str(self.feature)

    def execute(self, state: 'State') -> 'State':
        configuration = copy.deepcopy(state.configuration)
        configuration.elements[self.feature] = True
        self.select_mandatory_children(self.feature, configuration)
        self.select_parents(self.feature, configuration)
        return ConfigurationState(configuration, state.feature_model)

    def select_mandatory_children(self, feature: Feature, configuration: FMConfiguration):
        """Add mandatory children recursively to the configuration."""
        features = [feature]
        while features:
            f = features.pop()
            mandatory_children = [r.children[0] for r in f.get_relations() if r.is_mandatory() and (r.children[0] not in configuration.elements or not configuration.elements[r.children[0]])]
            features.extend(mandatory_children)
            for child in mandatory_children:
                configuration.elements[child] = True
            # Add a random child in case of group features.
            group_children = next((r.children for r in f.get_relations() if r.is_or() or r.is_alternative()), None)
            if group_children and not any(c for c in group_children if c in configuration.elements and configuration.elements[c]):
                random_children = random.choice(group_children)
                configuration.elements[random_children] = True
                features.append(random_children)

    def select_parents(self, feature: Feature, configuration: FMConfiguration):
        """Add parent features recursively to the configuration."""
        parent = feature.get_parent()
        while parent and (parent not in configuration.elements or not configuration.elements[parent]):
            configuration.elements[parent] = True
            self.select_mandatory_children(parent, configuration)
            parent = parent.get_parent()


# class SelectGroupFeature(SelectFeature):
#     """
#     Add an or-group or alternative-group feature to the configuration along with its tree dependencies.
#     """
#
#     @staticmethod
#     def get_name() -> str:
#         return "Select group feature"
#
#     def __str__(self) -> str:
#         return "Select group " + self.feature
#
#     def execute(self, state: 'State') -> 'State':
#         configuration = copy.deepcopy(state.configuration)
#         configuration.elements[self.feature] = True
#         children = next(r.children for r in self.feature.get_relations() if r.is_or() or r.is_alternative())
#         random_children = random.choice(children)
#         configuration.elements[random_children] = True
#         self.select_mandatory_children(random_children, configuration)
#         self.select_parents(self.feature, configuration)
#         return ConfigurationState(configuration, state.feature_model)


class DeselectFeature(Action):
    """
    Remove a feature from the configuration along with all its tree dependencies.
    """

    def __init__(self, feature: Feature):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Deselect feature"

    def __str__(self) -> str:
        return "Deselect feature " + str(self.feature)

    def execute(self, state: 'State') -> 'State':
        configuration = copy.deepcopy(state.configuration)
        configuration.elements[self.feature] = False
        self.deselect_children(self.feature, configuration)
        self.deselect_mandatory_parents(self.feature, configuration)
        return ConfigurationState(configuration, state.feature_model)

    def deselect_children(self, feature: Feature, configuration: FMConfiguration):
        """Remove children recursively to the configuration."""
        features = [feature]
        while features:
            f = features.pop()
            children = []
            for relation in f.get_relations():
                children.extend([c for c in relation.children if c in configuration.elements or configuration.elements[c]])
            features.extend(children)
            for child in children:
                configuration.elements[child] = False

    def deselect_mandatory_parents(self, feature: Feature, configuration: FMConfiguration):
        """Remove parents of the feature if the feature is mandatory."""
        parent = feature.get_parent()
        while parent and parent in configuration.elements and configuration.elements[parent]:
            children = [r.children[0] for r in parent.get_relations() if r.is_mandatory()]
            if feature in children:
                configuration.elements[parent] = False
                feature = parent
                parent = parent.get_parent()
            else:
                parent = None


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

    def find_successors(self) -> list:
        """All possible successors of this state."""
        return [a.execute(self) for a in self.get_actions()]

    def find_random_successor(self) -> 'State':
        """Random successor of this state (redefine it for more efficient simulation)."""
        return random.choice(self.get_actions()).execute(self)

    def get_actions(self) -> list:
        if self.actions:
            return self.actions

        actions = []

        core_features = self.aafms_helper.get_core_features()
        activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        deactivatable_candidate_features = [f for f in self.feature_model.get_features() if f not in activatable_candidate_features and f not in core_features]

        for feature in activatable_candidate_features:
            # Filter simbling features of alternative-groups already activated
            parent = feature.get_parent()
            if parent and fm_utils.is_alternative_group(parent):
                children = next(r.children for r in parent.get_relations() if r.is_alternative())
                if feature in children and not any(c for c in children if c in self.configuration.elements and self.configuration.elements[c]):
                    actions.append(SelectFeature(feature))
            else:
                actions.append(SelectFeature(feature))

        for feature in deactivatable_candidate_features:
            actions.append(DeselectFeature(feature))

        self.actions = actions
        return self.actions


    def is_terminal(self) -> bool:
        """A configuration is terminal if it is valid."""
        # self.n = 1
        # valid = self.aafms_helper.is_valid_configuration(self.configuration)
        # print(f"Config: {valid} -> {[str(f) for f in self.configuration.elements]}")
        # if self.n == 2:
        #     raise Exception
        return self.aafms_helper.is_valid_configuration(self.configuration)

    def reward(self) -> float:
        return 1 if self.aafms_helper.is_valid_configuration(self.configuration) else 0

    def __hash__(self) -> int:
        return hash(self.configuration)

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
