import operator
import itertools

from .bound import Bound
from .extrema import INFINITY, NEGATIVE_INFINITY


def _list_bounds(intervals):
    """
    Returns a sorted list of bounds that belong to the given intervals.
    Each item is a tuple of (bound, owner_interval).
    """

    bounds = []
    for interval in intervals:
        bounds.extend((
            (interval.lower, interval),
            (interval.upper, interval),
        ))

    return sorted(bounds, key=lambda i: i[0])


def union(*intervals, **kwargs):
    """
    Returns the union of intervals.

    >>> union()
    []

    No data:
    >>> union(Interval.closed(0, 2), Interval.closed(4, 10))
    [<Interval [0, 2]>, <Interval [4, 10]>]

    >>> union(Interval.closed(3, 5), Interval.closed(4, 10))
    [<Interval [3, 10]>]

    >>> union(Interval.closed(6, 8), Interval.closed(4, 10))
    [<Interval [4, 10]>]
    >>> union(Interval.closed(9, 11), Interval.closed(4, 10))
    [<Interval [4, 11]>]
    >>> union(Interval.closed(12, 14), Interval.closed(4, 10))
    [<Interval [4, 10]>, <Interval [12, 14]>]

    >>> union(Interval.closed(0, 2), Interval.closed(0, 5))
    [<Interval [0, 5]>]
    >>> union(Interval.closed(3, 5), Interval.closed(0, 5))
    [<Interval [0, 5]>]

    >>> union(Interval.closed(0, 2), Interval.closed(0, 2))
    [<Interval [0, 2]>]

    >>> union(Interval.closed(0, 1), Interval.open(1, 2))
    [<Interval [0, 2)>]

    With data:
    >>> union(Interval.closed(0, 2, 'data'), Interval.closed(4, 10))
    [<Interval [0, 2]: data>, <Interval [4, 10]>]
    >>> union(Interval.closed(3, 5, 'data'), Interval.closed(4, 10))
    [<Interval [3, 5]: data>, <Interval (5, 10]>]
    >>> union(Interval.closed(6, 8, 'data'), Interval.closed(4, 10))
    [<Interval [4, 6)>, <Interval [6, 8]: data>, <Interval (8, 10]>]
    >>> union(Interval.closed(9, 11, 'data'), Interval.closed(4, 10))
    [<Interval [4, 9)>, <Interval [9, 11]: data>]
    >>> union(Interval.closed(12, 14, 'data'), Interval.closed(4, 10))
    [<Interval [4, 10]>, <Interval [12, 14]: data>]

    >>> union(Interval.closed(0, 2, 'data'), Interval.closed(0, 5))
    [<Interval [0, 2]: data>, <Interval (2, 5]>]
    >>> union(Interval.closed(3, 5, 'data'), Interval.closed(0, 5))
    [<Interval [0, 3)>, <Interval [3, 5]: data>]

    >>> union(Interval.closed(0, 2, 'data'), Interval.closed(0, 2))
    [<Interval [0, 2]: data>]

    Complex case:

    0123456789012345678901234
         [ b   ]    [a ]
    [ a]            [  b    ]
      [  a  ]    [   a   ]
    -------------------------
    [ a )[ab](b] [a)[ab  ](b]

    >>> union(
    ...   Interval.closed(0, 3, 'a'),
    ...   Interval.closed(2, 8, 'a'),
    ...   Interval.closed(5, 11, 'b'),
    ...   Interval.closed(13, 21, 'a'),
    ...   Interval.closed(16, 19, 'a'),
    ...   Interval.closed(16, 24, 'b'),
    ... )
    [<Interval [0, 5): a>,
     <Interval [5, 8]: a, b>,
     <Interval (8, 11]: b>,
     <Interval [13, 16): a>,
     <Interval [16, 21]: a, b>,
     <Interval (21, 24]: b>]

    >>> union(
    ...   Interval.closed(0, 3, 'a'),
    ...   Interval.closed(2, 8, 'a'),
    ...   Interval.closed(5, 11, 'b'),
    ...   Interval.closed(13, 21, 'a'),
    ...   Interval.closed(16, 19, 'a'),
    ...   Interval.closed(16, 24, 'b'),
    ...   ignore_data=True,
    ... )
    [<Interval [0, 11]>, <Interval [13, 24]>]
    """

    if not intervals:
        return []

    ignore_data = kwargs.pop('ignore_data', False)

    bounds = _list_bounds(intervals)

    union = []

    lower_bound = None
    level = 0
    data_stack = []
    data_set = set()

    def add_interval(lower, upper):
        if lower >= upper:
            return

        last_interval = union[-1] if union else None

        if (
            last_interval
            and last_interval.upper.is_opposite_of(lower)
            and last_interval.data == data_set
        ):
            last_interval._upper = upper
            return

        union.append(Interval(lower, upper, data_set=data_set))

    for bound, interval in bounds:
        if bound.is_lower:
            level += 1

            if not lower_bound:
                lower_bound = bound

            if not ignore_data:
                data_stack.extend(interval.data)
                new_items = interval.data - data_set

                if new_items:
                    add_interval(lower_bound, ~bound)
                    lower_bound = bound
                    data_set.update(new_items)
        else:
            level -= 1

            if not level:
                add_interval(lower_bound, bound)
                lower_bound = None
                data_stack = []
                data_set.clear()
                continue

            if not ignore_data and interval.data:
                for item in interval.data:
                    data_stack.remove(item)

                new_data_set = set(data_stack)
                if new_data_set != data_set:
                    add_interval(lower_bound, bound)
                    lower_bound = ~bound
                    data_set = new_data_set

    return union


