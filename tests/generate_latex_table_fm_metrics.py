from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.fm_metamodel.operations import FMEstimatedProductsNumber, average_branching_factor, max_depth_tree
from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from flamapy.metamodels.bdd_metamodel.operations import BDDProductsNumber
from flamapy.metamodels.bdd_metamodel.transformations.fm_to_bdd import FmToBDD

from models.models_info import *


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
    for model in MODELS:
        fm = get_model(model[NAME])
        print(f'{model[NAME]}~\cite{{}}')
        print(f'& {len(fm.get_features())}')
        print(f'& {len(fm.get_optional_features())}')
        print(f'& {len(fm.get_mandatory_features())}')
        print(f'& {len(fm.get_or_group_features())}')
        print(f'& {len(fm.get_alternative_group_features())}')
        print(f'& {average_branching_factor(fm)}')
        print(f'& {max_depth_tree(fm)}')
        print(f'& {len(fm.get_constraints())}')
        
        try:
            bdd_model = FmToBDD(fm).transform()
            nof_products = BDDProductsNumber().execute(bdd_model).get_result()
        except:
            print('aprox:')
            nof_products = FMEstimatedProductsNumber().execute(fm).get_result()
        
        nof_products = int_to_scientific_notation(nof_products) if nof_products > 1e6 else nof_products
        print(f'& {nof_products}')
        print(f'\\\\')
        print()
