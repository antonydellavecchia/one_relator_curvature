import time

def timeit(method):
    def timed(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        print(f"{method.__name__}, {total_time}")

        return result
    return timed
