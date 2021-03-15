from typing import Dict

from montecarlo4fms.problems.state_as_configuration.actions import SelectRootFeature, SelectMandatoryFeature, SelectOptionalFeature, SelectAlternativeFeature, SelectOrFeature, SelectRandomFeature


class ActionsList():

    def __init__(self, feature_model: 'FeatureModel'):
        self._actions = self._build_actions_random(feature_model)

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

    def _build_actions_random(self, fm: 'FeatureModel') -> Dict['Feature', 'Action']:
        actions_dict = dict()

        for feature in fm.get_features():
            if feature == fm.root:
                actions_dict[None] = [SelectRandomFeature(fm)]

            actions_for_optional_relations = [SelectRandomFeature(fm)]

            new_dict = {'Mandatory': [], 'Optional': actions_for_optional_relations}
            actions_dict[feature] = new_dict

        return actions_dict

    def get_nof_actions(self) -> int:
        return sum(len(a) for a in self._actions.values())
