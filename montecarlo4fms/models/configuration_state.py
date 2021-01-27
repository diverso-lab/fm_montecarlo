import random
from .state import State
from .fm_godelization import FMGodelization
from famapy.core.models import Configuration
from famapy.core.discover import DiscoverMetamodels
import itertools


class ConfigurationState(Configuration, State):
    """
    It represents a configuration of a feature model as a state.
    Its successors are any possible selection of features where at least all mandatory decisions are covered, and maybe optional decisions are taken.
    A configuration is terminal if it has not possible successors.
    """

    def __init__(self, feature_model: 'FeatureModel', config_elements: list['Feature']):
        super().__init__(config_elements)
        self.feature_model = feature_model
        self._fm_godelization = FMGodelization(feature_model)

    def find_successors(self) -> list['ConfigurationState']:
        """
        All possible successors of this configuration state.
        The successors of a configuration are:
        - (1) the configurations with the inmediate mandatory (undecided) features selected according to the tree structure following a top-down approach.
        - (2) in case there is not any inmediate mandatory features undecided, the configurations with the inmediate optional (undecided) feature according to the tree structure following a top-down approach.
        A successor of a configuration differs only in a feature selection.
        """
        if not self.elements:
            return [ConfigurationState(self.feature_model, [self.feature_model.root])]

        successors = []
        features_selections = []
        undecided_mandatory_relations = self._get_undecided_mandatory_relations()
        if undecided_mandatory_relations:
            for relation in undecided_mandatory_relations:
                new_successors = self._get_successors_for_relation(relation)
                # Successors of mandatory features needs to be mixed.
                if not successors:
                    successors = new_successors
                else:
                    for s in successors:
                        for ns in new_successors:
                            s.elements = list(dict.fromkeys(s.elements + ns.elements))

        else: # optionals
            undecided_optional_relations = self._get_undecided_optional_relations()
            for relation in undecided_optional_relations:
                new_successors = self._get_successors_for_relation(relation)
                successors.extend(new_successors)

        return successors

    def find_random_successor(self):
        """Random configuration successor of the configuration."""
        if not self.elements:
            return ConfigurationState(self.feature_model, [self.feature_model.root])

        relations = self._get_undecided_mandatory_relations()
        if not relations:
            relations = self._get_undecided_optional_relations()
        random_relation = random.choice(relations)
        features = self._get_undecided_features_for_relation(random_relation)
        random_feature = random.choice(features)
        return ConfigurationState(self.feature_model, self.elements + [random_feature])

    def is_terminal(self):
        """A configuration is terminal if all mandatory decisions have been taken."""
        return self.elements and not self._get_undecided_mandatory_relations()

    def reward(self):
        """Returns 1 if it is a valid configuration, 0 in other case.
        TODO: use a SAT solver to check cross-tree constraints"""
        # dm = DiscoverMetamodels()
        # pysatm = dm.use_transformation_m2m(src=self.feature_model, dst='pysat')
        # print(pysatm)
        # operation = dm.use_operation(src=pysatm, operation='Valid')
        # print("Result operation 'Valid configuration':", operation.is_valid())

        return 1 if self.elements and not self._get_undecided_mandatory_relations() else 0

    def _get_successors_for_relation(self, relation: 'Relation') -> list['ConfigurationState']:
        """List of ConfigurationState that can be reached due to the given relation."""
        successors = []
        possible_features_choices = self._get_undecided_features_for_relation(relation)
        for pfc in possible_features_choices:
            successors.append(ConfigurationState(self.feature_model, self.elements + [pfc]))
        return successors

    def _get_undecided_features_for_relation(self, relation: 'Relation') -> list['Feature']:
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

    def _get_undecided_mandatory_relations(self) -> list['Relation']:
        """Undecided mandatory relations are those relation that needs to be decided in order to move closer to the next configuration according to the tree hierarchy."""
        res = []
        for feature in self.elements:
            for r in feature.get_relations():
                if (r.is_mandatory() and r.children[0] not in self.elements) or (r.is_alternative() and not any(child in self.elements for child in r.children)) or (r.is_or() and not any(child in self.elements for child in r.children)):
                    res.append(r)
        return res

    def _get_undecided_optional_relations(self) -> list['Relation']:
        """Undecided optional relations are those relations that may be decided (but not required by the tree hierarchy) in order to move closer to the next configuration."""
        res = []
        for feature in self.elements:
            for r in feature.get_relations():
                if (r.is_optional() and r.children[0] not in self.elements) or (r.is_or() and any(child not in self.elements for child in r.children)):
                    res.append(r)
        return res

    def __hash__(self):
        "Use of the unique Godel number."
        return self._fm_godelization.godelization(self)

    def __eq__(config1: 'ConfigurationState', config2: 'ConfigurationState'):
        "Compare the Godel numbers."
        return hash(config1) == hash(config2)

    def __str__(self):
        return str([str(x) for x in self.elements])
