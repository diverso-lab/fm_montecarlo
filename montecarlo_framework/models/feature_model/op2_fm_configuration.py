import copy
import random
from typing import Optional 

from pysat.solvers import Glucose3

from famapy.core.models import Configuration
from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid_configuration import Glucose3ValidConfiguration
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid_product import Glucose3ValidProduct
from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from famapy.metamodels.bdd_metamodel.transformations.fm_to_bdd import FmToBDD


class FM(FeatureModel):
    """Helper for feature model analysis."""

    def __init__(self, fm: FeatureModel) -> None:
        self.fm_model = fm
        self.sat_model = FmToPysat(fm).transform()
        try:
            self.bdd_model = FmToBDD(fm).transform()
        except:
            print(f'The BDD model cannot be build for this feature model.')
            self.bdd_model = None
        self._features_by_name = {f.name: f for f in self.fm_model.get_features()}
        self.solver = Glucose3()
        for clause in self.sat_model.get_all_clauses():
            self.solver.add_clause(clause)
    
    def get_feature_by_name(self, feature_name: str) -> Optional[Feature]:
        return self._features_by_name.get(feature_name)

    def is_valid_partial_configuration(self, partial_configuration: 'FMConfiguration') -> bool:
        return self.solver.solve(assumptions=partial_configuration.get_selected_variables())

    def is_valid_configuration(self, configuration: 'FMConfiguration') -> bool:
        variables = configuration.get_selected_variables() + configuration.get_unselected_variables()
        return self.solver.solve(assumptions=variables)
    
    # Get random configuration using the BDD
    # def get_random_configuration(self, p_config: 'FMConfiguration' = None) -> Configuration:
    #     # Initialize the configurations and values for BDD nodes with already known features
    #     values = {} if p_config is None else {f.name: selected for f, selected in p_config.elements.items()}
    #     features = {} if p_config is None else {f: selected for f, selected in p_config.elements.items()}

    #     # Set the BDD nodes with the already known features values
    #     u_func = self.bdd_model.bdd.let(values, self.bdd_model.root)

    #     care_vars = set(self.bdd_model.variables) - values.keys()
    #     n_vars = len(care_vars)
    #     for feature in care_vars:
    #         # Number of configurations with the feature selected
    #         v_sel = self.bdd_model.bdd.let({feature: True}, u_func)
    #         nof_configs_var_selected = self.bdd_model.bdd.count(v_sel, nvars=n_vars - 1)
    #         # Number of configurations with the feature unselected
    #         v_unsel = self.bdd_model.bdd.let({feature: False}, u_func)
    #         nof_configs_var_unselected = self.bdd_model.bdd.count(v_unsel, nvars=n_vars - 1)

    #         # Randomly select or not the feature
    #         selected = random.choices([True, False], 
    #                                 [nof_configs_var_selected, nof_configs_var_unselected], 
    #                                 k=1)[0]

    #         # Update configuration and BDD node for the new feature
    #         values[feature] = selected
    #         u_func = self.bdd_model.bdd.let({feature: selected}, u_func)
    #         features[self.get_feature_by_name(feature)] = selected

    #         n_vars -= 1
    #     return FMConfiguration(Configuration(features), self)

class FMConfiguration(Configuration):

    def __init__(self,
                 fm: FM,
                 selected_features: list[Feature] = None,
                 unselected_features: list[Feature] = None,
                 selected_variables: list[int] = None,
                 unselected_variables: list[int] = None):
        self.fm = fm
        self._selected_features = [*selected_features] if selected_features else [] 
        self._unselected_features = [*unselected_features] if unselected_features else [] 
        self._selected_variables = [*selected_variables] if selected_variables else [] 
        self._unselected_variables = [*unselected_variables] if unselected_variables else []
        self._configurable_features = None
    
    def get_selected_features(self) -> list[Feature]:
        return self._selected_features

    def get_unselected_features(self) -> list[Feature]:
        return self._unselected_features
    
    def get_selected_variables(self) -> list[int]:
        return self._selected_variables
    
    def get_unselected_variables(self) -> list[int]:
        return self._unselected_variables

    @classmethod
    def from_configuration(cls, config: 'FMConfiguration') -> 'FMConfiguration':
        new_config = cls(fm=config.fm, 
                         selected_features=config._selected_features,
                         unselected_features=config._unselected_features,
                         selected_variables=config._selected_variables,
                         unselected_variables=config._unselected_variables)
        return new_config

    def get_configurable_features(self) -> list[Feature]:
        """Configurable features are those features that can be selected to form a valid 
        configuration from the already selected features following the tree structure of the 
        feature model top-down.
        """
        if self._configurable_features is not None:
            return self._configurable_features

        configurable_features = []
        if not self._selected_features:
            configurable_features.append(self.fm.fm_model.root)
        else:
            # we transverse only the shortest list of features for efficiency
            if len(self._selected_features) <= len(self._unselected_features):
                # configurable features are the valid children of the already selected features
                for feature in self._selected_features:
                    for relation in feature.get_relations():
                        if relation.is_mandatory():
                            child = relation.children[0]
                            if child not in self._selected_features:
                                configurable_features.append(child)
                        elif relation.is_optional():
                            child = relation.children[0]
                            if child not in self._selected_features:
                                configurable_features.append(child)
                        elif relation.is_or():
                            for child in relation.children:
                                if child not in self._selected_features:
                                    configurable_features.append(child)
                        elif relation.is_alternative():
                            if not any(c in self._selected_features for c in relation.children):
                                for child in relation.children:
                                    configurable_features.append(child)
            else:
                # configurable features are those valid features whose parent have been already selected
                for feature in self._unselected_features:
                    if feature.get_parent() in self._selected_features:
                        configurable_features.append(feature)
        self._configurable_features = configurable_features
        return configurable_features

    def add_feature(self, feature: Feature) -> None:
        self._selected_features.append(feature)
        self._unselected_features.remove(feature)
        self._selected_variables.append(self.fm.sat_model.variables[feature.name])
        self._unselected_variables.remove(-self.fm.sat_model.variables[feature.name])
        self._configurable_features = None
    
    def remove_feature(self, feature: Feature) -> None:
        self._selected_features.remove(feature)
        self._unselected_features.append(feature)
        self._selected_variables.remove(self.fm.sat_model.variables[feature.name])
        self._unselected_variables.append(-self.fm.sat_model.variables[feature.name])
        self._configurable_features = None

    def is_valid_partial_configuration(self) -> bool:
        return self.fm.is_valid_partial_configuration(self)

    def is_valid_partial_configuration_with_feature(self, feature) -> bool:
        self._selected_variables.append(self.fm.sat_model.variables[feature.name])
        valid = self.is_valid_partial_configuration()
        self._selected_variables.remove(self.fm.sat_model.variables[feature.name])
        return valid

    def is_valid_configuration(self) -> bool:
        return self.fm.is_valid_configuration(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FMConfiguration):
            return (set(self._selected_features) == set(other._selected_features))
        return False

    def __hash__(self) -> int:
        return hash((frozenset(self._selected_features)))

    def __str__(self) -> str:
        return str([str(f) for f in self._selected_features])
