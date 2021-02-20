from famapy.metamodels.fm_metamodel.models import FeatureModel

from montecarlo4fms.models import Action
from montecarlo4fms.problems.reverse_engineering.models import FMState


class CreateFeatureModel(Action):

    def get_name(self) -> str:
        return "Create feature model"

    def execute(self, state: 'State') -> 'State':
        return FMState(FeatureModel(None), state.configurations)
