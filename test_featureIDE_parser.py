import unittest

from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import fm_utils, AAFMsHelper


class TestFeatureIDEParser(unittest.TestCase):

    def setUp(self):
        self.parser = FeatureIDEParser
        self.ext = '.' + self.parser.get_source_extension()
        self.input_folder = 'input_fms/'
        self.models = {'wget':                [17, 0, 'wget', 2, 0, 1],           # fm_name -> nof_features, nof_constraints, root_name, core_features, or-groups, alternative-groups
                       'tankwar':             [37, 0, 'TankWar', 7, 2, 6],
                       'mobile_media2':       [43, 3, 'MobileMedia2', 10, 4, 3],
                       'WeaFQAs':             [179, 7, 'FQAs', 1, 12, 23],
                       'busybox-1.18.0':      [854, 58, 'root', 20, 0, 8], # 67 constraints by FeatureIDE
                       # 'ea2468':              [1408, 1281, 'root', 4, 0, 0],
                       # 'automotive2_1':       [14010, 624, 'N_379925076__F_91527E35945B', 1394, 0, 0],
                       # 'linux-2.6.33.3':      [6467, 7650, 'root', 53, 0, 0],
                       # 'uClinux-distribution':[1580, 247, 'root', 6, 0, 0],
                       # 'embtoolkit':          [1179, 167, 'root', 78, 0, 0],
                        'linux-2.6.33.3basic': [44079, 28821, 'root', 2238, 9434, 39],
                        'automotive2_1basic':  [14098,   833, 'N_379925076__F_91527E35945B', 1412, 125, 1010],
                        'pizzas':              [12, 1, 'Pizza', 4, 1, 2]}

    def test_nof_features(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            with self.subTest(fm=fm_input):
                self.assertEqual(len(fm.get_features()), self.models[fm_input][0])

    def test_nof_constraints(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            with self.subTest(fm=fm_input):
                self.assertEqual(len(fm.get_constraints()), self.models[fm_input][1])

    def test_root(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            with self.subTest(fm=fm_input):
                self.assertEqual(fm.root.name, self.models[fm_input][2])
                self.assertIsNone(fm.root.get_parent())

    def test_or_groups(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            with self.subTest(fm=fm_input):
                or_groups = [f for f in fm.get_features() if fm_utils.is_or_group(f)]
                self.assertEqual(len(or_groups), self.models[fm_input][4])

    def test_alternative_groups(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            with self.subTest(fm=fm_input):
                alternative_groups = [f for f in fm.get_features() if fm_utils.is_alternative_group(f)]
                self.assertEqual(len(alternative_groups), self.models[fm_input][5])

    def test_core_features(self):
        for fm_input in self.models:
            parser = self.parser(self.input_folder + fm_input + self.ext)
            fm = parser.transform()
            aafms = AAFMsHelper(fm)
            with self.subTest(fm=fm_input):
                core_features = aafms.get_core_features()
                self.assertEqual(len(core_features), self.models[fm_input][3])


if __name__ == "__main__":
    unittest.main(verbosity=3)

    # parser = FeatureIDEParser('input_fms/wget.xml')
    # fm = parser.transform()
    # for f in fm.get_features():
    #     print(f"{str(f)} : {str(f.get_parent())}")
