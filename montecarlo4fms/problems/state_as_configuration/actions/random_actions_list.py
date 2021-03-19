from typing import Dict

from montecarlo4fms.problems.state_as_configuration.actions import SelectRandomFeature
from montecarlo4fms.problems.state_as_configuration.actions import ActionsList

class RandomActionsList(ActionsList):
    """List of random actions."""
    
    def __init__(self, feature_model: 'FeatureModel'):
        self._actions = self._build_actions(feature_model)

    def get_actions(self) -> Dict['Feature', 'Action']:
        return self._actions

    def _build_actions(self, fm: 'FeatureModel') -> Dict['Feature', 'Action']:
        actions_dict = dict()

        for feature in fm.get_features():
            if feature == fm.root:
                actions_dict[None] = [SelectRandomFeature(fm)]

            actions_for_optional_relations = [SelectRandomFeature(fm)]

            new_dict = {'Mandatory': [], 'Optional': actions_for_optional_relations}
            actions_dict[feature] = new_dict

        return actions_dict

