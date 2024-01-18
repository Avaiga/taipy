# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for convenience functionality in L{twisted._threads._convenience}.
"""


from twisted.trial.unittest import SynchronousTestCase
from .._convenience import Quit
from .._ithreads import AlreadyQuit


class QuitTests(SynchronousTestCase):
    """
    Tests for L{Quit}
    """

    def test_isInitiallySet(self) -> None:
        """
        L{Quit.isSet} starts as L{False}.
        """
        quit = Quit()
        self.assertEqual(quit.isSet, False)

    def test_setSetsSet(self) -> None:
        """
        L{Quit.set} sets L{Quit.isSet} to L{True}.
        """
        quit = Quit()
        quit.set()
        self.assertEqual(quit.isSet, True)

    def test_checkDoesNothing(self) -> None:
        """
        L{Quit.check} initially does nothing and returns L{None}.
        """
        quit = Quit()
        self.assertIs(quit.check(), None)

    def test_checkAfterSetRaises(self) -> None:
        """
        L{Quit.check} raises L{AlreadyQuit} if L{Quit.set} has been called.
        """
        quit = Quit()
        quit.set()
        self.assertRaises(AlreadyQuit, quit.check)

    def test_setTwiceRaises(self) -> None:
        """
        L{Quit.set} raises L{AlreadyQuit} if it has been called previously.
        """
        quit = Quit()
        quit.set()
        self.assertRaises(AlreadyQuit, quit.set)
