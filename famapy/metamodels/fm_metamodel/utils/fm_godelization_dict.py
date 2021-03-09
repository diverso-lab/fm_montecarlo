"""
PERFORMANCE DATA (Laptop i5-6200U, 2.40 GHz, 8 GB, Windows 10, Python 3.7.4):
For a feature model of 50k features:
- it takes around 24 ms to build the dictionary of codes.
- it takes around 6 ms to build the inverse dictionary of codes.
For a configuration of 50k features:
- it takes around 23 ms to apply the godel function.
- it takes around 17 ms to inverse the godel function.

PERFORMANCE DATA (Desktop i9-9900K, 3.60 GHz, 32 GB, Windows 10, Python 3.9.1):
For a feature model of 50k features:
- it takes around 12 ms to build the dictionary of codes.
- it takes around 5 ms to build the inverse dictionary of codes.
For a configuration of 50k features:
- it takes around 7 ms to apply the godel function.
- it takes around 2 ms to inverse the godel function.
"""
from typing import List, Dict

from famapy.metamodels.fm_metamodel.models import FMConfiguration

class FMGodelization:
    """
    Use of a Godel function to assign a unique identifier number to each feature and configuration.
    This works like a 'hash' function but it is possible to reverse.
    However, this should be used for storing configurations that belong to the same feature model
    Do not use as 'hash' or for comparing configurations that belong to different feature models.

    The Godel function works as follows:
    First, create the feature model codes:
        - given a feature model with N features (eg, [A, B, C, D]), we enumerate those features A=0, B=1, C=2, D=3, and so on.
        - the codes are stored in two dictionaries for efficiency: (Feature -> int) and its inverse (int -> Feature).
        - Note: the order of the features is not important, but it may affect efficiency. Thus, the most efficient order is transversing the feature diagram in breadth-first search.

    Second, calculate the number for a configuracion:
        - given a configuration of the feature model, we create a vector of size N initialized to zeros, and assign 1 to the positions of features present in the configuration, according to the previous order (but inverted).
        - Example: configuration [A, C] is codified to '0101' which is the binary representation of the configuration.
        - the Godel number is the decimal value of the binary representation.
    """

    def __init__(self, feature_model: 'FeatureModel'):
        self._fm_codes = self._get_feature_model_codes(feature_model)
        self._fm_codes_i = {value: key for (key, value) in self._fm_codes.items()}    # inverse of _fm_codes

    def godelization(self, config: 'Configuration') -> int:
        """Get the unique identifier number (decimal) of the configuration associated to the feature model."""
        n_features = len(self._fm_codes)
        #res = [0] * n_features
        n = n_features - 1  # for efficiency
        #for f in config.elements:
        #    res[n - self._fm_codes[f]] = int(config.elements[f])   # Create the binary number in reversed order. First feature at the left.
        res = {n-self._fm_codes[f] : str(int(config.elements[f])) for f in config.elements.keys()}
        return int(''.join(res.values()), 2)

    def degodelization(self, config_number: int) -> 'FMConfiguration':
        """Get the configuration from its godel number (decimal)."""
        res = {f: False for f in self._fm_codes.keys()}
        bin_config = bin(config_number)[::-1]   # Reverse order. First feature at the left.
        for i in range(len(bin_config)):
            if bin_config[i] == '1':
                res[self._fm_codes_i[i]] = True
        return FMConfiguration(res)

    def _get_feature_model_codes(self, feature_model: 'FeatureModel') -> Dict['Feature', int]:
        """Dictionary of {Feature : int}, assigning a unique number to each feature."""
        features = feature_model.get_features()
        return {f : i for f, i in zip(features, range(len(features)))}
