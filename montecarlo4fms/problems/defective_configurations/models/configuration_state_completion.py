import random
from typing import List

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action


class ActivateFeature(Action):
    """
    Add a feature to the configuration.
    """

    def __init__(self, feature: Feature):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Activate feature"

    def __str__(self) -> str:
        return "Act " + str(self.feature)

    def execute(self, state: 'State') -> 'State':
        elements = {f: state.configuration.elements[f] for f in state.configuration.elements}
        elements[self.feature] = True
        return ConfigurationStateCompletion(FMConfiguration(elements), state.feature_model, state.aafms_helper, state.required_features)


class ConfigurationStateCompletion(State):
    """
    A state is a configuration.
    """

    def __init__(self, configuration: FMConfiguration, feature_model: FeatureModel, aafms_helper: AAFMsHelper = None, required_features: List['Feature'] = []):
        self.configuration = configuration
        self.feature_model = feature_model
        self.actions = []
        if aafms_helper:
            self.aafms_helper = aafms_helper
        else:
            self.aafms_helper = AAFMsHelper(feature_model)
        self.is_valid_configuration = self.aafms_helper.is_valid_configuration(self.configuration)
        self.required_features = required_features
        self.contains_required_features = all((self.configuration.contains(f) for f in self.required_features))
        self.hash_value = None

    def find_random_successor(self) -> 'State':
        if not self.configuration.elements:
            return ActivateFeature(self.feature_model.root).execute(self)

        relations = self._get_undecided_mandatory_relations()
        if not relations:
            relations = self._get_undecided_optional_relations()
        random_relation = random.choice(relations)
        features = self._get_undecided_features_for_relation(random_relation)
        random_feature = random.choice(features)
        return ActivateFeature(random_feature).execute(self)

    def get_actions(self) -> list:
        if self.actions:
            return self.actions

        if not self.configuration.elements:
            self.actions = [ActivateFeature(self.feature_model.root)]
            return self.actions

        actions = []
        undecided_mandatory_relations = self._get_undecided_mandatory_relations()
        if undecided_mandatory_relations:
            # Esta implementación toma la decisión de cada feature como una única configuración (permite analizar feature a feature)
            # La configuración solo se incrementa de 1 en 1 feature en feature.
            for relation in undecided_mandatory_relations:
                undecided_features = self._get_undecided_features_for_relation(relation)
                actions.extend([ActivateFeature(f) for f in undecided_features])

            # Esta implementación toma todas las decisiones obligatorias en una única configuración
            # for relation in undecided_mandatory_relations:
            #     successors_for_relation = self._get_successors_for_relation(relation)
            #     # Successors of mandatory features needs to be mixed.
            #     if not successors:
            #         successors = successors_for_relation
            #     else:
            #         new_successors = []
            #         for s in successors:
            #             for ns in successors_for_relation:
            #                 new_successors.append(ConfigurationState(self.fm_helper, list(dict.fromkeys(s.elements + ns.elements))))
            #         successors = new_successors

        else: # optionals
            undecided_optional_relations = self._get_undecided_optional_relations()
            for relation in undecided_optional_relations:
                undecided_features = self._get_undecided_features_for_relation(relation)
                actions.extend([ActivateFeature(f) for f in undecided_features])

        self.actions = actions
        return self.actions

    def _get_undecided_features_for_relation(self, relation: 'Relation') -> List['Feature']:
        """List of undecided features of the given relation. That is, features that have not been already selected in the configuration."""
        if not relation.children:
            return []
        elif relation.is_mandatory() or relation.is_optional():
            return relation.children
        elif relation.is_alternative():
            return relation.children
        elif relation.is_or():
            return [child for child in relation.children if child not in self.configuration.elements]
        else: # n..m group cardinality
            return [child for child in relation.children if child not in self.configuration.elements]

    def _get_undecided_mandatory_relations(self) -> List['Relation']:
        """Undecided mandatory relations are those relation that needs to be decided in order to move closer to the next configuration according to the tree hierarchy."""
        res = []
        for feature in self.configuration.elements:
            for r in feature.get_relations():
                if (r.is_mandatory() and r.children[0] not in self.configuration.elements) or (r.is_alternative() and not any(child in self.configuration.elements for child in r.children)) or (r.is_or() and not any(child in self.configuration.elements for child in r.children)):
                    res.append(r)
        return res

    def _get_undecided_optional_relations(self) -> List['Relation']:
        """Undecided optional relations are those relations that may be decided (but not required by the tree hierarchy) in order to move closer to the next configuration."""
        res = []
        for feature in self.configuration.elements:
            for r in feature.get_relations():
                if (r.is_optional() and r.children[0] not in self.configuration.elements) or (r.is_or() and any(child not in self.configuration.elements for child in r.children)):
                    res.append(r)
        return res

    def is_terminal(self) -> bool:
        return (self.contains_required_features and self.is_valid_configuration) or not self.get_actions()

    def reward(self) -> float:
        if not self.contains_required_features:
             return -1
        if not self.is_valid_configuration:
             return -1
        n = len(self.feature_model.get_features()) - len(self.configuration.elements)
        return n

        #n = len(self.feature_model.get_features()) - len(self.configuration.elements)
        #return n if self.is_valid_configuration and self.contains_required_features else -1

    def __hash__(self) -> int:
        if not self.hash_value:
            self.hash_value = hash(tuple(self.configuration.elements.items()))
        return self.hash_value

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
