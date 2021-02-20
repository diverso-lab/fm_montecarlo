from abc import ABC, abstractmethod


class Configuration(ABC):

    @abstractmethod
    def __init__(self, elements: dict):  # make elements to be a dict of feature, boolean
        self.elements = elements
