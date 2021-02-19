from famapy.metamodels.fm_metamodel.models import FeatureModel


class FMCoreFeatures(CoreFeatures):
    """This implementation assumes that:
     (1) there are not any dead-features in the model.
     (2) there are not any false-optional features in the model.

     These assumptions imply that there are not any cross-tree constraints
     involving the core-features, otherwise the model would contain
     dead-features (for 'excludes' constraints) and false-optional features
     (for 'requires' constraints).
     """

    def __init__(self):
        self.result = []

    def get_core_features(self) -> list['Feature']:
        return self.result

    def execute(self, model: FeatureModel) -> 'FMCoreFeatures':
        if not model.root:  # void feature model
            return self
            
        core_features = [model.root]
        features = [model.root]
        while features:
            f = features.pop()
            for relation in f.get_relations():
                if relation.is_mandatory():
                    core_features.extend(relation.children)
                    features.extend(relation.children)
        self.result = core_features
        return self
