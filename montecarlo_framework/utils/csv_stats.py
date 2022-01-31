import argparse 
import csv
import statistics
from typing import Any 


MEDIAN = 'Median'
MODE = 'Mode'
MEAN = 'Mean'
STDEV = 'StDev'
VARIANCE = 'Variance'
MAX = 'Max'
MIN = 'Min'


def to_number(s: str) -> Any:
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return None


def get_data(filepath: str) -> tuple[list[str], dict[int, dict[str, str]]]:
    data = {}
    headers = []
    with open(filepath, mode='r', encoding='utf8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', skipinitialspace=True)
        headers = csv_reader.fieldnames
        for i, row in enumerate(csv_reader):
            data[i] = row
    return (headers, data)


def get_summary_stastistics(data: list[Any], digits: int) -> dict[str, Any]:
    results = {}
    results[MEDIAN] = round(statistics.median(data), digits)
    results[MODE] = round(statistics.mode(data), digits)
    results[MEAN] = round(statistics.mean(data), digits)
    results[STDEV] = round(statistics.stdev(data), digits)
    results[VARIANCE] = round(statistics.variance(data), digits)
    results[MIN] = round(min(data), digits)
    results[MAX] = round(max(data), digits)
    return results


def summary_stastistics(filepath: str):
    data = get_data(filepath)
    print(data)
    return data
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Getting summary statistics from experimentation data in CSV files.')
    parser.add_argument('-f', '--file', dest='file', type=str, required=True, help='Input csv file.')
    parser.add_argument('-p', '--precision', dest='precision', type=int, default=4, required=False, help='Number of digits for float number.')
    args = parser.parse_args()

    headers, data = get_data(args.file)
    summary_stats = {}
    for h in headers:
        values = [to_number(data[r][h]) for r in data.keys()]
        if all(v is not None for v in values):
            summary_stats[h] = get_summary_stastistics(values, args.precision)
    
    for h in summary_stats.keys():
        print(f'{h}: {summary_stats[h]}')
    
    