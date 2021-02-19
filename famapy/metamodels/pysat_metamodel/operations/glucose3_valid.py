from pysat.solvers import Glucose3

from famapy.core.operations import Valid
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3Valid(Valid):

    def __init__(self):
        self.result = False

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def execute(self, model: PySATModel) -> 'Glucose3Valid':
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint
        self.result = g.solve()
        return self
