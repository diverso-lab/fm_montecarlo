import copy
import itertools
import random
from functools import reduce
from typing import List, Set

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint, FMConfiguration
from famapy.metamodels.fm_metamodel.utils import fm_utils
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.models import State, Action


class CreateFeatureModel(Action):

    @staticmethod
    def get_name() -> str:
        return "Create empty FM"

    def __str__(self) -> str:
        return "Create empty FM"

    def execute(self, state: 'State') -> 'State':
        return FMState(FeatureModel(None), state.configurations)


class AddRootFeature(Action):

    @staticmethod
    def get_name() -> str:
        return "Add root feature"

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def __str__(self) -> str:
        return "Add root " + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        relation = Relation(parent=None, children=[], card_min=0, card_max=0)
        root_feature = Feature(self.feature_name, [relation])
        fm.root = root_feature
        fm.features = [root_feature]
        fm.relations = [relation]
        fm.features_by_name[root_feature.name] = root_feature
        return FMState(fm, state.configurations)


class AddOptionalFeature(Action):

    @staticmethod
    def get_name() -> str:
        return "Add optional feature"

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add optional: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        feature = Feature(self.feature_name, [parent_relation])
        optional_relation = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
        parent.add_relation(optional_relation)
        fm.features.append(feature)
        fm.relations.extend([parent_relation, optional_relation])
        fm.features_by_name[feature.name] = feature
        return FMState(fm, state.configurations)


class AddMandatoryFeature(Action):

    @staticmethod
    def get_name() -> str:
        return "Add mandatory feature"

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add mandatory: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        feature = Feature(self.feature_name, [parent_relation])
        optional_relation = Relation(parent=parent, children=[feature], card_min=1, card_max=1)
        parent.add_relation(optional_relation)
        fm.features.append(feature)
        fm.relations.extend([parent_relation, optional_relation])
        fm.features_by_name[feature.name] = feature
        return FMState(fm, state.configurations)


class AddOrGroupRelation(Action):

    @staticmethod
    def get_name() -> str:
        return "Add or-group feature"

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add or-group: " + self.parent_name + ":(" + self.feature_name1 + "," + self.feature_name2 + ")"

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation1 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child1 = Feature(self.feature_name1, [parent_relation1])
        parent_relation2 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child2 = Feature(self.feature_name2, [parent_relation2])
        or_relation = Relation(parent=parent, children=[child1, child2], card_min=1, card_max=2)
        parent.add_relation(or_relation)
        fm.features.extend([child1, child2])
        fm.relations.extend([parent_relation1, parent_relation2, or_relation])
        fm.features_by_name[child1.name] = child1
        fm.features_by_name[child2.name] = child2
        return FMState(fm, state.configurations)


class AddAlternativeGroupRelation(Action):

    @staticmethod
    def get_name() -> str:
        return "Add alternative-group feature"

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add xor-group: " + self.parent_name + ":(" + self.feature_name1 + "," + self.feature_name2 + ")"

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation1 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child1 = Feature(self.feature_name1, [parent_relation1])
        parent_relation2 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child2 = Feature(self.feature_name2, [parent_relation2])
        alternative_relation = Relation(parent=parent, children=[child1, child2], card_min=1, card_max=1)
        parent.add_relation(alternative_relation)
        fm.features.extend([child1, child2])
        fm.relations.extend([parent_relation1, parent_relation2, alternative_relation])
        fm.features_by_name[child1.name] = child1
        fm.features_by_name[child2.name] = child2
        return FMState(fm, state.configurations)


class AddFeatureToOrGroup(Action):

    @staticmethod
    def get_name() -> str:
        return "Add child to or-group"

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add or-group child: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child = Feature(self.feature_name, [parent_relation])
        relation = next(r for r in parent.get_relations() if r.is_or())
        relation.add_child(child)
        relation.card_max += 1
        fm.features.append(child)
        fm.relations.append(parent_relation)
        fm.features_by_name[child.name] = child
        return FMState(fm, state.configurations)


