import unittest2
import doctest

from pyinter import bound, interval, interval_set, extrema


def load_tests(loader, tests, ignore):
    flags = (
        doctest.NORMALIZE_WHITESPACE
        | doctest.ELLIPSIS
        | doctest.IGNORE_EXCEPTION_DETAIL
    )

    tests.addTests(doctest.DocTestSuite(extrema, optionflags=flags))
    tests.addTests(doctest.DocTestSuite(bound, optionflags=flags))
    tests.addTests(doctest.DocTestSuite(interval, optionflags=flags))
    tests.addTests(doctest.DocTestSuite(interval_set, optionflags=flags))
    return tests
