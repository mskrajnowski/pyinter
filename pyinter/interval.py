import operator
from collections import Iterable

from sortedcontainers import SortedSet

from .interval_set import IntervalSet
from .bound import Bound
from .extrema import INFINITY, NEGATIVE_INFINITY


class Interval(object):
    """
    An interval class with methods associated with mathematical intervals.
    This class can deal with any comparible objects and can store any arbitrary
    data.

    **Examples**
    An open interval:

    >>> Interval.open(100.2, 800.9)
    <Interval (100.2, 800.9)>

    A closed interval:

    >>> Interval.closed(100.2, 800.9)
    <Interval [100.2, 800.9]>

    An open-closed interval:

    >>> Interval.open_closed(100.2, 800.9)
    <Interval (100.2, 800.9]>

    A closed-open interval:

    >>> Interval.closed_open(100.2, 800.9)
    <Interval [100.2, 800.9)>

    Interval with data:

    >>> Interval.open(100.2, 800.9, 'hello')
    <Interval (100.2, 800.9): hello>

    Using the Interval constructor directly:

    >>> Interval(Bound(100.2, operator.gt), Bound(800.9, operator.lt), 'hello')
    <Interval (100.2, 800.9): hello>
    """

    _lower = None
    _upper = None

    # _set_class = SortedSet
    _set_class = IntervalSet

    def _create_set(self, intervals):
        return self._set_class(intervals, check_overlaps=False)

    @property
    def lower(self):
        return self._lower

    @property
    def upper(self):
        return self._upper

    @property
    def data(self):
        return self._data

    @classmethod
    def open(cls, lower_value, upper_value, data=None, **kwargs):
        """
        Helper function to construct an interval object with open lower
        and upper.
        """
        return cls(
            Bound(lower_value, operator.gt),
            Bound(upper_value, operator.lt),
            data=data,
            **kwargs
        )

    @classmethod
    def closed(cls, lower_value, upper_value, data=None, **kwargs):
        """
        Helper function to construct an interval object with closed lower
        and upper.
        """
        return cls(
            Bound(lower_value, operator.ge),
            Bound(upper_value, operator.le),
            data=data,
            **kwargs
        )

    @classmethod
    def open_closed(cls, lower_value, upper_value, data=None, **kwargs):
        """
        Helper function to construct an interval object with a open lower
        and closed upper.
        """
        return cls(
            Bound(lower_value, operator.gt),
            Bound(upper_value, operator.le),
            data=data,
            **kwargs
        )

    @classmethod
    def closed_open(cls, lower_value, upper_value, data=None, **kwargs):
        """
        Helper function to construct an interval object with a closed lower
        and open upper.
        """
        return cls(
            Bound(lower_value, operator.ge),
            Bound(upper_value, operator.lt),
            data=data,
            **kwargs
        )

    def __init__(self, lower, upper, data=None, data_set=None):
        """
        Create a new :class:`~pyinter.Interval` object, lower and upper
        should be `~pyinter.Bound` instances.
        You can attach any arbitrary data to the interval through data.
        """
        if lower > upper:
            raise ValueError(
                'lower({lower}) must be smaller '
                'than upper({upper})'
                .format(lower=lower, upper=upper)
            )

        self._lower = lower
        self._upper = upper

        self._data = set()
        if data:
            self._data.add(data)
        if data_set:
            self._data.update(data_set)

    def __repr__(self):
        return "<{} {}>".format(
            self.__class__.__name__,
            str(self),
        )

    def __unicode__(self):
        data_str = u''
        if self.data:
            data_str = u': {}'.format(
                u', '.join(unicode(item) for item in self.data)
            )

        return u"{}, {}{}".format(
            self._lower,
            self._upper,
            data_str,
        )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __cmp__(self, other):
        """
        >>> Interval.open(1, 2) < Interval.open(2, 3)
        True

        >>> Interval.closed(1, 2) < Interval.open(1, 2)
        True

        >>> Interval.open(1, 2) < Interval.open(1, 3)
        True
        """

        return (
            cmp(self.lower, other.lower)
            or cmp(self.upper, other.upper)
        )

    def __eq__(self, other):
        return (
            self.lower == other.lower
            and self.upper == other.upper
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.lower, self.upper))

    def __and__(self, other):
        if other and not isinstance(other, Interval):
            return other & self

        return self.intersect(other)

    def __or__(self, other):
        if other and not isinstance(other, Interval):
            return other | self

        return self.union(other)

    def __add__(self, other):
        return self | other

    def __sub__(self, other):
        if other and not isinstance(other, Interval):
            return self._create_set((self, )) - other

        return self.difference(other)

    def _contains_value(self, value):
        """
        Helper function for __contains__ to check a single value
        is contained within the interval
        """
        return value in self.lower and value in self.upper

    def __contains__(self, item):
        """
        >>> open = Interval.open(1, 3)
        >>> closed = Interval.closed(1, 3)

        >>> [i in open for i in (0, 1, 2, 3, 4)]
        [False, False, True, False, False]

        >>> [i in closed for i in (0, 1, 2, 3, 4)]
        [False, True, True, True, False]

        >>> open in closed
        True

        >>> closed in open
        False

        >>> intervals = [
        ...     Interval.open(0, 2),
        ...     Interval.closed(1, 2),
        ...     Interval.closed(2, 2),
        ...     Interval.closed(2, 3),
        ...     Interval.open(2, 4),
        ... ]

        >>> [i in open for i in intervals]
        [False, False, True, False, False]

        >>> [i in closed for i in intervals]
        [False, True, True, True, False]
        """

        if isinstance(item, Interval):
            lower_in = (
                self._contains_value(item.lower.value)
                or self.lower == item.lower
            )

            upper_in = (
                self._contains_value(item.upper.value)
                or self.upper == item.upper
            )

            return lower_in and upper_in
        else:
            return self._contains_value(item)

    def overlaps(self, other):
        """
        If self and other have any overlaping values returns True,
        otherwise returns False

        >>> open = Interval.open(1, 3)
        >>> closed = Interval.closed(1, 3)

        >>> intervals = [
        ...     Interval.closed(0, 1),
        ...     Interval.open(1, 2),
        ...     Interval.closed(2, 2),
        ...     Interval.open(2, 3),
        ...     Interval.closed(3, 4),
        ... ]

        >>> [open.overlaps(i) for i in intervals]
        [False, True, True, True, False]

        >>> [closed.overlaps(i) for i in intervals]
        [True, True, True, True, True]
        """

        return self.lower <= other.upper and self.upper >= other.lower

    def adjacent(self, other):
        """
        Checks whether the current Interval is next to the other
        (there can't be any values that would fit between the two intervals),
        eg.:

        >>> Interval.open(1, 3).adjacent(Interval.closed(3, 4))
        True

        >>> Interval.closed(1, 3).adjacent(Interval.open(0, 1))
        True
        """

        return (
            self.lower.is_opposite_of(other.upper)
            or self.upper.is_opposite_of(other.lower)
        )

    def intersect(self, other):
        """
        Returns a new :class:`~pyinter.Interval` representing
        the intersection of this :class:`~pyinter.Interval`
        with the other :class:`~pyinter.Interval`

        >>> Interval.open(1, 3) & Interval.closed(0, 1, 'data')
        >>> Interval.closed(1, 3) & Interval.closed(0, 1, 'data')
        <Interval [1, 1]: data>

        >>> Interval.open(1, 3) & Interval.open(1, 2, 'data')
        <Interval (1, 2): data>

        >>> Interval.open(1, 3) & Interval.closed(2, 2, 'data')
        <Interval [2, 2]: data>

        >>> Interval.open(1, 3) & Interval.open(2, 3, 'data')
        <Interval (2, 3): data>

        >>> Interval.closed(1, 3) & Interval.closed(3, 4, 'data')
        <Interval [3, 3]: data>
        >>> Interval.open(1, 3) & Interval.closed(3, 4, 'data')
        """

        if other is None:
            return None

        if self.overlaps(other):
            data = set(self.data)
            data.update(other.data)

            return self.__class__(
                max(self.lower, other.lower),
                min(self.upper, other.upper),
                data_set=data,
            )
        else:
            return None

    def union(self, other):
        """
        Returns a new Interval or an :class:`~pyinter.IntervalSet`
        representing the union of this :class:`~pyinter.Interval`
        with the other :class:`~pyinter.Interval`.

        If the two intervals are overlaping and contain the same data then
        this will return an :class:`~pyinter.Interval`, otherwise this returns
        an :class:`~pyinter.IntervalSet`.

        >>> Interval.open(1, 3) | Interval.closed(0, 1)
        <Interval [0, 3)>
        >>> Interval.closed(1, 3) | Interval.closed(0, 1, 'data')
        IntervalSet([0, 1]: data, (1, 3])

        >>> Interval.open(1, 3, 'some') | Interval.open(1, 2, 'more')
        IntervalSet((1, 2): some, more, [2, 3): some)

        >>> Interval.open(1, 2) | Interval.open(3, 4)
        IntervalSet((1, 2), (3, 4))

        >>> Interval.closed(4, 5) | Interval.open(1, 10, 'some')
        <Interval (1, 10): some>
        """

        if other is None:
            return self

        cls = self.__class__
        overlapping = self.overlaps(other)
        adjacent = self.adjacent(other)

        if not overlapping and not adjacent:
            return self._create_set((self, other))

        left, right = (self, other) if self <= other else (other, self)

        common_data = left.data & right.data
        left_contrib = left.data - common_data
        right_contrib = right.data - common_data

        if not left_contrib and not right_contrib:
            return cls(
                min(self.lower, other.lower),
                max(self.upper, other.upper),
                data_set=common_data,
            )

        if adjacent and (left_contrib or right_contrib):
            return self._create_set((self, other))

        if right in left and not right_contrib:
            return left

        if left in right and not left_contrib:
            return right

        intersection = left & right
        items = []

        if left.lower < intersection.lower:
            items.append(cls(
                left.lower,
                intersection.upper if not right_contrib
                else ~intersection.lower,
                data_set=left.data,
            ))

        if left_contrib and right_contrib:
            items.append(intersection)

        if right.upper > intersection.upper:
            items.append(cls(
                intersection.lower if not left_contrib
                else ~intersection.upper,
                right.upper,
                data_set=right.data,
            ))

        if len(items) == 1:
            return items[0]

        return self._create_set(items)

    def difference(self, other):
        """
        Returns a new Interval or an :class:`~pyinter.IntervalSet`
        representing the difference between this :class:`~pyinter.Interval`
        and the other :class:`~pyinter.Interval`.

        >>> Interval.open(1, 4) - Interval.open(1, 2)
        <Interval [2, 4)>
        >>> Interval.closed(1, 4) - Interval.open(1, 2)
        IntervalSet([1, 1], [2, 4])
        >>> Interval.closed(1, 4) - Interval.open(2, 3)
        IntervalSet([1, 2], [3, 4])
        >>> Interval.open(1, 4) - Interval.open(3, 4)
        <Interval (1, 3]>
        >>> Interval.open(1, 2) - Interval.open(1, 2)
        >>> Interval.closed(1, 2) - Interval.open(1, 2)
        IntervalSet([1, 1], [2, 2])
        >>> Interval.open(1, 2) - Interval.open(0, 3)
        """

        if other is None or not self.overlaps(other):
            return self

        cls = self.__class__
        intersection = self & other
        items = []

        if self.lower < intersection.lower:
            items.append(cls(
                self.lower, ~intersection.lower,
                data_set=self.data
            ))

        if self.upper > intersection.upper:
            items.append(cls(
                ~intersection.upper, self.upper,
                data_set=self.data
            ))

        if not items:
            return None

        if len(items) == 1:
            return items[0]

        return self._create_set(items)

    def complement(self):
        return self._create_set([
            self.__class__(
                Bound(NEGATIVE_INFINITY, operator.gt),
                ~self.lower,
                data_set=self.data,
            ),
            self.__class__(
                ~self.upper,
                Bound(INFINITY, operator.lt),
                data_set=self.data,
            ),
        ])

    def copy(self, other):
        return self.__class__(
            Bound(self.lower.value, self.lower.operator),
            Bound(self.upper.value, self.upper.operator),
            data_set=self.data,
        )
