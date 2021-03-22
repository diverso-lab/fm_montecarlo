import csv 

FILE = "jhipster3.6.1-testresults.csv"
FILE2 = "input_fms/fm-3.6.1refined-cnf.txt"

def main():
    with open(FILE) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        n = 0
        errors = 0
        for row in reader:
            n += 1
            if n == 1:
                print(row.keys())
            
            if row['Log.Build'] != 'NA':
                errors += 1
            
            
        print(f"configs: {n}")
        print(f"errors: {errors}")

def main2():
    with open(FILE2) as file:
        cnf_line = file.readline()
    
    clauses = list(map(lambda c: c[1:len(c)-1], cnf_line.split(' and ')))
    for c in clauses:
        tokens = c.split(' ')
        tokens = list(filter(lambda t: t != 'or', tokens))
        logic_not = False
        for feature in enumerate(tokens):
            if feature == 'not':
                logic_not = True
            else:

                logic_not = False
        print(tokens)


if __name__ == "__main__":
    #main()
    main2()