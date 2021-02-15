from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from .fm_godelization import FMGodelization
from pysat.solvers import Glucose3
from pysat_metamodel.famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat_metamodel.famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from typing import Set

class FMHelper:

    def __init__(self, feature_model: FeatureModel):
        self.feature_model = feature_model
        self.features = self.feature_model.features
        self.features_by_name = {f.name : f for f in self.features}

        #sat = PySATModel()
        transform = FmToPysat(feature_model)
        self.cnf_model = transform.transform()
        self.fm_godelization = FMGodelization(feature_model)
        self.formula = []

        # Add clauses of the feature model
        for clause in self.cnf_model.cnf:  # AC es conjunto de conjuntos
            self.formula.append(clause)  # añadimos la constraint

    def is_valid_configuration(self, config: Configuration) -> bool:
        g = Glucose3()
        g.append_formula(self.formula)
        config_names = [feature.name for feature in config.elements]
        formula = [[clause[0]] if clause[1] in config_names else [-clause[0]] for clause in self.cnf_model.features.items()]
        g.append_formula(formula)

        return g.solve()

    def is_valid_partial_configuration(self, config: Configuration) -> bool:
        g = Glucose3()
        g.append_formula(self.formula)
        config_names = [feature.name for feature in config.elements]
        assumptions = [self.cnf_model.variables[name] for name in config_names]
        return g.solve(assumptions=assumptions)

    def is_valid_partial_selection(self, selected_features: Set[Feature], unselected_features: Set[Feature]) -> bool:
        g = Glucose3()
        g.append_formula(self.formula)
        config_selected_names = [feature.name for feature in selected_features]
        config_unselected_names = [feature.name for feature in unselected_features]
        assumptions = [self.cnf_model.variables[name] for name in config_selected_names]
        assumptions.extend([-1*self.cnf_model.variables[name] for name in config_unselected_names])
        return g.solve(assumptions=assumptions)

    def get_configurations(self) -> Set[Feature]:
        g = Glucose3()
        g.append_formula(self.formula)
        configurations = []
        for solutions in g.enum_models():
            config = list()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    config.append(self.cnf_model.features.get(variable))
            configurations.append(config)
        return configurations

    def get_core_features(self) -> Set[Feature]:
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
