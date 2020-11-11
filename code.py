#Code stolen from micropython benchmarks

from math import sin, cos, sqrt

#floating point
class Point(object):
    __slots__ = ("x", "y", "z")

    def __init__(self, i):
        self.x = x = sin(i)
        self.y = cos(i) * 3
        self.z = (x * x) / 2

    def __repr__(self):
        return "<Point: x=%s, y=%s, z=%s>" % (self.x, self.y, self.z)

    def normalize(self):
        x = self.x
        y = self.y
        z = self.z
        norm = sqrt(x * x + y * y + z * z)
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def maximize(self, other):
        self.x = self.x if self.x > other.x else other.x
        self.y = self.y if self.y > other.y else other.y
        self.z = self.z if self.z > other.z else other.z
        return self


def maximize(points):
    next = points[0]
    for p in points[1:]:
        next = next.maximize(p)
    return next


def benchmark(n):
    points = [None] * n
    for i in range(n):
        points[i] = Point(i)
    for p in points:
        p.normalize()
    return maximize(points)


###########################################################################
# Benchmark interface
bm_params_float = {
    (50, 25): (1, 150),
    (100, 100): (1, 50),
    (1000, 1000): (10, 1500),
    (5000, 1000): (20, 3000),
}


#n-queens
# Pure-Python implementation of itertools.permutations().
def permutations(iterable, r=None):
    """permutations(range(3), 2) --> (0,1) (0,2) (1,0) (1,2) (2,0) (2,1)"""
    pool = tuple(iterable)
    n = len(pool)
    if r is None:
        r = n
    indices = list(range(n))
    cycles = list(range(n - r + 1, n + 1))[::-1]
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i + 1 :] + indices[i : i + 1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return


# From http://code.activestate.com/recipes/576647/
def n_queens(queen_count):
    """N-Queens solver.
    Args: queen_count: the number of queens to solve for, same as board size.
    Yields: Solutions to the problem, each yielded value is a N-tuple.
    """
    cols = range(queen_count)
    for vec in permutations(cols):
        if queen_count == len(set(vec[i] + i for i in cols)) == len(set(vec[i] - i for i in cols)):
            yield vec
###########################################################################
# Benchmark interface

bm_params_nqueens = {
    (50, 25): (1, 5),
    (100, 25): (1, 5),
    (1000, 100): (1, 7),
    (5000, 100): (1, 8),
}

def bm_setup_float(params):
    state = None

    def run():
        nonlocal state
        for _ in range(params[0]):
            state = benchmark(params[1])

    def result():
        return params[0] * params[1], "Point(%.4f, %.4f, %.4f)" % (state.x, state.y, state.z)

    return run, result
    

def bm_setup_nqueens(params):
    res = None

    def run():
        nonlocal res
        for _ in range(params[0]):
            res = len(list(n_queens(params[1])))

    def result():
        return params[0] * 10 ** (params[1] - 3), res

    return run, result


def bm_run(N, M):
    try:
        from utime import ticks_us, ticks_diff
    except ImportError:
        import time

        ticks_us = lambda: int(time.monotonic() * 1000)

        ticks_diff = lambda a, b: a - b

    # Pick sensible parameters given N, M
    ##ugly as sin. Should refactor
    cur_nm = (0, 0)
    param_float = None
    for nm, p in bm_params_float.items():
        if 10 * nm[0] <= 12 * N and nm[1] <= M and nm > cur_nm:
            cur_nm = nm
            param_float = p
    if param_float is None:
        print(-1, -1, "no matching params")
        return
        
    cur_nm = (0, 0)
    param_nqueens = None
    for nm, p in bm_params_nqueens.items():
        if 10 * nm[0] <= 12 * N and nm[1] <= M and nm > cur_nm:
            cur_nm = nm
            param_nqueens = p
    if param_nqueens is None:
        print(-1, -1, "no matching params")
        return

    # Run and time benchmark
    #print("float benchmark")
    total_ticks_diff=0
    run, result = bm_setup_float(param_float)
    for _ in range(10):
        t0 = ticks_us()
        run()
        t1 = ticks_us()
        norm, out = result()
        #print(ticks_diff(t1, t0), norm, out)
        total_ticks_diff = total_ticks_diff + ticks_diff(t1, t0)
    print(board, "," , processor, ",", speed, ",",circuitpy_version, ", average float ,", total_ticks_diff / 10)
    
    #print("nqueens benchmark")
    total_ticks_diff=0
    run, result = bm_setup_nqueens(param_nqueens)
    for _ in range(10):
        t0 = ticks_us()
        run()
        t1 = ticks_us()
        norm, out = result()
        #print(ticks_diff(t1, t0), norm, out)
        total_ticks_diff = total_ticks_diff + ticks_diff(t1, t0)
    print(board, "," ,processor, ",", speed, ",", circuitpy_version, ", average nqueens ,", total_ticks_diff / 10)

board = "Adafruit Circuit Playground Bluefruit"
processor = "nRF52840"
speed = "64"
circuitpy_version = "6.0.0-rc1"
bm_run(100,100)
