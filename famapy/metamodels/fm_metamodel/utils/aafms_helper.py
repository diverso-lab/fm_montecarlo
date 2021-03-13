from typing import List, Set

from pysat.solvers import Glucose3

from famapy.metamodels.fm_metamodel.models import FMConfiguration
from famapy.metamodels.pysat_metamodel.transformations import FmToPysat


class AAFMsHelper:

    def __init__(self, feature_model: 'FeatureModel'):
        self.feature_model = feature_model
        transform = FmToPysat(feature_model)
        self.cnf_model = transform.transform()
        self.formula = [clause for clause in self.cnf_model.cnf] # caching the clauses of the feature model

    def is_valid_configuration(self, config: 'Configuration') -> bool:
        if not self.feature_model or not self.feature_model.root:
            return not config

        g = Glucose3()
        g.append_formula(self.formula)
        config_names = [feature.name for feature in config.elements if config.elements[feature]]
        formula = [[clause[0]] if clause[1] in config_names else [-clause[0]] for clause in self.cnf_model.features.items()]
        g.append_formula(formula)
        valid = g.solve()
        g.delete()
        return valid

    def is_valid_partial_configuration(self, config: 'Configuration') -> bool:
        g = Glucose3()
        g.append_formula(self.formula)
        config_selected_names = [feature.name for feature in config.elements if config.elements[feature]]
        config_unselected_names = [feature.name for feature in config.elements if not config.elements[feature]]
        assumptions = [self.cnf_model.variables[name] for name in config_selected_names]
        assumptions.extend(-1*[self.cnf_model.variables[name] for name in config_unselected_names])
        valid = g.solve(assumptions=assumptions)
        g.delete()
        return valid

    # def is_valid_partial_selection(self, selected_features: Set['Feature'], unselected_features: Set['Feature']) -> bool:
    #     g = Glucose3()
    #     g.append_formula(self.formula)
    #     config_selected_names = [feature.name for feature in selected_features]
    #     config_unselected_names = [feature.name for feature in unselected_features]
    #     assumptions = [self.cnf_model.variables[name] for name in config_selected_names]
    #     assumptions.extend([-1*self.cnf_model.variables[name] for name in config_unselected_names])
    #     return g.solve(assumptions=assumptions)

    def get_configurations(self) -> List['FMConfiguration']:
        g = Glucose3()
        g.append_formula(self.formula)
        configurations = []
        for solutions in g.enum_models():
            elements = dict()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    feature = self.feature_model.get_feature_by_name(self.cnf_model.features.get(variable))
                    elements[feature] = True
            config = FMConfiguration(elements=elements)
            configurations.append(config)
        g.delete()
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
