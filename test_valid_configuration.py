import unittest

from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import fm_utils, AAFMsHelper
from famapy.metamodels.fm_metamodel.models import FMConfiguration




def main():
    parser = FeatureIDEParser('input_fms/TestValid.xml')
    fm = parser.transform()
    print(fm)

    aafms = AAFMsHelper(fm)
    print(f"cnf_model: {aafms.cnf_model}")
    print(f"cnf_model.features: {aafms.cnf_model.features}")

    elements = {fm.get_feature_by_name('A'): True,
              fm.get_feature_by_name('B'): True,
              fm.get_feature_by_name('C'): True}

    config = FMConfiguration(elements=elements)
    print(f"is_valid_configuration({str(config)}): {aafms.is_valid_configuration(config)}")
    print(f"is_valid_partial_configuration({str(config)}): {aafms.is_valid_partial_configuration(config)}")
    print("\n")

    elements = {fm.get_feature_by_name('A'): True,
              fm.get_feature_by_name('B'): True,
              fm.get_feature_by_name('C'): True,
              fm.get_feature_by_name('E'): True}

    config = FMConfiguration(elements=elements)
    print(f"is_valid_configuration({str(config)}): {aafms.is_valid_configuration(config)}")
    print(f"is_valid_partial_configuration({str(config)}): {aafms.is_valid_partial_configuration(config)}")
    print("\n")

    elements = {fm.get_feature_by_name('A'): True,
              fm.get_feature_by_name('B'): True,
              fm.get_feature_by_name('C'): True,
              fm.get_feature_by_name('D'): True}

    config = FMConfiguration(elements=elements)
    print(f"is_valid_configuration({str(config)}): {aafms.is_valid_configuration(config)}")
    print(f"is_valid_partial_configuration({str(config)}): {aafms.is_valid_partial_configuration(config)}")
    print("\n")

    elements = {fm.get_feature_by_name('A'): True,
              fm.get_feature_by_name('B'): True,
              fm.get_feature_by_name('C'): True,
              fm.get_feature_by_name('D'): True,
              fm.get_feature_by_name('E'): True}

    config = FMConfiguration(elements=elements)
    print(f"is_valid_configuration({str(config)}): {aafms.is_valid_configuration(config)}")
    print(f"is_valid_partial_configuration({str(config)}): {aafms.is_valid_partial_configuration(config)}")
    print("\n")



if __name__ == "__main__":
    main()