def intersection(*intervals, **kwargs):
    """
    Returns the intersection of all the intervals.

    >>> intersection()
    []

    No data:
    >>> intersection(Interval.closed(0, 2), Interval.closed(4, 10))
    []
    >>> intersection(Interval.closed(3, 5), Interval.closed(4, 10))
    [<Interval [4, 5]>]
    >>> intersection(Interval.closed(6, 8), Interval.closed(4, 10))
    [<Interval [6, 8]>]
    >>> intersection(Interval.closed(9, 11), Interval.closed(4, 10))
    [<Interval [9, 10]>]
    >>> intersection(Interval.closed(12, 14), Interval.closed(4, 10))
    []

    >>> intersection(Interval.closed(0, 2), Interval.closed(0, 5))
    [<Interval [0, 2]>]
    >>> intersection(Interval.closed(3, 5), Interval.closed(0, 5))
    [<Interval [3, 5]>]

    >>> intersection(Interval.closed(0, 2), Interval.closed(0, 2))
    [<Interval [0, 2]>]

    Ininities
    >>> intersection(
    ...   Interval.closed(0, 2),
    ...   Interval(Bound.gt_ninf(), Bound.lt_inf()),
    ... )
    [<Interval [0, 2]>]

    >>> intersection(
    ...   Interval.closed(0, 2),
    ...   Interval(Bound.gt_ninf(), Bound.lt(0)),
    ... )
    []

    >>> intersection(
    ...   Interval.closed(0, 2),
    ...   Interval(Bound.gt(2), Bound.lt_inf()),
    ... )
    []

    >>> intersection(
    ...   Interval.closed(0, 2),
    ...   Interval(Bound.ge(1), Bound.lt_inf()),
    ... )
    [<Interval [1, 2]>]

    >>> intersection(
    ...   Interval.closed(0, 2),
    ...   Interval(Bound.gt_ninf(), Bound.le(1)),
    ... )
    [<Interval [0, 1]>]

    With data:
    >>> intersection(Interval.closed(0, 2, 'data'), Interval.closed(4, 10))
    []
    >>> intersection(Interval.closed(3, 5, 'data'), Interval.closed(4, 10))
    [<Interval [4, 5]: data>]
    >>> intersection(Interval.closed(6, 8, 'data'), Interval.closed(4, 10))
    [<Interval [6, 8]: data>]
    >>> intersection(Interval.closed(9, 11, 'data'), Interval.closed(4, 10))
    [<Interval [9, 10]: data>]
    >>> intersection(Interval.closed(12, 14, 'data'), Interval.closed(4, 10))
    []

    >>> intersection(Interval.closed(0, 2, 'data'), Interval.closed(0, 5))
    [<Interval [0, 2]: data>]
    >>> intersection(Interval.closed(3, 5, 'data'), Interval.closed(0, 5))
    [<Interval [3, 5]: data>]

    >>> intersection(Interval.closed(0, 2, 'data'), Interval.closed(0, 2))
    [<Interval [0, 2]: data>]

    >>> intersection(Interval.closed(0, 2, 'data'), Interval.closed(0, 2),
    ...              ignore_data=True)
    [<Interval [0, 2]>]
    """

    if not intervals:
        return []

    ignore_data = kwargs.pop('ignore_data', False)

    if ignore_data:
        data_union = set()
    else:
        data_union = intervals[0].data.union(*(
            interval.data for interval in intervals[1:]
        ))

    bounds = _list_bounds(intervals)

    intersection = []

    lower_bound = None
    level = 0

    for bound, interval in bounds:
        if bound.is_lower:
            level += 1

            if level == len(intervals):
                lower_bound = bound
        else:
            if level == len(intervals):
                intersection.append(
                    Interval(lower_bound, bound, data_set=data_union)
                )

            level -= 1

    return intersection


