import copy

from famapy.metamodels.fm_metamodel.models import Feature, Relation

from montecarlo4fms.models import Action
from montecarlo4fms.problems.reverse_engineering.models import FMState


class AddRootFeature(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
        return "Add root feature " + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        relation = Relation(parent=None, children=[], card_min=0, card_max=0)
        root_feature = Feature(self.feature_name, [relation])
        fm.root = root_feature
        fm.features = [root_feature]
        fm.relations = [relation]
        return FMState(fm, state.configurations)
