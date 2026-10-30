import sys
import math
import time
from multiprocessing.pool import ThreadPool

try:
    from Pyro4 import expose
except ImportError:
    def expose(fn):
        return fn

try:
    xrange_fn = xrange
except NameError:
    xrange_fn = range


def dispatch_worker_task(task_args):
    worker, n_str, a_str, b_str, worker_idx = task_args
    factors = worker.mymap(n_str, a_str, b_str)
    if hasattr(factors, 'value'):
        factors = factors.value
    return factors


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers if workers is not None else []

    def solve(self):
        start_time = time.time()
        n = self.read_input()
        limit = int(math.isqrt(n)) if hasattr(math, 'isqrt') else int(math.floor(math.sqrt(n)))
        num_workers = len(self.workers)

        if num_workers == 0:
            factors = Solver.mymap(str(n), "2", str(limit + 1))
        else:
            total_range = limit - 2 + 1
            chunk_size = int(math.ceil(float(total_range) / float(num_workers)))
            tasks = []
            for i in xrange_fn(num_workers):
                a = 2 + i * chunk_size
                b = min(2 + (i + 1) * chunk_size, limit + 1)
                if a < b:
                    tasks.append((self.workers[i], str(n), str(a), str(b), i))

            pool = ThreadPool(processes=len(tasks))
            results = pool.map(dispatch_worker_task, tasks)
            pool.close()
            pool.join()
            factors = self.myreduce(results)

        elapsed_time = time.time() - start_time
        self.write_output(n, factors, elapsed_time)

    @staticmethod
    @expose
    def mymap(n_str, a_str, b_str):
        n = int(n_str)
        a = int(a_str)
        b = int(b_str)
        local_factors = []
        for d in xrange_fn(a, b):
            if n % d == 0:
                local_factors.append(d)
                other = n // d
                if other != d:
                    local_factors.append(other)
        return local_factors

    @staticmethod
    @expose
    def myreduce(mapped):
        all_factors = set()
        for values in mapped:
            if hasattr(values, 'value'):
                values = values.value
            for f in values:
                all_factors.add(f)
        return sorted(list(all_factors))

    def read_input(self):
        with open(self.input_file_name, "r") as f:
            return int(f.readline().strip())

    def write_output(self, n, factors, elapsed_time):
        if not self.output_file_name:
            return
        with open(self.output_file_name, "w") as f:
            f.write("Target_N: {}\n".format(n))
            f.write("Factors_Count: {}\n".format(len(factors)))
            f.write("Factors: {}\n".format(", ".join(map(str, factors))))
            f.write("Elapsed_seconds: {:.6f}\n".format(elapsed_time))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
        s = Solver(workers=None, input_file_name=inp, output_file_name=out)
        s.solve()
