import copy
from typing import List, Set

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, FMConfiguration
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action
#from montecarlo4fms.problems.reverse_engineering.actions import CreateFeatureModel

class FMState(State):

    def __init__(self, feature_model: 'FeatureModel', configurations: Set['FMConfiguration']):
        self.feature_model = feature_model
        self.configurations = configurations
        self.missing_features = self._get_missing_features()

    def _get_missing_features(self):
        """Return the set of features in the configurations that are missing in the feature model."""
        features = set()
        for c in self.configurations:
            features.update({f for f in c.elements.keys() if c.elements[f]})
        if not self.feature_model:
            return features
        return features - set(self.feature_model.get_features())

    def get_actions(self) -> List['Action']:
        """Return the list of valid actions for this state."""
        if not self.feature_model:
            return [CreateFeatureModel()]

        if not self.feature_model.root:
            return [AddRootFeature(feature.name) for feature in self.missing_features]

        actions = []
        # Add simple feature
        for feature in self.missing_features:
            for candidate_parent in self.feature_model.get_features():
                if not fm_utils.is_group(candidate_parent):
                    actions.append(AddOptionalFeature(feature.name, candidate_parent.name))

        return actions

    def is_terminal(self) -> bool:
        """A state is terminal if the feature model contains all features from all configurations.
        That is, there are not missing features."""
        return not self.missing_features

    def reward(self) -> float:
        return 0

    def __hash__(self) -> int:
        return hash(self.feature_model)

    def __eq__(s1: 'FMState', s2: 'FMState') -> bool:
        return s1.feature_model == s2.feature_model

    def __str__(self) -> str:
        return str(self.feature_model)


class CreateFeatureModel(Action):

    def get_name(self) -> str:
        return "Create empty FM"

    def execute(self, state: 'State') -> 'State':
        return FMState(FeatureModel(None), state.configurations)


class AddRootFeature(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
        return "Add root " + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        relation = Relation(parent=None, children=[], card_min=0, card_max=0)
        root_feature = Feature(self.feature_name, [relation])
        fm.root = root_feature
        fm.features = [root_feature]
        fm.relations = [relation]
        fm.features_by_name[root_feature.name] = root_feature
        return FMState(fm, state.configurations)


class AddOptionalFeature(Action):

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
        return "Add optional (" + self.parent_name + "->" + self.feature_name + ")"

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        feature = Feature(self.feature_name, [parent_relation])
        optional_relation = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
        parent.add_relation(optional_relation)
        fm.features.append(feature)
        fm.relations.extend([parent_relation, optional_relation])
        fm.features_by_name[feature.name] = feature
        return FMState(fm, state.configurations)
