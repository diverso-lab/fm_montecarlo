import csv
from typing import List
from fm_metamodel.famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration
from famapy.core.models import Configuration

class PerformanceModel:

    def __init__(self, feature_model: FeatureModel):
        self.feature_model = feature_model
        self.values = dict()

    def load_configurations_from_csv(self, csv_filepath: str, features_header_names: List[str], value_header_name: str):
        with open(csv_filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                config = FMConfiguration([self.feature_model.get_feature_by_name(row[x]) for x in features_header_names])
                value = float(row[value_header_name])
                self.values[config] = value

    def get_model(self) -> dict:
        return self.values

    def get_value(self, config: Configuration) -> float:
        product = next((p for p in self.values.keys() if all(f in config.elements for f in p.elements)), None)
        if product:
            return self.values[product]
        else:
            return 0
