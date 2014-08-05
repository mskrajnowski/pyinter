import unittest2
import doctest
from pyinter import bound


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(bound))
    return tests