def set_intersection(*interval_sets, **kwargs):
    """
    Returns the intersection of the given interval sets.

    >>> set_intersection()
    []

    01234567890123456789
    [  ] [  ]     [   ]
        [   ]  [    ]
      [              ]
    -------------------
         [  ]     [ ]

    >>> set_intersection(
    ... [Interval.closed(0, 3), Interval.closed(5, 8),
    ...  Interval.closed(14, 18)],
    ... [Interval.closed(4, 8), Interval.closed(11, 16)],
    ... [Interval.closed(2, 17)]
    ... )
    [<Interval [5, 8]>, <Interval [14, 16]>]

    01234567890123456789
    [  ] [  ]     [   ]
        [ a ]  [ b  ]
      [              ]
    -------------------
         [a ]     [b]

    >>> set_intersection(
    ... [Interval.closed(0, 3), Interval.closed(5, 8),
    ...  Interval.closed(14, 18)],
    ... [Interval.closed(4, 8, 'a'), Interval.closed(11, 16, 'b')],
    ... [Interval.closed(2, 17)]
    ... )
    [<Interval [5, 8]: a>, <Interval [14, 16]: b>]

    >>> set_intersection(
    ... [Interval.closed(0, 3), Interval.closed(5, 8),
    ...  Interval.closed(14, 18)],
    ... [Interval.closed(4, 8, 'a'), Interval.closed(11, 16, 'b')],
    ... [Interval.closed(2, 17)],
    ... ignore_data=True,
    ... )
    [<Interval [5, 8]>, <Interval [14, 16]>]

    """

    if not interval_sets:
        return []

    ignore_data = kwargs.get('ignore_data', False)

    all_bounds = _list_bounds(itertools.chain(*interval_sets))

    intersection = []

    lower_bound = None
    data_stack = []
    level = 0

    for bound, interval in all_bounds:
        if bound.is_lower:
            level += 1

            if not ignore_data:
                data_stack.extend(interval.data)

            if level == len(interval_sets):
                lower_bound = bound
        else:
            if level == len(interval_sets):
                intersection.append(
                    Interval(lower_bound, bound, data_set=set(data_stack))
                )

            if not ignore_data:
                for item in interval.data:
                    data_stack.remove(item)

            level -= 1

    return intersection


def invert(*intervals):
    """
    Returns the complement of the given intervals (with no data).

    >>> invert()
    [<Interval (-inf, inf)>]

    >>> invert(*invert()) == []
    True

    >>> invert(Interval.closed(0, 1))
    [<Interval (-inf, 0)>, <Interval (1, inf)>]

    >>> invert(*invert(Interval.closed(0, 1)))
    [<Interval [0, 1]>]

    >>> invert(Interval.open(0, 2), Interval.closed(1, 3))
    [<Interval (-inf, 0]>, <Interval (3, inf)>]

    >>> invert(*invert(Interval.open(0, 2), Interval.closed(1, 3)))
    [<Interval (0, 3]>]

    >>> invert(Interval.open(0, 1), Interval.closed(2, 3))
    [<Interval (-inf, 0]>, <Interval [1, 2)>, <Interval (3, inf)>]

    >>> invert(*invert(Interval.open(0, 1), Interval.closed(2, 3)))
    [<Interval (0, 1)>, <Interval [2, 3]>]
    """

    if not intervals:
        return [Interval.open(NEGATIVE_INFINITY, INFINITY)]

    intervals = union(*intervals, ignore_data=True)
    bounds = _list_bounds(intervals)
    lower_bound = Bound.gt(NEGATIVE_INFINITY)
    inverted = []

    def add_interval(lower, upper):
        if lower < upper:
            inverted.append(Interval(lower, upper))

    for bound, interval in bounds:
        if bound.is_lower:
            add_interval(lower_bound, ~bound)
        else:
            lower_bound = ~bound

    add_interval(lower_bound, Bound.lt(INFINITY))

    return inverted