class AddFeatureToAlternativeGroup(Action):

    @staticmethod
    def get_name() -> str:
        return "Add child to alternative-group"

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def __str__(self) -> str:
        return "Add xor-group child: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        child = Feature(self.feature_name, [parent_relation])
        relation = next(r for r in parent.get_relations() if r.is_alternative())
        relation.add_child(child)
        fm.features.append(child)
        fm.relations.append(parent_relation)
        fm.features_by_name[child.name] = child
        return FMState(fm, state.configurations)


class AddRequiresConstraint(Action):

    @staticmethod
    def get_name() -> str:
        return "Add requires constraint"

    def __init__(self, feature_name1: str, feature_name2: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2

    def __str__(self) -> str:
        return "Add requires: " + self.feature_name1 + "->" + self.feature_name2

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        feature1 = fm.get_feature_by_name(self.feature_name1)
        feature2 = fm.get_feature_by_name(self.feature_name2)
        ctc = Constraint(name=self.feature_name1 + "->" + self.feature_name2, origin=feature1, destination=feature2, ctc_type='requires')
        fm.ctcs.append(ctc)
        return FMState(fm, state.configurations)


class AddExcludesConstraint(Action):

    @staticmethod
    def get_name() -> str:
        return "Add excludes constraint"

    def __init__(self, feature_name1: str, feature_name2: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2

    def __str__(self) -> str:
        return "Add excludes: " + self.feature_name1 + "->" + self.feature_name2

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        feature1 = fm.get_feature_by_name(self.feature_name1)
        feature2 = fm.get_feature_by_name(self.feature_name2)
        ctc = Constraint(name=self.feature_name1 + "->!" + self.feature_name2, origin=feature1, destination=feature2, ctc_type='excludes')
        fm.ctcs.append(ctc)
        return FMState(fm, state.configurations)


class FMState(State):

    def __init__(self, feature_model: 'FeatureModel', configurations: Set['FMConfiguration']):
        self.feature_model = feature_model
        self.configurations = configurations
        self.missing_features = self._get_missing_features()
        self.actions = []
        self.actions = self.get_actions()

    def _get_missing_features(self) -> list:
        """Return the set of features in the configurations that are missing in the feature model."""
        features = set()
        for c in self.configurations:
            features.update({f for f in c.elements.keys() if c.elements[f]})
        if not self.feature_model:
            return features
        return [f for f in features if f not in self.feature_model.get_features()]

    def find_random_successor(self) -> 'State':
        """Random successor of this state (redefine it for more efficient simulation)."""
        if self.is_terminal():
            raise Exception("Find random successor called in terminal state.")

        if not self.feature_model:
            return CreateFeatureModel().execute(self)

        if not self.feature_model.root:
            return AddRootFeature(random.choice(self.missing_features).name).execute(self)

        possible_actions = []
        possible_actions.extend([AddOptionalFeature, AddMandatoryFeature])
        if len(self.missing_features) > 1:
            possible_actions.extend([AddOrGroupRelation, AddAlternativeGroupRelation])

        group_features = [f for f in self.feature_model.get_features() if fm_utils.is_group(f)]
        non_group_features = [f for f in self.feature_model.get_features() if f not in group_features]
        or_group_features = [f for f in group_features if fm_utils.is_or_group(f)]
        alternative_group_features = [f for f in group_features if fm_utils.is_alternative_group(f)]

        if or_group_features:
            possible_actions.append(AddFeatureToOrGroup)
        if alternative_group_features:
            possible_actions.append(AddFeatureToAlternativeGroup)

        candidate_features_for_constraints = list(self.feature_model.get_features())
        candidate_features_for_constraints.remove(self.feature_model.root)      # avoid constraint for root feature
        ctcs = self.feature_model.ctcs
        possible_ctcs = []
        if len(candidate_features_for_constraints) > 1:
            combinations = itertools.combinations(candidate_features_for_constraints, 2)
            for f1, f2 in combinations:
                if f1.get_parent() != f2 and f2.get_parent() != f1:         # avoid constraints between parent-child
                    requires_f1_f2 = next((c for c in ctcs if c.ctc_type == 'requires' and c.origin == f1 and c.destination == f2), None)
                    requires_f2_f1 = next((c for c in ctcs if c.ctc_type == 'requires' and c.origin == f2 and c.destination == f1), None)
                    excludes_f1_f2 = next((c for c in ctcs if c.ctc_type == 'excludes' and c.origin == f1 and c.destination == f2), None)
                    excludes_f2_f1 = next((c for c in ctcs if c.ctc_type == 'excludes' and c.origin == f2 and c.destination == f1), None)
                    if excludes_f1_f2 or excludes_f2_f1:
                        pass
                    elif not requires_f1_f2 and not requires_f2_f1:
                        possible_ctcs.append(AddRequiresConstraint(f1.name, f2.name))
                        possible_ctcs.append(AddRequiresConstraint(f2.name, f1.name))
                        possible_ctcs.append(AddExcludesConstraint(f1.name, f2.name))
                    elif not requires_f1_f2:
                        possible_ctcs.append(AddRequiresConstraint(f1.name, f2.name))
                    elif not requires_f2_f1:
                        possible_ctcs.append(AddRequiresConstraint(f2.name, f1.name))
        if possible_ctcs:
            possible_actions.extend([AddRequiresConstraint, AddExcludesConstraint])

        # Choose a random action
        random_action = random.choice(possible_actions)
        if random_action.get_name() == AddOptionalFeature.get_name() or random_action.get_name() == AddMandatoryFeature.get_name():
            return random_action(random.choice(self.missing_features).name, random.choice(non_group_features).name).execute(self)
        if random_action.get_name() == AddOrGroupRelation.get_name() or random_action.get_name() == AddAlternativeGroupRelation.get_name():
            childs = random.choice(list(itertools.combinations(self.missing_features, 2)))
            return random_action(childs[0].name, childs[1].name, random.choice(non_group_features).name).execute(self)
        if random_action.get_name() == AddFeatureToOrGroup.get_name():
            return random_action(random.choice(self.missing_features).name, random.choice(or_group_features).name).execute(self)
        if random_action.get_name() == AddFeatureToAlternativeGroup.get_name():
            return random_action(random.choice(self.missing_features).name, random.choice(alternative_group_features).name).execute(self)
        if random_action.get_name() == AddRequiresConstraint.get_name() or random_action.get_name() == AddExcludesConstraint.get_name():
            return random.choice(possible_ctcs).execute(self)


    def get_actions(self) -> List['Action']:
        """Return the list of valid actions for this state."""
        if self.actions:
            return self.actions

        if not self.feature_model:
            self.actions = [CreateFeatureModel()]
            return self.actions

        if not self.feature_model.root:
            self.actions = [AddRootFeature(feature.name) for feature in self.missing_features]
            return self.actions

        group_features = [f for f in self.feature_model.get_features() if fm_utils.is_group(f)]
        non_group_features = [f for f in self.feature_model.get_features() if f not in group_features]
        actions = []
        # Add simple feature
        for feature in self.missing_features:
            for candidate_parent in non_group_features:
                actions.append(AddOptionalFeature(feature.name, candidate_parent.name))
                actions.append(AddMandatoryFeature(feature.name, candidate_parent.name))

        # Add group relation (two features)
        if len(self.missing_features) > 1:
            combinations = itertools.combinations(self.missing_features, 2)
            for f1, f2 in combinations:
                for candidate_parent in non_group_features:
                    actions.append(AddOrGroupRelation(f1.name, f2.name, candidate_parent.name))
                    actions.append(AddAlternativeGroupRelation(f1.name, f2.name, candidate_parent.name))

        # Add feature to existing group
        for feature in self.missing_features:
            for candidate_parent in group_features:
                if fm_utils.is_or_group(candidate_parent):
                    actions.append(AddFeatureToOrGroup(feature.name, candidate_parent.name))
                elif fm_utils.is_alternative_group(candidate_parent):
                    actions.append(AddFeatureToAlternativeGroup(feature.name, candidate_parent.name))

        candidate_features_for_constraints = list(self.feature_model.get_features())
        candidate_features_for_constraints.remove(self.feature_model.root)      # avoid constraint for root feature
        ctcs = self.feature_model.ctcs
        if len(candidate_features_for_constraints) > 1:
            combinations = itertools.combinations(candidate_features_for_constraints, 2)
            for f1, f2 in combinations:
                if f1.get_parent() != f2 and f2.get_parent() != f1:         # avoid constraints between parent-child
                    requires_f1_f2 = next((c for c in ctcs if c.ctc_type == 'requires' and c.origin == f1 and c.destination == f2), None)
                    requires_f2_f1 = next((c for c in ctcs if c.ctc_type == 'requires' and c.origin == f2 and c.destination == f1), None)
                    excludes_f1_f2 = next((c for c in ctcs if c.ctc_type == 'excludes' and c.origin == f1 and c.destination == f2), None)
                    excludes_f2_f1 = next((c for c in ctcs if c.ctc_type == 'excludes' and c.origin == f2 and c.destination == f1), None)
                    if excludes_f1_f2 or excludes_f2_f1:
                        pass
                    elif not requires_f1_f2 and not requires_f2_f1:
                        actions.append(AddRequiresConstraint(f1.name, f2.name))
                        actions.append(AddRequiresConstraint(f2.name, f1.name))
                        actions.append(AddExcludesConstraint(f1.name, f2.name))
                    elif not requires_f1_f2:
                        actions.append(AddRequiresConstraint(f1.name, f2.name))
                    elif not requires_f2_f1:
                        actions.append(AddRequiresConstraint(f2.name, f1.name))
        self.actions = actions
        return self.actions

    def is_terminal(self) -> bool:
        """A state is terminal if the feature model contains all features from all configurations.
        That is, there are not missing features."""
        return not self.missing_features

    def reward(self) -> float:
        """
        Two objective function as defined in Lopez-Herrejon2015 [JSS] - An assessment of search-based techniques for reverse engineering FMs.
            1. Relaxed: Express the concern of capturing primarily the configurations provided.
                Its value is the number of configurations (self.configurations) that are valid according to the feature model represented by this state.
                We want to maximize this value.
            2. Minimal Difference (MinDiff): Express the concern of obtaining a closer-fit to the configurations provided (other configurations are not relevant).
                Its value is 'deficit' + 'surplus' where:
                    'deficit' is the number of configurations (self.configurations) that are not contained in the configuration of the feature model.
                    'surplus' is the number of configurations of the feature model that are not contained in the required configuration (self.configurations).
                We want to minimize this value.
        """
        aafms_helper = AAFMsHelper(self.feature_model)
        configurations_captured = aafms_helper.get_configurations()
        relaxed_value = reduce(lambda count, c: count + (aafms_helper.is_valid_configuration(c)), self.configurations, 0)
        deficit_value = reduce(lambda count, c: count + (c not in configurations_captured), self.configurations, 0)
        surplus_value = reduce(lambda count, c: count + (c not in self.configurations), configurations_captured, 0)

        return relaxed_value - (deficit_value + surplus_value)

    def __hash__(self) -> int:
        prime = 31
        return prime * hash(self.feature_model) + sum(prime * hash(a.get_name()) for a in self.get_actions())

    def __eq__(s1: 'FMState', s2: 'FMState') -> bool:
        return hash(s1) == hash(s2)

    def __str__(self) -> str:
        return str(self.feature_model)
