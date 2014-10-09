import itertools

# Interval is used in doctests
from .interval import Interval, set_intersection, difference
from .interval import union as _union


class IntervalSet(object):
    """
    A class to hold collections of intervals,
    otherwise known as discontinuous ranges.

    >>> intervals = (
    ...     Interval.closed(2, 3),
    ...     Interval.open(1, 2),
    ...     Interval.closed(5, 6),
    ... )

    >>> IntervalSet(intervals)
    <IntervalSet (1, 3], [5, 6]>

    If you're sure that intervals passed don't overlap and aren't adjacent
    you can pass check_overlaps=False, which will cause the set to just store
    the passed intervals as they are.
    It's used internally by the Interval when creating sets.

    >>> IntervalSet(intervals, check_overlaps=False)
    <IntervalSet (1, 2), [2, 3], [5, 6]>
    """

    def __init__(self, iterable=None, check_overlaps=True):
        self.intervals = []

        if iterable:
            if check_overlaps:
                self.update(iterable)
            else:
                self.intervals.extend(iterable)

    def __contains__(self, item):
        """
        Checks whether the value is inside any of the intervals in the set.

        >>> set = Interval.open(0, 2) | Interval.closed(3, 4)
        >>> [i in set for i in range(6)]
        [False, True, False, True, True, False]

        >>> Interval.open(1, 2) in set
        True
        >>> Interval.closed(3, 3) in set
        True
        >>> Interval.closed(2, 3) in set
        False
        >>> Interval.open(1, 4) in set
        False
        """
        for interval in self:
            if item in interval:
                return True
        return False

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str(self))

    def __unicode__(self):
        return u', '.join(unicode(interval) for interval in sorted(self))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __and__(self, other):
        return self.intersection(other)

    def __or__(self, other):
        return self.union(other)

    def __add__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return self.difference(other)

    def __iter__(self):
        return iter(self.intervals)

    def __eq__(self, other):
        if isinstance(other, IntervalSet):
            return self.intervals == other.intervals
        return False

    def _iter_other_sets(self, others):
        for other in others:
            yield (other, ) if isinstance(other, Interval) else other

    def _iter_other_intervals(self, others):
        for other in others:
            if isinstance(other, Interval):
                yield other
            else:
                for interval in other:
                    yield interval

    def intersection(self, *others):
        """
        Returns the intersection between this set and other sets
        and/or intervals.
        set.intersection(a, b) <=> set & a & b

        >>> set_a = Interval.open(1, 3, 'some') | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5, 'data')
        >>> set_a & set_b
        <IntervalSet (1, 2]: some, [4, 5): data>
        >>> set_a & set_b == set_a.intersection(set_b)
        True
        >>> set_a & Interval.closed(0, 2, 'data')
        <IntervalSet (1, 2]: data, some>
        >>> set_a & Interval.open(5, 6)
        <IntervalSet >
        """

        result = set_intersection(self, *self._iter_other_sets(others))
        return self.__class__(result, check_overlaps=False)

    def intersection_update(self, *others):
        """
        Updates the set to include only the intersection of itself and others.

        >>> set_a = Interval.open(1, 3) | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> result = IntervalSet(set_a)
        >>> result.intersection_update(set_b)
        >>> result
        <IntervalSet (1, 2], [4, 5)>
        >>> result == set_a & set_b
        True
        """

        result = set_intersection(self, *self._iter_other_sets(others))
        self.intervals = result

    def union(self, *others):
        """
        Calculates the union of the current set with other sets
        and/or intervals. The return value can be an IntervalSet or
        an Interval.

        set.union(a, b) <=> set | a | b

        >>> set_a = Interval.open(1, 3, 'some') | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5, 'data')
        >>> set_b_no_data = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> set_a | set_b
        <IntervalSet [0, 1], (1, 3): some, (3, 5): data, [5, 5]>
        >>> set_a.union(set_b)
        <IntervalSet [0, 1], (1, 3): some, (3, 5): data, [5, 5]>
        >>> set_a | set_b == set_a.union(set_b)
        True
        >>> set_a | set_b_no_data
        <IntervalSet [0, 1], (1, 3): some, (3, 5]>
        >>> set_a | Interval.open(2, 10)
        <IntervalSet (1, 3): some, [3, 10)>
        >>> set_a | Interval.open(2, 10, 'some')
        <IntervalSet (1, 10): some>
        """

        intervals = itertools.chain(
            self,
            *self._iter_other_sets(others)
        )
        result = _union(*intervals)
        return self.__class__(result, check_overlaps=False)

    def update(self, *others):
        """
        Updates the set adding new intervals from others (which can be
        either sets or intervals).

        >>> set_a = Interval.open(1, 3) | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> result = IntervalSet(set_a)
        >>> result.update(set_b)
        >>> result
        <IntervalSet [0, 3), (3, 5]>
        >>> result == set_a | set_b
        True
        """

        intervals = itertools.chain(
            self,
            *self._iter_other_sets(others)
        )
        result = _union(*intervals)
        self.intervals = result

    def difference(self, *others):
        """
        Returns intervals, which are contained in this interval set, but not
        in any of the other sets and/or intervals.
        The return value can be either an IntervalSet, an Interval or None.
        set.difference(a, b) <=> set - a - b

        >>> set_a = Interval.closed(0, 2) | Interval.open(3, 5, 'data')
        >>> set_b = Interval.open(1, 3, 'some') | Interval.closed(4, 5)
        >>> set_a - Interval.open(1, 10)
        <IntervalSet [0, 1]>
        >>> set_a - Interval.open(1, 4)
        <IntervalSet [0, 1], [4, 5): data>
        >>> set_a - set_b
        <IntervalSet [0, 1], (3, 4): data>
        >>> set_b - set_a
        <IntervalSet (2, 3): some, [5, 5]>
        >>> set_b - set_a == set_b.difference(set_a)
        True
        >>> set_b - set_b
        <IntervalSet >
        >>> set_a - set_a
        <IntervalSet >
        >>> set_a - (set_b | set_a)
        <IntervalSet >
        """

        result = difference(self, self._iter_other_intervals(others))
        return self.__class__(result, check_overlaps=False)

    def difference_update(self, *others):
        """
        Updates the set removing all intervals which collide with intervals
        in others (which can be either sets or intervals).

        >>> set_a = Interval.closed(0, 2) | Interval.open(3, 5, 'data')

        >>> result = IntervalSet(set_a)
        >>> result.difference_update(Interval.open(1, 10))
        >>> result
        <IntervalSet [0, 1]>

        >>> result = IntervalSet(set_a)
        >>> result.difference_update(Interval.open(1, 4))
        >>> result
        <IntervalSet [0, 1], [4, 5): data>
        """

        result = difference(self, self._iter_other_intervals(others))
        self.intervals = result

    def add(self, other):
        self.update((other, ))
