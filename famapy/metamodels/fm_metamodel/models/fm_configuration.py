import copy
from famapy.core.models import Configuration


class FMConfiguration(Configuration):

    def __init__(self, elements: dict):
        super().__init__(elements)
        self._selected_elements = {e for e in self.elements.keys() if self.elements[e]}

    def add_element(self, e):
        self.elements[e] = True
        self._selected_elements.add(e)

    def get_selected_elements(self) -> set:
        return self._selected_elements

    def contains(self, feature: 'Feature') -> bool:
        return feature in self._selected_elements

    def clone(self) -> 'FMConfiguration':
        return FMConfiguration(copy.copy(self.elements))

    def __eq__(config1: 'FMConfiguration', config2: 'FMConfiguration') -> bool:
        return config1._selected_elements == config2._selected_elements

    def __str__(self) -> str:
        return str([str(e) for e in self._selected_elements])
