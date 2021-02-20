from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from montecarlo4fms.problems.reverse_engineering.models import StateFM
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation
import famapy.metamodels.fm_metamodel.utils.fm_utils as fm_utils
import copy


class AddOptionalFeature(Action):

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
        return "Add optional feature (" + self.parent_name + "->" + self.feature_name + ")"

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
        return StateFM(fm, state.configurations)
