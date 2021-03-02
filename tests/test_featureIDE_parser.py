import unittest

from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser

from famapy.metamodels.fm_metamodel.utils import fm_utils


class TestFeatureIDEParser(unittest.TestCase):

    def setUp(self):
        self.parser = FeatureIDEParser
        self.ext = '.' + self.parser.get_source_extension()
        self.input_folder = '../input_fms/'
        self.models = {'wget':                [17, 0, 'wget', 2, 0, 1]          # fm_name -> nof_features, nof_constraints, root_name, core_features, or-groups, alternative-groups

                      }
                       # 'linux-2.6.33.3basic': [44079, 28821, 'root', 2238],
                       # 'automotive2_1basic':  [14098,   833, 'N_379925076__F_91527E35945B', 1412],
                       # 'pizzas':              [12, 1, 'Pizza', 4]}

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


if __name__ == "__main__":
    unittest.main(verbosity=3)
