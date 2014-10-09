"""
Provides the INFINITY and NEGATIVE_INFINITY constants.
INFINITY is greater than everything, apart from itself.
NEGATIVE_INFINITY is lesser than everything, apart from itself.

>>> INFINITY != 0 and not INFINITY == 0
True
>>> NEGATIVE_INFINITY != 0 and not NEGATIVE_INFINITY == 0
True
>>> INFINITY > 0 > NEGATIVE_INFINITY and INFINITY >= 0 >= NEGATIVE_INFINITY
True
>>> NEGATIVE_INFINITY < 0 < INFINITY and NEGATIVE_INFINITY <= 0 <= INFINITY
True
>>> INFINITY < 0 < NEGATIVE_INFINITY or INFINITY <= 0 <= NEGATIVE_INFINITY
False
>>> NEGATIVE_INFINITY > 0 > INFINITY or NEGATIVE_INFINITY >= 0 >= INFINITY
False

>>> from datetime import date, datetime
>>> d = date(2014, 1, 1)
>>> dt = datetime(2014, 1, 1, 0, 0)
>>> INFINITY != d and not INFINITY == d
True
>>> INFINITY != dt and not INFINITY == dt
True
>>> NEGATIVE_INFINITY != d and not NEGATIVE_INFINITY == d
True
>>> NEGATIVE_INFINITY != dt and not NEGATIVE_INFINITY == dt
True
>>> INFINITY > d > NEGATIVE_INFINITY and INFINITY >= d >= NEGATIVE_INFINITY
True
>>> INFINITY > dt > NEGATIVE_INFINITY and INFINITY >= dt >= NEGATIVE_INFINITY
True
>>> NEGATIVE_INFINITY < d < INFINITY and NEGATIVE_INFINITY <= d <= INFINITY
True
>>> NEGATIVE_INFINITY < dt < INFINITY and NEGATIVE_INFINITY <= dt <= INFINITY
True

>>> INFINITY > INFINITY
False
>>> NEGATIVE_INFINITY < NEGATIVE_INFINITY
False

>>> import sys
>>> INFINITY > sys.maxsize and -sys.maxsize > NEGATIVE_INFINITY
True
>>> sys.maxsize < INFINITY and NEGATIVE_INFINITY < -sys.maxsize
True

>>> sorted(set([INFINITY, INFINITY, NEGATIVE_INFINITY, NEGATIVE_INFINITY]))
[-inf, inf]
"""


class _Indeterminate(object):
    # required for comparisons with dates, times, datetimes
    # https://docs.python.org/2/library/datetime.html#date-objects
    timetuple = tuple()

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return hash(repr(self))


class _NegativeInfinity(_Indeterminate):
    def __lt__(self, other):
        if self == other:
            return False
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __repr__(self):
        return '-inf'


class _Infinity(_Indeterminate):
    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __gt__(self, other):
        if other == self:
            return False
        return True

    def __ge__(self, other):
        return True

    def __repr__(self):
        return 'inf'


INFINITY = _Infinity()
NEGATIVE_INFINITY = _NegativeInfinity()
