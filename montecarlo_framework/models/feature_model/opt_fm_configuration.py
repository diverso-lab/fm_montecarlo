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
            self.bdd_model = None
        self._features_by_name = {f.name: f for f in self.fm_model.get_features()}
        self.solver = Glucose3()
        for clause in self.sat_model.get_all_clauses():  
            self.solver.add_clause(clause)
    
    def get_feature_by_name(self, feature_name: str) -> Optional[Feature]:
        return self._features_by_name.get(feature_name)

    def is_valid_partial_configuration(self, partial_configuration: 'FMConfiguration') -> bool:
        return self.solver.solve(assumptions=partial_configuration.selected_variables)

    def is_valid_configuration(self, configuration: 'FMConfiguration') -> bool:
        variables = configuration.selected_variables + configuration.unselected_variables
        return self.solver.solve(assumptions=variables)
    
    def get_random_configuration(self, p_config: Configuration = None) -> Configuration:
        # Initialize the configurations and values for BDD nodes with already known features
        values = {} if p_config is None else {f.name: selected for f, selected in p_config.elements.items()}
        features = {} if p_config is None else {f: selected for f, selected in p_config.elements.items()}

        # Set the BDD nodes with the already known features values
        u_func = self.bdd_model.bdd.let(values, self.bdd_model.root)

        care_vars = set(self.bdd_model.variables) - values.keys()
        n_vars = len(care_vars)
        for feature in care_vars:
            # Number of configurations with the feature selected
            v_sel = self.bdd_model.bdd.let({feature: True}, u_func)
            nof_configs_var_selected = self.bdd_model.bdd.count(v_sel, nvars=n_vars - 1)
            # Number of configurations with the feature unselected
            v_unsel = self.bdd_model.bdd.let({feature: False}, u_func)
            nof_configs_var_unselected = self.bdd_model.bdd.count(v_unsel, nvars=n_vars - 1)

            # Randomly select or not the feature
            selected = random.choices([True, False], 
                                    [nof_configs_var_selected, nof_configs_var_unselected], 
                                    k=1)[0]

            # Update configuration and BDD node for the new feature
            values[feature] = selected
            u_func = self.bdd_model.bdd.let({feature: selected}, u_func)
            features[self.get_feature_by_name(feature)] = selected

            n_vars -= 1
        return FMConfiguration(Configuration(features), self)


class FMConfiguration():

    def __init__(self,
                 fm: FM,
                 selected_features: list[Feature] = None,
                 unselected_features: list[Feature] = None,
                 selected_variables: list[int] = None,
                 unselected_variables: list[int] = None,
                 open_features: list[Feature] = None,
                 configurable_features: list[Feature] = None):
        self.fm = fm
        self.selected_features = [*selected_features] if selected_features else [] 
        self.unselected_features = [*unselected_features] if unselected_features else [] 
        self.selected_variables = [*selected_variables] if selected_variables else [] 
        self.unselected_variables = [*unselected_variables] if unselected_variables else []
        self.open_features = [*open_features] if open_features else self._get_open_features()
        self.configurable_features = [*configurable_features] if configurable_features else self._get_configurable_features() 
    
    @classmethod
    def from_configuration(cls, config: 'FMConfiguration', feature: Feature = None) -> 'FMConfiguration':
        new_config = cls(fm=config.fm, 
                         selected_features=config.selected_features,
                         unselected_features=config.unselected_features,
                         selected_variables=config.selected_variables,
                         unselected_variables=config.unselected_variables,
                         configurable_features=config.configurable_features,
                         open_features=config.open_features)
        if feature is not None:
            new_config.add_feature(feature)
        return new_config

    def _get_open_features(self) -> list[Feature]:
        """Open features are those whose children can be selected to form a valid configuration."""
        open_features = []
        for feature in self.selected_features:
            if any(not child in self.selected_features and self.is_valid_partial_configuration_with_feature(child) for child in feature.get_children()):
                open_features.append(feature)
        return open_features

    def _get_configurable_features(self) -> list[Feature]:
        """Configurable features are those features that can be selected to form a valid 
        configuration from the already selected features following the tree structure of the 
        feature model top-down.
        """
        configurable_features = []
        if not self.selected_features:
            configurable_features.append(self.fm.fm_model.root)
        else:
            for feature in self.open_features:
                children = feature.get_children()
                for child in children:
                    if not child in self.selected_features and self.is_valid_partial_configuration_with_feature(child):
                        configurable_features.append(child)
        return configurable_features

    def get_selected_features(self) -> list[Feature]:
        return self.selected_features

    def get_configurable_features(self) -> list[Feature]:
        return self.configurable_features

    def add_feature(self, feature: Feature) -> None:
        self.selected_features.append(feature)
        self.unselected_features.remove(feature)
        self.selected_variables.append(self.fm.sat_model.variables[feature.name])
        self.unselected_variables.remove(-self.fm.sat_model.variables[feature.name])
        if any(not child in self.selected_features and self.is_valid_partial_configuration_with_feature(child) for child in feature.get_children()):
            self.open_features.append(feature)
        self.configurable_features = self._get_configurable_features()
    
    def remove_feature(self, feature: Feature) -> None:
        self.selected_features.remove(feature)
        self.unselected_features.append(feature)
        self.selected_variables.remove(self.fm.sat_model.variables[feature.name])
        self.unselected_variables.append(-self.fm.sat_model.variables[feature.name])
        if feature in self.open_features:
            self.open_features.remove(feature)
        parent = feature.get_parent()
        if (parent is not None and parent not in self.open_feature and 
            any(not child in self.selected_features and self.is_valid_partial_configuration_with_feature(child) for child in parent.get_children())):
                self.open_features.append(feature)
        self.configurable_features = self._get_configurable_features()

    def is_valid_partial_configuration(self) -> bool:
        return self.fm.is_valid_partial_configuration(self)

    def is_valid_partial_configuration_with_feature(self, feature) -> bool:
        self.selected_variables.append(self.fm.sat_model.variables[feature.name])
        valid = self.is_valid_partial_configuration()
        self.selected_variables.remove(self.fm.sat_model.variables[feature.name])
        return valid

    def is_valid_configuration(self) -> bool:
        return self.fm.is_valid_configuration(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FMConfiguration):
            return (set(self.selected_features) == set(other.selected_features))
        return False

    def __hash__(self) -> int:
        return hash((frozenset(self.selected_features)))

    def __str__(self) -> str:
        return str([str(f) for f in self.selected_features])


    # def _open_closed_configurable_features(self) -> tuple[list[Feature], list[Feature], list[Feature]]:
    #     """Returns the list of open features, closed features, and configurable features.
        
    #     - Open features are those whose children can be selected to form a valid configuration.
    #     - Closed features are those whose children have been already selected in the 
    #     configuration or cannot be added to form a valid configuration.
    #     - Configurable features are those features that can be selected to form a valid 
    #     configuration from the already selected features following the tree structure of the 
    #     feature model top-down.
    #     """
    #     open_features = []
    #     closed_features = []
    #     configurable_features = []
    #     selected_features = self.get_selected_features()
    #     if not selected_features:
    #         open_features = []
    #         closed_features = []
    #         configurable_features.append(self.fm.fm_model.root)
    #     else:
    #         for feature in selected_features:
    #             children = feature.get_children()
    #             closed = True
    #             for child in children:
    #                 if not child in selected_features and self.is_valid_partial_configuration_with_feature(child):
    #                     closed = False
    #                     configurable_features.append(child)
    #             if closed:
    #                 closed_features.append(feature)
    #             else:
    #                 open_features.append(feature)
    #     return (open_features, closed_features, configurable_features)
