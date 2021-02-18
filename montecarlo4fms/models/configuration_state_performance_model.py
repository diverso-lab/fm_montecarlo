import random
import itertools
from typing import List
from .state import State
from famapy.core.models import Configuration
from famapy.core.discover import DiscoverMetamodels
from montecarlo4fms.utils import PerformanceModel
from fm_metamodel.famapy.metamodels.fm_metamodel.models import FMConfiguration

class ConfigurationState(Configuration, State):
    """
    It represents a configuration of a feature model as a state.
    Its successors are any possible selection of features where at least all mandatory decisions are covered, and maybe optional decisions are taken.
    A configuration is terminal if it has not possible successors.
    """

    def __init__(self, fm_helper: 'FMHelper', config_elements: List['Feature']):
        super().__init__(config_elements)
        self.fm_helper = fm_helper
        self.performance_model = PerformanceModel(fm_helper.feature_model)
        self.performance_model.load_configurations_from_csv('logging-performance.csv', ['Framework', 'Message Size (b)', 'Output'], 'Computational Time (s)')

    def find_successors(self) -> List['ConfigurationState']:
        """
        All possible successors of this configuration state.
        The successors of a configuration are:
        - (1) the configurations with the inmediate mandatory (undecided) features selected according to the tree structure following a top-down approach.
        - (2) in case there is not any inmediate mandatory features undecided, the configurations with the inmediate optional (undecided) feature according to the tree structure following a top-down approach.
        A successor of a configuration differs only in a feature selection.
        """
        if not self.elements:
            return [ConfigurationState(self.fm_helper, [self.fm_helper.feature_model.root])]

        successors = []
        features_selections = []
        undecided_mandatory_relations = self._get_undecided_mandatory_relations()
        if undecided_mandatory_relations:

            # Esta implementación toma la decisión de cada feature como una única configuración (permite analizar feature a feature)
            # La configuración solo se incrementa de 1 en 1 feature en feature.
            for relation in undecided_mandatory_relations:
                new_successors = self._get_successors_for_relation(relation)
                successors.extend(new_successors)

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
                new_successors = self._get_successors_for_relation(relation)
                successors.extend(new_successors)

        return successors

    def find_random_successor(self):
        """Random configuration successor of the configuration."""
        if not self.elements:
            return ConfigurationState(self.fm_helper, [self.fm_helper.feature_model.root])

        relations = self._get_undecided_mandatory_relations()
        if not relations:
            relations = self._get_undecided_optional_relations()
        random_relation = random.choice(relations)
        features = self._get_undecided_features_for_relation(random_relation)
        random_feature = random.choice(features)
        return ConfigurationState(self.fm_helper, self.elements + [random_feature])

    def is_terminal(self):
        """A configuration is terminal if all mandatory decisions have been taken."""
        #return self.elements and not self._get_undecided_mandatory_relations()
        #return self._is_valid() and any(x for x in self.elements if x.name == 'F12')
        return self.elements and (self._is_valid() or (not self._get_undecided_mandatory_relations() and not self._get_undecided_optional_relations()))
        #return self.elements and not self._get_undecided_mandatory_relations() and not self._get_undecided_optional_relations()

    def _is_valid(self):
        return self.fm_helper.is_valid_configuration(self)

    def reward(self):
        """Returns 1 if it is a valid configuration, 0 in other case."""
        # dm = DiscoverMetamodels()
        # pysatm = dm.use_transformation_m2m(src=self.feature_model, dst='pysat')
        # print(pysatm)
        # operation = dm.use_operation(src=pysatm, operation='Valid')
        # print("Result operation 'Valid configuration':", operation.is_valid())
        #return len(self.fm_helper.feature_model.get_features()) - len(self.elements)
        #return 1 if self._is_valid() else -1
        #return len(self.elements) if self._is_valid() else -len(self.elements)
        #n = len(self.fm_helper.feature_model.get_features()) - len(self.elements)
        #return n if self._is_valid() else -n
        return -1*self.performance_model.get_value(self)

    def _get_successors_for_relation(self, relation: 'Relation') -> List['ConfigurationState']:
        """List of ConfigurationState that can be reached due to the given relation."""
        successors = []
        possible_features_choices = self._get_undecided_features_for_relation(relation)
        for pfc in possible_features_choices:
            successors.append(ConfigurationState(self.fm_helper, self.elements + [pfc]))
        return successors

    def _get_undecided_features_for_relation(self, relation: 'Relation') -> List['Feature']:
        """List of undecided features of the given relation. That is, features that have not been already selected in the configuration."""
        if not relation.children:
            return []
        elif relation.is_mandatory() or relation.is_optional():
            return relation.children
        elif relation.is_alternative():
            return relation.children
        elif relation.is_or():
            return [child for child in relation.children if child not in self.elements]
        else: # n..m group cardinality
            return [child for child in relation.children if child not in self.elements]

    def _get_undecided_mandatory_relations(self) -> List['Relation']:
        """Undecided mandatory relations are those relation that needs to be decided in order to move closer to the next configuration according to the tree hierarchy."""
        res = []
        for feature in self.elements:
            for r in feature.get_relations():
                if (r.is_mandatory() and r.children[0] not in self.elements) or (r.is_alternative() and not any(child in self.elements for child in r.children)) or (r.is_or() and not any(child in self.elements for child in r.children)):
                    res.append(r)
        return res

    def _get_undecided_optional_relations(self) -> List['Relation']:
        """Undecided optional relations are those relations that may be decided (but not required by the tree hierarchy) in order to move closer to the next configuration."""
        res = []
        for feature in self.elements:
            for r in feature.get_relations():
                if (r.is_optional() and r.children[0] not in self.elements) or (r.is_or() and any(child not in self.elements for child in r.children)):
                    res.append(r)
        return res

    def __hash__(self):
        "Use of the unique Godel number."
        return self.fm_helper.fm_godelization.godelization(self)

    def __eq__(config1: 'ConfigurationState', config2: 'ConfigurationState'):
        "Compare the Godel numbers."
        return hash(config1) == hash(config2)

    def __str__(self):
        return str([str(x) for x in self.elements])
