import random
import itertools
from functools import reduce
from typing import Set, List

from montecarlo4fms.models import State, Action
from montecarlo4fms.problems.reverse_engineering.models.actions import CreateFeatureModel, AddRootFeature, AddOptionalFeature
from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, FMConfiguration
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
import famapy.metamodels.fm_metamodel.utils.fm_utils as fm_utils

class StateFM(State):
    """
    S: The set of states is the set of all possible feature models for a given set of features.
    A: The set of valid actions are:
        - add a root feature to the empty feature model.
        - add a mandatory feature.
        - add an optional feature.
        - add a new or-group with two features.
        - add a new and-group with two features.
        - add a feature to an existing or-group or and-group.
        - add a requires constraint between two existing features.
        - add a excludes constraint between two existing features.
    Terminal State: a feature model is terminal if contain all features in the given set of features.
    """

    def __init__(self, feature_model: FeatureModel, configurations: Set[FMConfiguration]):
        self.feature_model = feature_model
        self.configurations = configurations
        self.missing_features = self._extract_features_from_configurations() - set(self.feature_model.get_features())
        self.actions = None

    # def find_successors(self) -> List['StateFM']:
    #     actions = self.get_actions()
    #     successors = []
    #     for a in actions:
    #         models = a.execute(self.feature_model)
    #         for fm in models:
    #             new_successor = StateFM(fm, self.configurations)
    #             successors.append(new_successor)
    #     return successors

    # def find_random_successor(self) -> 'StateFM':
    #     random_action = random.choice(self.get_actions())
    #     fms = random_action.execute(self.feature_model)
    #     random_fm = random.choice(fms)
    #     return StateFM(random_fm, self.configurations)

    def get_actions(self) -> List[Action]:
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
                    #actions.append(AddMandatoryFeature(feature.name))

        # Add feature to existing group
        # if any(fm_utils.is_or_group(f) for f in self.feature_model.get_features()):
        #     for feature in self.missing_features:
        #         actions.append(AddFeatureToOrGroup(feature.name))
        # if any(fm_utils.is_alternative_group(f) for f in self.feature_model.get_features()):
        #     for feature in self.missing_features:
        #         actions.append(AddFeatureToAlternativeGroup(feature.name))

        # Add group relation (two features)
        # if len(self.missing_features) > 1:
        #     combinations = itertools.combinations(self.missing_features, 2)
        #     for f1, f2 in combinations:
        #         actions.append(AddOrGroupRelation(f1.name, f2.name))
        #         actions.append(AddAlternativeGroupRelation(f1.name, f2.name))
        return actions

    def is_terminal(self) -> bool:
        return not self.missing_features

    def reward(self) -> float:
        if not self.feature_model or not self.feature_model.root:
            return 0
        aafms_helper = AAFMsHelper(self.feature_model)
        configurations = aafms_helper.get_configurations()
        # reward = 0
        # print("-----")
        # for c in configurations:
        #     print(f"new config: {[str(f) for f in c]}")
        #
        # for c in self.configurations:
        #     print(f"original config: {[str(f) for f in c]}")
        #     if c in configurations:
        #         print("Bingo!!")
        #         reward += 1
        # print("-----")
        # raise Exception
        n = reduce(lambda count, c: count + (c in configurations), self.configurations, 0)
        return n

    def _extract_features_from_configurations(self) -> Set[Feature]:
        features = set()
        for c in self.configurations:
            features.update(c.elements)
        return features

    def __hash__(self) -> int:
        return hash(self.feature_model)

    def __eq__(s1: 'StateFM', s2: 'StateFM') -> bool:
        return s1.feature_model == s2.feature_model

    def __str__(self) -> str:
        return str(self.feature_model)
