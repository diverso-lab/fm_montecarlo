import time 
import multiprocessing
import concurrent.futures


def do_something(seconds: int):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    return f'Done sleeping...{seconds}'


def manual_multiprocessing():
    start = time.perf_counter_ns()

    processes = []    
    for _ in range(10):
        p = multiprocessing.Process(target=do_something, args=[1.5])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
        


    finish = time.perf_counter_ns()
    print(f'Finished in {round((finish-start)*1e-9, 2)} seconds.')    


def concurrent_futures():  # This takes longer than manual multiprocessing.
    start = time.perf_counter_ns()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [5, 4, 3, 2, 1]
        results = [executor.submit(do_something, sec) for sec in secs]
        for f in concurrent.futures.as_completed(results):
            print(f.result())

    finish = time.perf_counter_ns()
    print(f'Finished in {round((finish-start)*1e-9, 2)} seconds.') 


def map_concurrent_futures():
    start = time.perf_counter_ns()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [5, 4, 3, 2, 1]
        results = executor.map(do_something, secs)

        for result in results:  # print out in the order they started (not finished)
            print(result)

    finish = time.perf_counter_ns()
    print(f'Finished in {round((finish-start)*1e-9, 2)} seconds.') 


if __name__ == '__main__':
    map_concurrent_futures()