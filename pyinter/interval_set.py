from collections import Iterable
import heapq


class IntervalSet(set):
    """
    A class to hold collections of intervals,
    otherwise known as discontinuous ranges.

    >>> from .interval import Interval
    >>> intervals = (
    ...     Interval.closed(2, 3),
    ...     Interval.open(1, 2),
    ...     Interval.closed(5, 6),
    ... )

    >>> IntervalSet(intervals)
    IntervalSet((1, 3], [5, 6])

    If you're sure that intervals passed don't overlap and aren't adjacent
    you can pass check_overlaps=False, which will cause the set to just store
    the passed intervals as they are.
    It's used internally by the Interval when creating sets.
    >>> IntervalSet(intervals, check_overlaps=False)
    IntervalSet((1, 2), [2, 3], [5, 6])
    """

    def __init__(self, iterable=None, check_overlaps=True):
        raw = super(IntervalSet, self)
        raw.__init__()

        if iterable:
            if check_overlaps:
                self.update(iterable)
            else:
                raw.update(iterable)

    def __contains__(self, item):
        """
        Checks whether the value is inside any of the intervals in the set.

        >>> from .interval import Interval
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
        return '{}({})'.format(self.__class__.__name__, str(self))

    def __unicode__(self):
        return u', '.join(unicode(interval) for interval in sorted(self))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __and__(self, other):
        return self.intersection(other)

    def __or__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return self.difference(other)

    def intersection(self, *others):
        """
        Returns the intersection between this set and other sets
        and/or intervals. The return value can be either an IntervalSet,
        an Interval or None.
        set.intersection(a, b) <=> set & a & b

        >>> from .interval import Interval
        >>> set_a = Interval.open(1, 3, 'some') | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5, 'data')
        >>> set_a & set_b
        IntervalSet((1, 2]: some, [4, 5): data)
        >>> set_a & set_b == set_a.intersection(set_b)
        True
        >>> set_a & Interval.closed(0, 2, 'data')
        <Interval (1, 2]: some, data>
        >>> set_a & Interval.open(5, 6)
        """
        result = self.__class__(self, check_overlaps=False)
        result.intersection_update(*others)

        if len(result) == 0:
            return None

        if len(result) == 1:
            return iter(result).next()

        return result

    def intersection_update(self, *others):
        """
        Updates the set to include only the intersection of itself and others.

        >>> from .interval import Interval
        >>> set_a = Interval.open(1, 3) | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> result = IntervalSet(set_a)
        >>> result.intersection_update(set_b)
        >>> result
        IntervalSet((1, 2], [4, 5))
        >>> result == set_a & set_b
        True
        """

        for other in others:
            self_queue = sorted(self)
            self.clear()

            if isinstance(other, Iterable):
                other_queue = sorted(other)
            else:
                other_queue = [other]

            raw = super(IntervalSet, self)

            while self_queue and other_queue:
                self_interval = self_queue[0]
                other_interval = other_queue[0]

                intersection = self_interval & other_interval
                if intersection:
                    raw.add(intersection)

                pop_from = (
                    self_queue if other_interval.upper > self_interval.upper
                    else other_queue
                )

                pop_from.pop(0)

    def union(self, *others):
        """
        Calculates the union of the current set with other sets
        and/or intervals. The return value can be an IntervalSet or
        an Interval.

        set.union(a, b) <=> set | a | b

        >>> from .interval import Interval
        >>> set_a = Interval.open(1, 3, 'some') | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5, 'data')
        >>> set_b_no_data = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> set_a | set_b
        IntervalSet([0, 1], (1, 3): some, (3, 5): data, [5, 5])
        >>> set_a.union(set_b)
        IntervalSet([0, 1], (1, 3): some, (3, 5): data, [5, 5])
        >>> set_a | set_b == set_a.union(set_b)
        True
        >>> set_a | set_b_no_data
        IntervalSet([0, 1], (1, 3): some, (3, 5])
        >>> set_a | Interval.open(2, 10)
        IntervalSet((1, 3): some, [3, 10))
        >>> set_a | Interval.open(2, 10, 'some')
        <Interval (1, 10): some>
        """

        result = self.__class__(self, check_overlaps=False)
        result.update(*others)

        if len(result) == 0:
            return None

        if len(result) == 1:
            return iter(result).next()

        return result

    def update(self, *others):
        """
        Updates the set adding new intervals from others (which can be
        either sets or intervals).

        >>> from .interval import Interval
        >>> set_a = Interval.open(1, 3) | Interval.closed(4, 5)
        >>> set_b = Interval.closed(0, 2) | Interval.open(3, 5)
        >>> result = IntervalSet(set_a)
        >>> result.update(set_b)
        >>> result
        IntervalSet([0, 3), (3, 5])
        >>> result == set_a | set_b
        True
        """

        queue = list(self)
        heapq.heapify(queue)

        for other in others:
            if isinstance(other, Iterable):
                for interval in other:
                    heapq.heappush(queue, interval)
            else:
                heapq.heappush(queue, other)

        self.clear()
        raw = super(IntervalSet, self)
        last_interval = None

        while queue:
            interval = heapq.heappop(queue)

            if not last_interval:
                last_interval = interval
                continue

            union = interval | last_interval
            if isinstance(union, IntervalSet):
                for i in union:
                    if i.lower < interval.lower:
                        raw.add(i)
                    elif i.lower == interval.lower:
                        last_interval = i
                    else:
                        heapq.heappush(queue, i)
            else:
                last_interval = union

        if last_interval:
            raw.add(last_interval)

    def add(self, other):
        self.update((other, ))
