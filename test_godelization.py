import cProfile

from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import FMGodelization
from famapy.metamodels.fm_metamodel.models import FMConfiguration

def main():
    parser = FeatureIDEParser('input_fms/linux-2.6.33.3basic.xml')
    fm = parser.transform()

    print(f"#Features: {len(fm.get_features())}")
    fm_godel = FMGodelization(fm)

    elements = {f: True for f in fm.get_features()}
    config = FMConfiguration(elements)

    n = fm_godel.godelization(config)
    print(f"Number: {n}")

    config2 = fm_godel.degodelization(n)
    print(f"Equals: {config == config2}")



if __name__ == '__main__':
    cProfile.run('main()')
