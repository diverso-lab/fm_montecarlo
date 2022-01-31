import os
import logging
from typing import Callable


RESULTS = 'results/'
os.makedirs(RESULTS, exist_ok=True)


def get_logger(name: str, mode: str = 'w') -> Callable:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(RESULTS + name + '.csv', mode=mode, encoding='utf8')
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger.info