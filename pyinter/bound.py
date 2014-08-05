import operator


class Bound(object):
    """
    Represents a single interval (lower or upper) bound.

    Bounds are defined by a value and an operator which will, be used
    to check whether values are inside a bound.

    >>> greater_than_15 = Bound(15, operator.gt)
    >>> [value in greater_than_15 for value in (14, 15, 16)]
    [False, False, True]

    >>> [value in Bound(15, operator.le) for value in (14, 15, 16)]
    [True, True, False]
    """

    OPPOSITE_OPERATORS = {
        operator.lt: operator.ge,
        operator.le: operator.gt,
        operator.ge: operator.lt,
        operator.gt: operator.le,
    }

    # logical order of operators
    # ...)[value](...
    OPERATOR_ORDER = {
        operator.lt: -2,  # )
        operator.ge: -1,  # [
        operator.le: +1,  # ]
        operator.gt: +2,  # (
    }

    PREFIXES_SUFFIXES = {
        operator.lt: ('', ')'),
        operator.le: ('', ']'),
        operator.ge: ('[', ''),
        operator.gt: ('(', ''),
    }

    _value = None
    _operator = None

    @classmethod
    def lt(cls, value):
        """Shortcut method for Bound(value, operator.lt)"""
        return cls(value, operator.lt)

    @classmethod
    def le(cls, value):
        """Shortcut method for Bound(value, operator.le)"""
        return cls(value, operator.le)

    @classmethod
    def ge(cls, value):
        """Shortcut method for Bound(value, operator.ge)"""
        return cls(value, operator.ge)

    @classmethod
    def gt(cls, value):
        """Shortcut method for Bound(value, operator.gt)"""
        return cls(value, operator.gt)

    def __init__(self, value, operator):
        self._value = value
        self._operator = operator
        self._order = self.OPERATOR_ORDER[operator]

    @property
    def value(self):
        return self._value

    @property
    def operator(self):
        return self._operator

    def is_opposite_of(self, other):
        return (
            self.value == other.value
            and other.operator == self.OPPOSITE_OPERATORS[self.operator]
        )

    def __contains__(self, value):
        """
        Checks whether a value is inside the Bound.

        >>> [value in Bound.lt(2) for value in (1, 2, 3)]
        [True, False, False]

        >>> [value in Bound.le(2) for value in (1, 2, 3)]
        [True, True, False]

        >>> [value in Bound.ge(2) for value in (1, 2, 3)]
        [False, True, True]

        >>> [value in Bound.gt(2) for value in (1, 2, 3)]
        [False, False, True]
        """

        return self._operator(value, self._value)

    def __cmp__(self, other):
        """
        Compares bounds based on the logical order they would appear.
        If the value is the same, the ordering is as follows:
        lt < ge < le < gt -> ...)[value](...

        >>> Bound.gt(5) < Bound.lt(6)
        True
        >>> Bound.lt(6) < Bound.ge(6) < Bound.le(6) < Bound.gt(6)
        True
        >>> Bound.gt(6) < Bound.lt(7)
        True
        >>> [Bound(5, op) == Bound(5, op)
        ...  for op in (operator.lt, operator.gt, operator.le, operator.ge)]
        [True, True, True, True]
        """
        return cmp(self.value, other.value) or cmp(self._order, other._order)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str(self))

    def __unicode__(self):
        prefix, suffix = self.PREFIXES_SUFFIXES[self._operator]
        return u'{}{}{}'.format(prefix, self._value, suffix)

    def __hash__(self):
        return hash((self.value, self._order))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __invert__(self):
        """
        Returns the opposite bound with the same value.

        >>> Bound.lt(5) == ~Bound.ge(5)
        True

        >>> Bound.gt(5) == ~Bound.le(5)
        True
        """

        return self.__class__(
            self._value,
            self.OPPOSITE_OPERATORS[self._operator]
        )
