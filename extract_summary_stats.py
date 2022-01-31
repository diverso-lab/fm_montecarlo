import argparse
import csv
import os
import statistics
from typing import Any


RESULTS_FILEPATH = 'summary_stats.csv'

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


def get_summary_stastistics(data: list[Any], digits: int = 4) -> dict[str, Any]:
    results = {}
    results[MEDIAN] = round(statistics.median(data), digits)
    results[MODE] = round(statistics.mode(data), digits)
    results[MEAN] = round(statistics.mean(data), digits)
    results[STDEV] = round(statistics.stdev(data), digits)
    results[VARIANCE] = round(statistics.variance(data), digits)
    results[MIN] = round(min(data), digits)
    results[MAX] = round(max(data), digits)
    return results


def get_summary_stats(filepath: str):
    headers, data = get_data(filepath)
    summary_stats = {}
    for h in headers:
        values = [to_number(data[r][h]) for r in data.keys()]
        if values:
            if all(v is not None for v in values):
                summary_stats[h] = get_summary_stastistics(values)
            else:
                summary_stats[h] = data[0][h]
        else:
            summary_stats[h] = data[0][h]
    return summary_stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract summary statistics (median, mean, stddev,...) from the result files available in the given folder.')
    parser.add_argument('-d', '--directory', dest='directory', type=str, required=True, help='Directory with the result files.')
    args = parser.parse_args()

    result_filepath = os.path.join(args.directory, RESULTS_FILEPATH)
    if os.path.exists(result_filepath):
        os.remove(result_filepath)

    summary = []
    for subdir, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith('.csv'):
                filepath = os.path.join(subdir, file)
                summary.append(get_summary_stats(filepath))
    
    # Prepare headers
    d = summary[0]
    header_line = []
    for header in d.keys():
        if isinstance(d[header], dict):
            for h in d[header].keys():
                header_line.append(header + ' ' + h) 
        else:
            header_line.append(header)

    # Prepare values
    data = []
    for d in summary:
        line = []
        for header in d.keys():
            if isinstance(d[header], dict):
               for h in d[header].keys():
                   line.append(d[header][h]) 
            else:
                line.append(d[header])
        data.append(line)
    
    # Write csv
    with open(result_filepath, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(header_line)
        for d in data:
            writer.writerow(d)
