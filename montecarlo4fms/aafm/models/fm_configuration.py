import copy
from famapy.core.models import Configuration


class FMConfiguration(Configuration):

    def __init__(self, elements: dict = {}):
        super().__init__(elements)

    def add_element(self, e):
        self.elements[e] = True

    def get_selected_elements(self) -> set:
        #return {e for e in self.elements.keys() if self.elements[e]}
        return set(self.elements.keys())

    def contains(self, feature: 'Feature') -> bool:
        return feature in self.elements and self.elements[feature]

    def clone(self) -> 'FMConfiguration':
        return FMConfiguration(copy.copy(self.elements))

    def __eq__(self, other: 'FMConfiguration') -> bool:
        return self.elements == other.elements

    def __str__(self) -> str:
        return str([str(e) for e in self.elements.keys() if self.elements[e]])

    def __hash__(self) -> int:
        return hash(frozenset(self.elements.items()))
