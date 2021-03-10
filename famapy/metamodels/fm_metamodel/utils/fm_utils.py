from famapy.metamodels.fm_metamodel.models import Feature


def is_or_group(feature: Feature) -> bool:
    return any(r.is_or() for r in feature.get_relations())

def is_alternative_group(feature: Feature) -> bool:
    return any(r.is_alternative() for r in feature.get_relations())

def is_group(feature: Feature) -> bool:
    return is_or_group(feature) or is_alternative_group(feature)

def select_parent_features(feature: Feature) -> list[Feature]:
    features = []
    parent = feature.get_parent()
    while parent:
        features.append(parent)
        parent = parent.get_parent()
    return features
