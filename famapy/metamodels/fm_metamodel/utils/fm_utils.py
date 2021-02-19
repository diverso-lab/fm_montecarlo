from famapy.metamodels.fm_metamodel.models import Feature

def is_or_group(feature: Feature) -> bool:
    return any(r.is_or() for r in feature.get_relations())

def is_alternative_group(feature: Feature) -> bool:
    return any(r.is_alternative() for r in feature.get_relations())

def is_group(feature: Feature) -> bool:
    return is_or_group(feature) or is_alternative_group(feature)
