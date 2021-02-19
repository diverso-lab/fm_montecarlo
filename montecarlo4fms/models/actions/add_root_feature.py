from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation

class AddRootFeature(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
        return "Add root feature"

    def execute(self, feature_model: FeatureModel) -> List[FeatureModel]:
        if feature_model.root:
            return []
        relation = Relation(parent=None, children=[], card_min=0, card_max=0)
        root_feature = Feature(self.feature_name, [relation])
        fm = FeatureModel(root_feature, [], [root_feature], [relation])
        return [fm]
