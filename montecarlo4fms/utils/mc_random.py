import random
from typing import KeysView

# SEED = 2021
# random.seed(SEED)

# def initSeed(seed):
#     # declare
#     #global myRandom
#     myRandom = random.Random(seed)


class MCRandom():

    SEED = None 

    @staticmethod
    def set_seed(seed):
        MCRandom.SEED = seed
        return random.seed(seed)

    @staticmethod
    def choice(sequence):
        if MCRandom.SEED is not None:
            sorted(sequence)
        return random.choice(sequence)

    @staticmethod
    def shuffle(sequence):
        if MCRandom.SEED is not None:
            sorted(sequence)
        random.shuffle(sequence)

    @staticmethod
    def random():
        return random.random()
    
    @staticmethod
    def sample(sequence, k):
        if MCRandom.SEED is not None:
            sorted(sequence)
        return random.sample(sequence, k=k)
