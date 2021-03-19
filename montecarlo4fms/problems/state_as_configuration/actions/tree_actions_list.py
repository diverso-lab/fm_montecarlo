from typing import Dict

from montecarlo4fms.problems.state_as_configuration.actions import SelectRootFeature, SelectMandatoryFeature, SelectOptionalFeature, SelectAlternativeFeature, SelectOrFeature
from montecarlo4fms.problems.state_as_configuration.actions import ActionsList

class TreeActionsList(ActionsList):
    """List of actions following the tree hierarchy structure of the feature model."""
    
    def __init__(self, feature_model: 'FeatureModel'):
        self._actions = self._build_actions(feature_model)

    def get_actions(self) -> Dict['Feature', 'Action']:
        return self._actions

    def _build_actions(self, fm: 'FeatureModel') -> Dict['Feature', 'Action']:
        actions_dict = dict()

        for feature in fm.get_features():
            if feature == fm.root:
                actions_dict[None] = [SelectRootFeature(feature)]

            actions_for_mandatory_relations = []
            actions_for_optional_relations = []
            if any(r.is_mandatory() for r in feature.get_relations()):
                actions_for_mandatory_relations.append(SelectMandatoryFeature(feature))
            if any(r.is_optional() for r in feature.get_relations()):
                actions_for_optional_relations.append(SelectOptionalFeature(feature))
            if any(r.is_alternative() for r in feature.get_relations()):
                actions_for_mandatory_relations.append(SelectAlternativeFeature(feature))
            if any(r.is_or() for r in feature.get_relations()):
                actions_for_optional_relations.append(SelectOrFeature(feature))

            new_dict = {'Mandatory': actions_for_mandatory_relations, 'Optional': actions_for_optional_relations}
            actions_dict[feature] = new_dict

        return actions_dict