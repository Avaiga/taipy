# -*- test-case-name: twisted.trial.test.test_script -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for handling of trial's --order option.
"""

from twisted.trial import unittest


class FooTest(unittest.TestCase):
    """
    Used to make assertions about the order its tests will be run in.
    """

    def test_first(self) -> None:
        pass

    def test_second(self) -> None:
        pass

    def test_third(self) -> None:
        pass

    def test_fourth(self) -> None:
        pass


class BazTest(unittest.TestCase):
    """
    Used to make assertions about the order the test cases in this module are
    run in.
    """

    def test_baz(self) -> None:
        pass


class BarTest(unittest.TestCase):
    """
    Used to make assertions about the order the test cases in this module are
    run in.
    """

    def test_bar(self) -> None:
        pass
