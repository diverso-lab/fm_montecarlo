from multiprocessing.queues import Queue
import time 
import multiprocessing

from famapy.metamodels.fm_metamodel.models import FeatureModel
from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader


def do_something(fm: FeatureModel, result_queue: Queue):
    print(f'Counting features...')
    n = len(fm.get_features())
    result_queue.put(fm.root)
    return n


def main(input_model: str):
    start = time.perf_counter_ns()

    feature_model = FeatureIDEReader(input_model).transform()

    result_queue = multiprocessing.Queue()
    processes = []    
    for _ in range(10):
        p = multiprocessing.Process(target=do_something, args=[feature_model, result_queue])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
    
    results = [result_queue.get() for process in processes]

    print(results)
    


    finish = time.perf_counter_ns()
    print(f'Finished in {round((finish-start)*1e-9, 2)} seconds.')    



if __name__ == '__main__':
    main('models/pizzas.xml')