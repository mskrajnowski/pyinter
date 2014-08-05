import unittest2
import doctest
from pyinter import interval


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(interval))
    return tests
