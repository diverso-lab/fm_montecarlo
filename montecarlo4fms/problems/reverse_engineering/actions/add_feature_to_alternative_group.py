from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation
import famapy.metamodels.fm_metamodel.utils.fm_utils as fm_utils
import copy


class AddFeatureToAlternativeGroup(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
        return "Add feature to alternative group"

    def execute(self, feature_model: FeatureModel) -> List[FeatureModel]:
        features = feature_model.get_features()
        if not features:
            return []
        fms = []
        for candidate_parent in features:
            if fm_utils.is_alternative_group(candidate_parent):
                fm = copy.deepcopy(feature_model)
                parent = fm.get_feature_by_name(candidate_parent.name)

                parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
                child = Feature(self.feature_name, [parent_relation])

                alternative_relation = next(r for r in parent.get_relations() if r.is_alternative())
                alternative_relation.add_child(child)

                fm.features.append(child)
                fm.relations.append(parent_relation)
                fm.features_by_name[child.name] = child
                fms.append(fm)
        return fms
