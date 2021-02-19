from pysat.solvers import Glucose3

from famapy.core.operations import ValidConfiguration
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ValidConfiguration(ValidConfiguration):

    def __init__(self) -> None:
        self.configuration = None
        self.result = None

    def set_configuration(self, configuration: Configuration):
        self.configuration = configuration

    def is_valid(self) -> bool:
        return self.result

    def get_result(self):
        return self.is_valid()

    def execute(self, model: PySATModel) -> 'Glucose3ValidConfiguration':
        g = Glucose3()
        for clause in model.cnf:
            g.add_clause(clause)
        config_names = [feature.name for feature in self.configuration.elements]
        formula = [[clause[0]] if clause[1] in config_names else [-clause[0]] for clause in model.features.items()]
        g.append_formula(formula)
        self.result = g.solve()

        return self
