from collections.abc import Iterable
from enum import Enum, auto 

from famapy.core.models import Configuration
from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from famapy.metamodels.fm_metamodel.operations import get_core_features


class RelationType(Enum):
    OPTIONAL = auto()
    MANDATORY = auto()
    ALTERNATIVE = auto()
    OR = auto()
    GROUP_CARDINALITY = auto()


def initialize_configuration(fm: FeatureModel, 
                             features_names: list[str]) -> Configuration:
    features = {fm.get_feature_by_name(f): True for f in features_names}
    return Configuration(elements=features)


def select_parent_features(feature: Feature) -> list[Feature]:
    features = []
    parent = feature.get_parent()
    while parent:
        features.append(parent)
        parent = parent.get_parent()
    return features


def initialize_configuration_with_core_features(fm: FeatureModel) -> Configuration:
    features = {f: True for f in get_core_features(fm)}
    return Configuration(elements=features)


def get_open_features(configuration: Configuration) -> Iterable[Feature]:
    return [f 
            for feature in configuration.elements 
                for f in feature.get_children() 
                    if f not in configuration.elements or not configuration.elements[f]]


def get_features_hash_table(fm: FeatureModel) -> dict[Feature, dict[RelationType, list[Feature]]]:
    result = {}
    for feature in fm.get_features():
        children = {}
        for relation in feature.get_relations():
            optionals, mandatories, alternatives, ors, cardinalities = [], [], [], [], []
            
            if relation.is_optional():
                optionals.append(relation.children)
            if relation.is_mandatory():
                mandatories.append(relation.children)
            if relation.is_alternative():
                alternatives.append(relation.children)
            if relation.is_or():
                ors.append(relation.children)
            else:
                cardinalities.append(relation.children)

        children[RelationType.MANDATORY] = optionals
        children[RelationType.MANDATORY] = mandatories
        children[RelationType.ALTERNATIVE] = alternatives
        children[RelationType.OR] = ors
        children[RelationType.GROUP_CARDINALITY] = cardinalities
        result[feature] = children
    return result
