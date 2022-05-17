import csv
import datetime
from typing import Any 

from famapy.metamodels.fm_metamodel.models import (
    Feature,
    FeatureModel
)


class AttributesCSVReader():
    """Reader for feature attributes in .csv.

    The csv format is as follow:

    Feature, Attribute1, Attribute2, Attribute3,...
    featureAname, valueA1, valueA2, valueA3,... 
    featureBname, valueB1, valueB2, valueB3,...
    ...
    """

    # @staticmethod
    # def get_source_extension() -> str:
    #     return 'csv'

    def __init__(self, path: str, model: FeatureModel) -> None:
        self.path = path
        self.model = model

    def transform(self) -> dict[Feature, dict[str, Any]]:
        attributes = dict()
        with open(self.path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
            header = reader.fieldnames
            for row in reader:
                feature_name = row[header[0]]
                feature = self.model.get_feature_by_name(feature_name)
                if feature is not None:
                    feature_attributes = dict()
                    for attr_index in header[1:]:
                        feature_attributes[attr_index] = parse_value(row[attr_index])
                    attributes[feature] = feature_attributes
        return attributes


def parse_value(value: str) -> Any:
    try:
        return int(value)
    except:
        pass
    try:
        return float(value)
    except:
        pass
    try:
        return datetime.datetime.strptime(value, '%b %d %Y')
    except:
        pass
    return None
