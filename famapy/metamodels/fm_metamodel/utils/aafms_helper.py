from typing import List, Set

from pysat.solvers import Glucose3

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.pysat_metamodel.transformations import FmToPysat


class AAFMsHelper:

    def __init__(self, feature_model: 'FeatureModel'):
        self.feature_model = feature_model
        transform = FmToPysat(feature_model)
        self.cnf_model = transform.transform()
        self.variables = {value: key for (key, value) in self.cnf_model.features.items()}
        self.solver = Glucose3()
        self.solver.append_formula(self.cnf_model.cnf)

    def is_valid_configuration(self, config: 'Configuration') -> bool:
        if not self.feature_model or not self.feature_model.root:
            return not config

        variables = [value if self.feature_model.get_feature_by_name(feature_name) in config.get_selected_elements() else -value for (feature_name, value) in self.variables.items()]
        return self.solver.solve(assumptions=variables)

    def is_valid_partial_configuration(self, config: 'Configuration') -> bool:
        variables = [self.variables[feature.name] if selected else -self.variables[feature.name] for (feature, selected) in config.elements.items()]
        return self.solver.solve(assumptions=variables)

    def get_configurations(self) -> List['FMConfiguration']:
        configurations = []
        for solutions in self.solver.enum_models():
            elements = dict()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    feature = self.feature_model.get_feature_by_name(self.cnf_model.features.get(variable))
                    elements[feature] = True
            config = FMConfiguration(elements=elements)
            configurations.append(config)
        return configurations

    def get_core_features(self) -> Set['Feature']:
        if not self.feature_model.root:  # void feature model
            return set()

        core_features = [self.feature_model.root]
        features = [self.feature_model.root]
        while features:
            f = features.pop()
            for relation in f.get_relations():
                if relation.is_mandatory():
                    core_features.extend(relation.children)
                    features.extend(relation.children)
        return set(core_features)
