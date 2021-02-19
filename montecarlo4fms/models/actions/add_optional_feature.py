from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation
import famapy.metamodels.fm_metamodel.utils.fm_utils as fm_utils
import copy


class AddOptionalFeature(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
        return "Add optional feature"

    def execute(self, feature_model: FeatureModel) -> List[FeatureModel]:
        features = feature_model.get_features()
        if not features:
            return []
        fms = []
        for candidate_parent in features:
            if not fm_utils.is_group(candidate_parent):
                fm = copy.deepcopy(feature_model)
                parent = fm.get_feature_by_name(candidate_parent.name)
                parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
                feature = Feature(self.feature_name, [parent_relation])
                optional_relation = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
                parent.add_relation(optional_relation)
                fm.features.append(feature)
                fm.relations.extend([parent_relation, optional_relation])
                fm.features_by_name[feature.name] = feature
                fms.append(fm)
        return fms
