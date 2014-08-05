import unittest2
import doctest
from pyinter import interval_set


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(interval_set))
    return tests