def difference(base_intervals, subtracting_intervals):
    mask = invert(*subtracting_intervals)
    return set_intersection(base_intervals, mask)


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

    def _create_set(self, intervals=()):
        from .interval_set import IntervalSet
        return IntervalSet(intervals, check_overlaps=False)

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
                u', '.join(unicode(item) for item in sorted(self.data))
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

        >>> Interval.open(1, 2) == Interval.open(2, 3)
        False

        >>> Interval.open(1, 2) == Interval.open(1, 2)
        True

        >>> Interval.open(1, 2, 'data') == Interval.open(1, 2)
        True

        >>> Interval.open(1, 2) == Interval.open(1, 3)
        False
        """

        return (
            cmp(self.lower, other.lower)
            or cmp(self.upper, other.upper)
        )

    def __hash__(self):
        """
        >>> sorted(set([
        ...   Interval.open(0, 1),
        ...   Interval.closed(0, 1),
        ...   Interval.open(0, 2),
        ...   Interval.closed(1, 3),
        ...   Interval.open(0, 1),
        ...   Interval.open(0, 1, 'data'),
        ...   Interval.closed(0, 1),
        ... ]))
        [<Interval [0, 1]>,
         <Interval (0, 1)>,
         <Interval (0, 2)>,
         <Interval [1, 3]>]
        """

        return hash((self.lower, self.upper))

    def __and__(self, other):
        if not other:
            return self._create_set()

        if not isinstance(other, Interval):
            return other & self

        result = self.intersect(other)
        return self._create_set((result, ) if result else ())

    def __or__(self, other):
        if not other:
            return self._create_set((self,))

        if not isinstance(other, Interval):
            return other | self

        return self.union(other)

    def __add__(self, other):
        return self | other

    def __sub__(self, other):
        if not other:
            return self._create_set((self,))

        if not isinstance(other, Interval):
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
        <IntervalSet >
        >>> Interval.closed(1, 3) & Interval.closed(0, 1, 'data')
        <IntervalSet [1, 1]: data>

        >>> Interval.open(1, 3) & Interval.open(1, 2, 'data')
        <IntervalSet (1, 2): data>

        >>> Interval.open(1, 3) & Interval.closed(2, 2, 'data')
        <IntervalSet [2, 2]: data>

        >>> Interval.open(1, 3) & Interval.open(2, 3, 'data')
        <IntervalSet (2, 3): data>

        >>> Interval.closed(1, 3) & Interval.closed(3, 4, 'data')
        <IntervalSet [3, 3]: data>
        >>> Interval.open(1, 3) & Interval.closed(3, 4, 'data')
        <IntervalSet >
        """

        if not other:
            return None

        result = intersection(self, other)
        return result[0] if result else None

    def union(self, other):
        """
        Returns a list of Intervals representing the union of
        this :class:`~pyinter.Interval`
        with the other :class:`~pyinter.Interval`.

        >>> Interval.open(1, 3) | Interval.closed(0, 1)
        <IntervalSet [0, 3)>
        >>> Interval.closed(1, 3) | Interval.closed(0, 1, 'data')
        <IntervalSet [0, 1]: data, (1, 3]>

        >>> Interval.open(1, 3, 'some') | Interval.open(1, 2, 'more')
        <IntervalSet (1, 2): more, some, [2, 3): some>

        >>> Interval.open(1, 2) | Interval.open(3, 4)
        <IntervalSet (1, 2), (3, 4)>

        >>> Interval.closed(4, 5) | Interval.open(1, 10, 'some')
        <IntervalSet (1, 10): some>

        >>> Interval.open(1, 5) | Interval.open(2, 3, 'data')
        <IntervalSet (1, 2], (2, 3): data, [3, 5)>
        """

        result = union(self, other) if other else [self]
        return self._create_set(result)

    def difference(self, other):
        """
        Returns a list of Intervals representing the difference
        between this :class:`~pyinter.Interval`
        and the other :class:`~pyinter.Interval`.

        >>> Interval.open(1, 4) - Interval.open(1, 2)
        <IntervalSet [2, 4)>
        >>> Interval.closed(1, 4) - Interval.open(1, 2)
        <IntervalSet [1, 1], [2, 4]>
        >>> Interval.closed(1, 4) - Interval.open(2, 3)
        <IntervalSet [1, 2], [3, 4]>
        >>> Interval.open(1, 4) - Interval.open(3, 4)
        <IntervalSet (1, 3]>
        >>> Interval.open(1, 2) - Interval.open(1, 2)
        <IntervalSet >
        >>> Interval.closed(1, 2) - Interval.open(1, 2)
        <IntervalSet [1, 1], [2, 2]>
        >>> Interval.open(1, 2) - Interval.open(0, 3)
        <IntervalSet >
        """

        if other is None or not self.overlaps(other):
            result = [self]
        else:
            result = difference((self,), (other,))

        return self._create_set(result)

    def complement(self):
        return self._create_set(invert((self,)))

    def copy(self, other):
        return self.__class__(
            Bound(self.lower.value, self.lower.operator),
            Bound(self.upper.value, self.upper.operator),
            data_set=self.data,
        )
