from famapy.core.models import Configuration

class FMConfiguration(Configuration):

    def __init__(self, elements: dict = {}):
        super().__init__(elements=elements)

    def __iter__(self):
        return iter(self.elements)

    #def __hash__(self):
    #    return hash(tuple(self.elements.items()))

    def contains(self, feature: 'Feature') -> bool:
        return feature in self.elements and self.elements[feature]

    def __eq__(config1: 'FMConfiguration', config2: 'FMConfiguration'):
        return config1.elements == config2.elements

    def __str__(self) -> str:
        return str(['+' + str(f) if self.elements[f] else '-' + str(f) for f in self.elements])
