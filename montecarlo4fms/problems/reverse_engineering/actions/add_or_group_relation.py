from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation
import famapy.metamodels.fm_metamodel.utils.fm_utils as fm_utils
import copy


class AddOrGroupRelation(Action):

    def __init__(self, feature_name1: str, feature_name2: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2

    def get_name(self) -> str:
        return "Add or group"

    def execute(self, feature_model: FeatureModel) -> List[FeatureModel]:
        features = feature_model.get_features()
        if not features:
            return []
        fms = []
        for candidate_parent in features:
            if not fm_utils.is_group(candidate_parent):
                fm = copy.deepcopy(feature_model)
                parent = fm.get_feature_by_name(candidate_parent.name)

                parent_relation1 = Relation(parent=parent, children=[], card_min=0, card_max=0)
                child1 = Feature(self.feature_name1, [parent_relation1])
                parent_relation2 = Relation(parent=parent, children=[], card_min=0, card_max=0)
                child2 = Feature(self.feature_name2, [parent_relation2])

                alternative_relation = Relation(parent=parent, children=[child1, child2], card_min=1, card_max=2)
                parent.add_relation(alternative_relation)

                fm.features.extend([child1, child2])
                fm.relations.extend([parent_relation1, parent_relation2, alternative_relation])
                fm.features_by_name[child1.name] = child1
                fm.features_by_name[child2.name] = child2
                fms.append(fm)
        return fms
