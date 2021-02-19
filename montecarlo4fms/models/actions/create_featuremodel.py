from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State, Action
from famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation

class CreateFeatureModel(Action):

    def get_name(self) -> str:
        return "Create feature model"

    def execute(self, feature_model: FeatureModel) -> List[FeatureModel]:
        return [FeatureModel(None)]
