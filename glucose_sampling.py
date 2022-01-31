from famapy.metamodels.fm_metamodel.models import FeatureModel
from famapy.metamodels.fm_metamodel.operations import FMEstimatedProductsNumber, average_branching_factor
from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from famapy.metamodels.bdd_metamodel.operations import BDDProductsNumber
from famapy.metamodels.bdd_metamodel.transformations.fm_to_bdd import FmToBDD
from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

from models.models_info import *

from pysat.solvers import Glucose3


def int_to_scientific_notation(n: int, precision: int = 2) -> str:
    """Convert a large int into scientific notation.
    
    It is required for large numbers that Python cannot convert to float,
    solving the error `OverflowError: int too large to convert to float`.
    """
    str_n = str(n)
    decimal = str_n[1:precision+1]
    exponent = str(len(str_n) - 1)
    return str_n[0] + '.' + decimal + 'e' + exponent

def get_model(model_name) -> FeatureModel:
    return FeatureIDEReader('models/' + model_name + FIDE_EXTENSION).transform()


if __name__ == '__main__':
    fm = get_model('pizzas')
    sat_model = FmToPysat(fm).transform()
    solver = Glucose3()

    for clause in sat_model.get_all_clauses():  # AC es conjunto de conjuntos
        solver.add_clause(clause)  # añadimos la constraint

    products = []
    for solutions in solver.enum_models():
        product = []
        for variable in solutions:
            if variable > 0:
                product.append(sat_model.features.get(variable))
        products.append(product)
    solver.delete()

    help(solver)
    print(solver.get_model())
    print(solver.get_model())