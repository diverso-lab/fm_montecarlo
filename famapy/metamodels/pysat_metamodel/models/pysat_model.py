from pysat.formula import CNF

from famapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):

    @staticmethod
    def get_extension():
        return 'pysat'

    def __init__(self):
        self.cnf = CNF()
        self.variables = {}
        self.features = {}

    def add_constraint(self, constraint):
        self.cnf.append(constraint)
