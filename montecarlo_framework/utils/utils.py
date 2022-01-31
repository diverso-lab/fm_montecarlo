import statistics
from typing import Any 


MEDIAN = 'Median'
MODE = 'Mode'
MEAN = 'Mean'
STDEV = 'StDev'
VARIANCE = 'Variance'
MAX = 'Max'
MIN = 'Min'


def get_summary_stastistics(data: list[Any], digits: int) -> dict[str, Any]:
    assert len(data) >= 1
    results = {}

    if len(data) == 1:
        value = round(data[0], digits)
        results[MEDIAN] = value
        results[MODE] = value
        results[MEAN] = value
        results[STDEV] = 0.0
        results[VARIANCE] = 0.0
        results[MIN] = value
        results[MAX] = value
    else:
        results[MEDIAN] = round(statistics.median(data), digits)
        results[MODE] = round(statistics.mode(data), digits)
        results[MEAN] = round(statistics.mean(data), digits)
        results[STDEV] = round(statistics.stdev(data), digits)
        results[VARIANCE] = round(statistics.variance(data), digits)
        results[MIN] = round(min(data), digits)
        results[MAX] = round(max(data), digits)
    return results
