from functools import total_ordering
from ast import AST
from typing import Sequence

from famapy.core.models import VariabilityModel
from famapy.core.exceptions import ElementNotFound

class Relation:

    def __init__(self, parent: 'Feature', children: Sequence['Feature'], card_min: int, card_max: int):
        self.parent = parent
        self.children = children
        self.card_min = card_min
        self.card_max = card_max

    def add_child(self, feature: 'Feature'):
        self.children.append(feature)

    def is_mandatory(self) -> bool:
        return self.card_min == 1 and self.card_max == 1 and len(self.children) == 1

    def is_optional(self) -> bool:
        return self.card_min == 0 and self.card_max == 1 and len(self.children) == 1

    def is_or(self) -> bool:
        return self.card_min == 1 and self.card_max == len(self.children) and len(self.children) > 1

    def is_alternative(self) -> bool:
        return self.card_min == 1 and self.card_max == 1 and len(self.children) > 1

    def __str__(self):
        res = (self.parent.name if self.parent else '') + '[' + str(self.card_min) + ',' + str(self.card_max) + ']'
        for _child in self.children:
            res += _child.name + ' '
        return res

    def __hash__(self) -> int:
        return hash((self.parent, tuple(self.children), self.card_min, self.card_max))

    def __eq__(self, other: 'Relation') -> bool:
        return self.parent == other.parent and self.children == other.children and self.card_min == other.card_min and self.card_max == other.card_max

@total_ordering
class Feature:

    def __init__(self, name: str, relations: Sequence['Relation'] = [], parent: 'Feature' = None, is_abstract: bool = False):
        self.name = name
        self.relations = relations
        self.parent = parent
        self.is_abstract = is_abstract

    def add_relation(self, relation: 'Relation'):
        self.relations.append(relation)

    def get_relations(self):
        return self.relations

    def get_parent(self):
        return self.parent

    def __str__(self):
        return self.name # if not self.is_abstract else self.name + " (abstract)"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: 'Feature') -> bool:
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

class Constraint:
    #This is heavily limited. Currently this will only support requires and excludes
    def __init__(self, name: str, origin:'Feature', destination:'Feature', ctc_type:str):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.ctc_type = ctc_type

    def __hash__(self) -> int:
        return hash((self.origin, self.destination, self.ctc_type))

    def __eq__(self, other: 'Constraint') -> bool:
        return self.origin == other.origin and self.destination == other.destination and self.ctc_type == other.ctc_type

class FeatureModel(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'fm'

    def __init__(self, root: Feature, constraint: Sequence[Constraint]=[], features: Sequence[Feature]=[], relations: Sequence[Relation]=[]):
        self.root = root
        self.ctcs = constraint  # implementar CTC con AST
        self.features = features
        self.relations = relations
        if not features:
            self.features = self.get_features()
        if not relations:
            self.relations = self.get_relations()
        self.features_by_name = {f.name : f for f in self.features}

    def get_relations(self, feature=None):
        if not self.root:   # Empty feature model
            return []

        if not self.relations:
            relations = []
            if not feature:
                feature = self.root
            for relation in feature.relations:
                relations.append(relation)
                for _feature in relation.children:
                    relations.extend(self.get_relations(_feature))
            self.relations
        return self.relations

    def get_features(self):
        if not self.root:   # Empty feature model
            return []

        if not self.features:
            features = []
            features.append(self.root)
            for relation in self.get_relations():
                features.extend(relation.children)
            self.features = features
        return self.features

    #This method is for consistency with the getters
    def get_constraints(self):
        return self.ctcs

    def get_feature_by_name(self, feature_name: str) -> Feature:
        if not feature_name in self.features_by_name:
            raise Exception(f"Not feature with name: {feature_name}")
        return self.features_by_name[feature_name]

    def __hash__(self) -> int:
        return hash((self.root, tuple(self.features), tuple(self.relations), tuple(self.ctcs)))

    def __eq__(self, other: 'FeatureModel') -> bool:
        return (self.root == other.root
               and self.features == other.features
               and self.relations == other.relations
               and self.ctcs == other.ctcs)

    def __str__(self) -> str:
        if not self.root:
            return '(empty feature model)'
        res = 'root: ' + self.root.name + '\r\n'
        for i, relation in enumerate(self.get_relations()):
            res += f'relation {i}: {relation}\r\n'
        for i, ctc in enumerate(self.ctcs):
            res += ctc.origin.name +" "+ctc.ctc_type + " " + ctc.destination.name
        return(res)

    # def __hash__(self) -> int:
    #     return hash((self.features, self.ctcs, self.relations))

    def __eq__(self, other: 'FeatureModel'):
        return self.root == other.root and self.features == other.features and self.relations == other.relations and self.ctcs == other.ctcs
