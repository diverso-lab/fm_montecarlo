import random 

class MCRandom():

    @staticmethod
    def set_seed(self, seed=None):
        random.seed(seed)

    @staticmethod
    def choice(self, sequence):
        return random.choice(sequence)

    @staticmethod
    def shuffle(self, sequence):
        random.shuffle(sequence)