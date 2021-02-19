from famapy.core.models import Configuration

class FMConfiguration(Configuration):

    def __init__(self, elements: list):
        super().__init__(elements=elements)

    def __iter__(self):
        return iter(self.elements)

    def __hash__(self):
        return hash(frozenset(self.elements))

    def __eq__(config1: 'FMConfiguration', config2: 'FMConfiguration'):
        return config1.elements == config2.elements
