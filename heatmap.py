import csv

COLORS = {0.0: 'BLUE',
          0.2: 'GREEN',
          0.4: 'YELLOW',
          0.6: 'ORANGE',
          0.8: 'RED'}

def read_file(filepath: 'str') -> list:
    data = {}
    with open(filepath, newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',', skipinitialspace=True)
        for row in reader:
            data[row['Feature']] = float(row['Q-value'])
    return data


def assign_color(value: float) -> str:
    if value == 0.0:
        return 'WHITE'
    else:
        for v, c in reversed(COLORS.items()):
            if value >= v:
                return c
    

if __name__ == "__main__":
    # Read Monte Carlo Q-Values
    data = read_file("MCTS-heatmap.txt")
    
    # Normalize values to range 0..1
    values = list(data.values())
    min_value = min(values)
    max_value = max(values)
    normalized_values = {}
    heatmap = {}
    for feature, v in data.items():
        normalized_values[feature] = (v-min_value)/(max_value-min_value)
        heatmap[feature] = assign_color(normalized_values[feature])

    print(normalized_values)
    print(heatmap)

    with open("MCTS-heatmap-colors.txt", 'w+') as file:
        file.write("Feature, Normalized value, Color\n")
        for f, v, c in zip(heatmap.keys(), normalized_values.values(), heatmap.values()):
            file.write(f"{f}, {v}, {c}\n")
    