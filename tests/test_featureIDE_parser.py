from famapy_fm.metamodels.fm_metamodel.transformations import FeatureIDEParser
import unittest


class TestFeatureIDEParser(unittest.TestCase):

    def setUp(self):
        self.parser = FeatureIDEParser
        self.ext = '.' + self.parser.get_source_extension()
        self.input_folder = '../input_fms/'
        self.models = {'linux-2.6.33.3basic': [44079, 28821, 'root', 2238],      # fm_name -> nof_features, nof_constraints, root_name, core_features
                       'automotive2_1basic':  [14098,   833, 'N_379925076__F_91527E35945B', 1412]}

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


if __name__ == "__main__":
    unittest.main(verbosity=3)
