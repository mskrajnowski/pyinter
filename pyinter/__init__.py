'''
Pyinter is a python interval library which deals with interval
arithmetic and sets of intervals (discontinuous ranges).
'''

from pyinter.bound import Bound
from pyinter.interval import (
    Interval,
    union,
    intersection,
    set_intersection,
    invert,
    difference,
)
from pyinter.interval_set import IntervalSet

__all__ = [
    'Bound',
    'Interval',
    'IntervalSet',
    'union',
    'intersection',
    'set_intersection',
    'invert',
    'difference',
]
