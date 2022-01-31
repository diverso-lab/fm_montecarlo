import copy
import itertools
import random
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation
from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.models import State, Action, Problem


class CreateFeatureModel(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Create empty FM'

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model is None

    def __str__(self) -> str:
        return f"{self.get_name()}"
    
    def execute(self, state: 'State') -> 'State':
        return FMState(FeatureModel(None), state.configurations)


class AddRootFeature(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add root feature'

    def __init__(self, feature_name: str) -> None:
        self.feature_name = feature_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return f"{self.get_name()} '{str(self.feature_name)}'"

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        #relation = Relation(parent=None, children=[], card_min=0, card_max=0)
        root_feature = Feature(self.feature_name)
        fm.root = root_feature
        return FMState(fm, state.configurations)


class AddOptionalFeature(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add optional feature'

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add optional: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #feature = Feature(self.feature_name, [parent_relation], parent=parent)
        feature = Feature(self.feature_name, parent=parent)
        relation = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
        parent.add_relation(relation)
        return FMState(fm, state.configurations)


class AddMandatoryFeature(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add mandatory feature'

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add mandatory: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #feature = Feature(self.feature_name, [parent_relation], parent=parent)
        feature = Feature(self.feature_name, parent=parent)
        relation = Relation(parent=parent, children=[feature], card_min=1, card_max=1)
        parent.add_relation(relation)
        return FMState(fm, state.configurations)


class AddOrGroupRelation(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add or-group feature'

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add or-group: " + self.parent_name + ":(" + self.feature_name1 + "," + self.feature_name2 + ")"

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation1 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child1 = Feature(self.feature_name1, [parent_relation1], parent=parent)
        child1 = Feature(self.feature_name1, parent=parent)
        #parent_relation2 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child2 = Feature(self.feature_name2, [parent_relation2], parent=parent)
        child2 = Feature(self.feature_name2, parent=parent)
        or_relation = Relation(parent=parent, children=[child1, child2], card_min=1, card_max=2)
        parent.add_relation(or_relation)
        return FMState(fm, state.configurations)


class AddAlternativeGroupRelation(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add alternative-group feature'

    def __init__(self, feature_name1: str, feature_name2: str, parent_name: str):
        self.feature_name1 = feature_name1
        self.feature_name2 = feature_name2
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add xor-group: " + self.parent_name + ":(" + self.feature_name1 + "," + self.feature_name2 + ")"

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation1 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child1 = Feature(self.feature_name1, [parent_relation1], parent=parent)
        child1 = Feature(self.feature_name1, parent=parent)
        #parent_relation2 = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child2 = Feature(self.feature_name2, [parent_relation2], parent=parent)
        child2 = Feature(self.feature_name2, parent=parent)
        alternative_relation = Relation(parent=parent, children=[child1, child2], card_min=1, card_max=1)
        parent.add_relation(alternative_relation)
        return FMState(fm, state.configurations)


class AddFeatureToOrGroup(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add child to or-group'

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add or-group child: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child = Feature(self.feature_name, [parent_relation], parent=parent)
        child = Feature(self.feature_name, parent=parent)
        relation = next(r for r in parent.get_relations() if r.is_or())
        relation.add_child(child)
        relation.card_max += 1
        return FMState(fm, state.configurations)
        

class AddFeatureToAlternativeGroup(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Add child to alternative-group'

    def __init__(self, feature_name: str, parent_name: str):
        self.feature_name = feature_name
        self.parent_name = parent_name

    def cost(self, state1: 'FMState', state2: 'FMState') -> float:
        return 1.0

    def is_applicable(self, state: 'FMState') -> bool:
        return state.feature_model.root is None

    def __str__(self) -> str:
        return "Add xor-group child: " + self.parent_name + ":" + self.feature_name

    def execute(self, state: 'State') -> 'State':
        fm = copy.deepcopy(state.feature_model)
        parent = fm.get_feature_by_name(self.parent_name)
        #parent_relation = Relation(parent=parent, children=[], card_min=0, card_max=0)
        #child = Feature(self.feature_name, [parent_relation], parent=parent)
        child = Feature(self.feature_name, parent=parent)
        relation = next(r for r in parent.get_relations() if r.is_alternative())
        relation.add_child(child)
        return FMState(fm, state.configurations)


class FMState(State):
    """A state represents a feature model."""

    def __init__(self, feature_model: FeatureModel, configurations: set[FMConfiguration]) -> None:
        self.feature_model = feature_model
        self._hash_value = hash(self.feature_model)
        self.configurations = configurations
        self.missing_features = self._get_missing_features()
        self._actions = None

    def _get_missing_features(self) -> list[Feature]:
        """Return the set of features in the configurations that are missing in the feature model."""
        features = set()
        for c in self.configurations:
            features.update({f for f in c.get_selected_features()})
        if not self.feature_model:
            return features
        return [f for f in features if f not in self.feature_model.get_features()]

    def actions(self) -> list[Action]:
        if self._actions is not None:
            return self._actions

        if not self.feature_model:
            self._actions = [CreateFeatureModel]
            return self._actions
        
        if not self.feature_model.root:
            self._actions = [AddRootFeature]
            return self._actions

        possible_actions = []
        possible_actions.extend([AddOptionalFeature, AddMandatoryFeature])
        if len(self.missing_features) > 1:
            possible_actions.extend([AddOrGroupRelation, AddAlternativeGroupRelation])

        or_group_features = self.feature_model.get_or_group_features()
        alternative_group_features = self.feature_model.get_alternative_group_features()

        if or_group_features:
            possible_actions.append(AddFeatureToOrGroup)
        if alternative_group_features:
            possible_actions.append(AddFeatureToAlternativeGroup)

        self._actions = possible_actions
        return self._actions

    def successors(self, action: Action) -> list[State]:
        if action.get_name() == CreateFeatureModel.get_name():
            return [CreateFeatureModel().execute(self)]
        
        if action.get_name() == AddRootFeature.get_name():
            return [AddRootFeature(f.name).execute(self) for f in self.missing_features]
        
        if action.get_name() == AddOptionalFeature.get_name():
            states = []
            for parent in self.feature_model.get_features():
                states.extend([AddOptionalFeature(f.name, parent.name).execute(self) for f in self.missing_features])
            return states

        if action.get_name() == AddMandatoryFeature.get_name():
            states = []
            for parent in self.feature_model.get_features():
                states.extend([AddMandatoryFeature(f.name, parent.name).execute(self) for f in self.missing_features])
            return states

        if action.get_name() == AddOrGroupRelation.get_name():
            childs = list(itertools.combinations(self.missing_features, 2))
            states = []
            for parent in self.feature_model.get_features():
                states.extend([AddOrGroupRelation(childs[0].name, childs[1].name, parent.name).execute(self) for f in self.missing_features])
            return states

        if action.get_name() == AddAlternativeGroupRelation.get_name():
            childs = list(itertools.combinations(self.missing_features, 2))
            states = []
            for parent in self.feature_model.get_features():
                states.extend([AddAlternativeGroupRelation(childs[0].name, childs[1].name, parent.name).execute(self) for f in self.missing_features])
            return states

        if action.get_name() == AddFeatureToOrGroup.get_name():
            states = []
            for parent in self.feature_model.get_or_group_features():
                states.extend([AddFeatureToOrGroup(f.name, parent.name).execute(self) for f in self.missing_features])
            return states

        if action.get_name() == AddFeatureToAlternativeGroup.get_name():
            states = []
            for parent in self.feature_model.get_alternative_group_features():
                states.extend([AddFeatureToAlternativeGroup(f.name, parent.name).execute(self) for f in self.missing_features])
            return states
        return None

    def nof_successors(self) -> int:
        if self.is_terminal():
            return 0

        if not self.feature_model:
            return 1

        if not self.feature_model.root:
            return len(self.missing_features)

        nof_successors = 0
        if len(self.missing_features) > 1:
            nof_successors = len(list(itertools.combinations(self.missing_features, 2))) * len(self.feature_model.get_features()) * 2
            
        nof_successors += len(self.missing_features) * len(self.feature_model.get_or_group_features())
        nof_successors += len(self.missing_features) * len(self.feature_model.get_alternative_group_features())
        return nof_successors

    def random_successor(self) -> tuple[State, Action]:
        if self.is_terminal():
            raise Exception("Find random successor called in terminal state.")

        if not self.feature_model:
            action = CreateFeatureModel()
            return (action.execute(self), action)

        if not self.feature_model.root:
            action = AddRootFeature(random.choice(self.missing_features).name)
            return (action.execute(self), action)

        possible_actions = []
        possible_actions.extend([AddOptionalFeature, AddMandatoryFeature])
        if len(self.missing_features) > 1:
            possible_actions.extend([AddOrGroupRelation, AddAlternativeGroupRelation])

        or_group_features = self.feature_model.get_or_group_features()
        alternative_group_features = self.feature_model.get_alternative_group_features()
        group_features = or_group_features + alternative_group_features
        non_group_features = [f for f in self.feature_model.get_features() if f not in group_features]

        if or_group_features:
            possible_actions.append(AddFeatureToOrGroup)
        if alternative_group_features:
            possible_actions.append(AddFeatureToAlternativeGroup)

        rnd_action = random.choice(range(len(possible_actions)))
        random_action = possible_actions[rnd_action]
        if random_action.get_name() == AddOptionalFeature.get_name() or random_action.get_name() == AddMandatoryFeature.get_name():
            a = random_action(random.choice(self.missing_features).name, random.choice(non_group_features).name)
            return (a.execute(self), a)
        if random_action.get_name() == AddOrGroupRelation.get_name() or random_action.get_name() == AddAlternativeGroupRelation.get_name():
            childs = random.choice(list(itertools.combinations(self.missing_features, 2)))
            a = random_action(childs[0].name, childs[1].name, random.choice(non_group_features).name)
            return (a.execute(self), a)
        if random_action.get_name() == AddFeatureToOrGroup.get_name():
            a = random_action(random.choice(self.missing_features).name, random.choice(or_group_features).name)
            return (a.execute(self), a)
        if random_action.get_name() == AddFeatureToAlternativeGroup.get_name():
            a = random_action(random.choice(self.missing_features).name, random.choice(alternative_group_features).name)
            return (a.execute(self), a)
        return None

    def get_random_terminal_state(self) -> State:    
        state = self
        while not state.is_terminal():
            state, _ = state.random_successor()
        return state

    def is_terminal(self) -> bool:
        return not self.missing_features

    def is_valid(self) -> bool:
        return True

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FMState) and self.feature_model == other.feature_model

    def __str__(self) -> str:
        return str(self.feature_model)
    
    def heuristic(self) -> float:
        return 0.0

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
        #print(f"FM: {self.feature_model}")
        fm = FM(self.feature_model)
        #configurations_captured = aafms_helper.get_configurations()
        relaxed_value = reduce(lambda count, c: count + (fm.is_valid_configuration(c)), self.configurations, 0)
        #deficit_value = reduce(lambda count, c: count + (c not in configurations_captured), self.configurations, 0)
        #surplus_value = reduce(lambda count, c: count + (c not in self.configurations), configurations_captured, 0)

        return relaxed_value #- (deficit_value + surplus_value)


class ReverseEngineeringProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Reverse Engineering of feature models'

    def __init__(self, initial_state: 'FMState'):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> 'FMState':
        return self.initial_state