import csv

with open("rs.csv", 'r') as f:
    lines = csv.reader(f)
    next(lines)
    result = {}
    for i, line in enumerate(lines):
        sample_size = int(line[1].strip())
        kos = int(line[2].strip())
        result[i] = line
        result[i].append(str(float(kos)/float(sample_size)))
        print(line)

    with open("rs2.csv", "w+") as f2:
        for r in result:
            line = ", ".join(result[r])
            f2.write(f"{line}\n")