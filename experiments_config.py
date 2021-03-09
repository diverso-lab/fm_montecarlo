INPUT_PATH = "input_fms/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"


def initialize_results_file():
    with open(OUTPUT_RESULTS_FILE, 'w+') as file:
        file.write("Run, Algorithm, Iterations, Time, Features in Config, Valid Config, Reward, Nodes, Configuration\n")


if __name__ == '__main__':
    initialize_results_file()
