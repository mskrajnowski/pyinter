import random
import time
import unittest2

from pyinter import Interval


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r %2.2f sec' % (method.__name__, te - ts))
        return result

    return timed


class TestPerformance(unittest2.TestCase):

    def setUp(self):
        self.intervals = []
        data = 'abcde'

        for i in range(1024):
            lower = random.randint(0, 100)
            upper = lower + 100
            self.intervals.append(Interval.closed(
                lower, upper, random.choice(data)
            ))

    @timeit
    def test_and(self):
        for i in range(10):
            pairs = zip(*[self.intervals[i::2] for i in (0, 1)])
            for a, b in pairs:
                a & b

    @timeit
    def test_or(self):
        for i in range(10):
            pairs = zip(*[self.intervals[i::2] for i in (0, 1)])
            for a, b in pairs:
                a | b

    @timeit
    def test_or_grouped(self):
        queue = list(self.intervals)

        while len(queue) > 1:
            pairs = zip(*[queue[i::2] for i in (0, 1)])
            queue = []
            for a, b in pairs:
                queue.append(a | b)

    @timeit
    def test_and_grouped(self):
        queue = list(self.intervals)

        while len(queue) > 1:
            pairs = zip(*[queue[i::2] for i in (0, 1)])
            queue = []
            for a, b in pairs:
                queue.append(a & b)

if __name__ == '__main__':
    test_or = TestPerformance('test_or')
    test_or.setUp()
    test_or()

    test_and = TestPerformance('test_and')
    test_and.setUp()
    test_and()

    test_or_grouped = TestPerformance('test_or_grouped')
    test_or_grouped.setUp()
    test_or_grouped()
