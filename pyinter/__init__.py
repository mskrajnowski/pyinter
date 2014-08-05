'''
Pyinter is a python interval library which deals with interval
arithmetic and sets of intervals (discontinuous ranges).
'''

from pyinter.bound import Bound
from pyinter.interval import Interval
from pyinter.interval_set import IntervalSet
from pyinter import examples

__all__ = ['Bound', 'Interval', 'IntervalSet', 'examples']
