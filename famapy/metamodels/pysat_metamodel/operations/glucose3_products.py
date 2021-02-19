from pysat.solvers import Glucose3

from famapy.core.operations import Products
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3Products(Products):

    def __init__(self):
        self.products = []

    def get_products(self):
        return self.products

    def get_result(self):
        return self.get_products()

    def execute(self, model: PySATModel) -> 'Glucose3Products':
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint

        for solutions in g.enum_models():
            product = list()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    product.append(model.features.get(variable))
            self.products.append(product)
        return self
