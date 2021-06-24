import copy
from collections import OrderedDict
from functools import total_ordering
from famapy.core.models import Configuration

@total_ordering
class FMConfiguration(Configuration):

    def __init__(self, elements: dict = {}):
        #elements = dict(sorted(elements.items()))
        super().__init__(elements)
        #self.elements = OrderedDict(sorted(elements.items()))

    def add_element(self, e):
        self.elements[e] = True

    def get_selected_elements(self) -> list:
        #return {e for e in self.elements.keys() if self.elements[e]}
        return sorted(self.elements.keys())

    def contains(self, feature: 'Feature') -> bool:
        return feature in self.elements and self.elements[feature]

    def clone(self) -> 'FMConfiguration':
        return FMConfiguration(copy.copy(self.elements))

    def __eq__(self, other: 'FMConfiguration') -> bool:
        return self.elements == other.elements

    def __str__(self) -> str:
        return str([str(e) for e in sorted(self.elements.keys()) if self.elements[e]])

    def __hash__(self) -> int:
        return hash(frozenset(sorted(self.elements.items())))

    def __lt__(self, other):
        return sorted(self.elements.keys()) < sorted(other.elements.keys())
