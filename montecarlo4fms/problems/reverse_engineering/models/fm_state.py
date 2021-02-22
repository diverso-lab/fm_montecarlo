import copy
import itertools
from typing import List, Set

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint, FMConfiguration
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action


class FMState(State):

    def __init__(self, feature_model: 'FeatureModel', configurations: Set['FMConfiguration']):
        self.feature_model = feature_model
        self.configurations = configurations
        self.missing_features = self._get_missing_features()

    def _get_missing_features(self) -> set:
        """Return the set of features in the configurations that are missing in the feature model."""
        features = set()
        for c in self.configurations:
            features.update({f for f in c.elements.keys() if c.elements[f]})
        if not self.feature_model:
            return features
        return {f for f in features if f not in self.feature_model.get_features()}

    def get_actions(self) -> List['Action']:
        """Return the list of valid actions for this state."""
        if not self.feature_model:
            return [CreateFeatureModel()]

        if not self.feature_model.root:
            return [AddRootFeature(feature.name) for feature in self.missing_features]

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
                    elif requires_f1_f2 and not requires_f2_f1:
                        actions.append(AddRequiresConstraint(f2.name, f1.name))
                    elif requires_f2_f1:
                        actions.append(AddRequiresConstraint(f1.name, f2.name))
                    else:
                        actions.append(AddRequiresConstraint(f1.name, f2.name))
                        actions.append(AddRequiresConstraint(f2.name, f1.name))
                        actions.append(AddExcludesConstraint(f1.name, f2.name))

        return actions

    def is_terminal(self) -> bool:
        """A state is terminal if the feature model contains all features from all configurations.
        That is, there are not missing features."""
        return not self.missing_features

    def reward(self) -> float:
        return 0

    def __hash__(self) -> int:
        prime = 31
        return prime * hash(self.feature_model) + sum(prime * hash(a.get_name()) for a in self.get_actions())

    def __eq__(s1: 'FMState', s2: 'FMState') -> bool:
        return s1.feature_model == s2.feature_model

    def __str__(self) -> str:
        return str(self.feature_model)


class CreateFeatureModel(Action):

    def get_name(self) -> str:
        return "Create empty FM"

    def execute(self, state: 'State') -> 'State':
        return FMState(FeatureModel(None), state.configurations)


class AddRootFeature(Action):

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def get_name(self) -> str:
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

    def __init__(self, feature_name1: str, feature_name2: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2

    def get_name(self) -> str:
        return "Add requires: " + self.feature_name1 + "->" + self.feature_name2

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        feature1 = fm.get_feature_by_name(self.feature_name1)
        feature2 = fm.get_feature_by_name(self.feature_name2)
        ctc = Constraint(name=self.feature_name1 + "->" + self.feature_name2, origin=feature1, destination=feature2, ctc_type='requires')
        fm.ctcs.append(ctc)
        return FMState(fm, state.configurations)


class AddExcludesConstraint(Action):

    def __init__(self, feature_name1: str, feature_name2: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2

    def get_name(self) -> str:
        return "Add excludes: " + self.feature_name1 + "->" + self.feature_name2

    def execute(self, state: State) -> State:
        fm = copy.deepcopy(state.feature_model)
        feature1 = fm.get_feature_by_name(self.feature_name1)
        feature2 = fm.get_feature_by_name(self.feature_name2)
        ctc = Constraint(name=self.feature_name1 + "->!" + self.feature_name2, origin=feature1, destination=feature2, ctc_type='excludes')
        fm.ctcs.append(ctc)
        return FMState(fm, state.configurations)
