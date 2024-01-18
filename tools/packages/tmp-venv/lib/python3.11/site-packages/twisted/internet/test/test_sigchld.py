# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet._sigchld}, an alternate, superior SIGCHLD
monitoring API.
"""
from __future__ import annotations

import errno
import os
import signal

from twisted.python.runtime import platformType
from twisted.trial.unittest import SynchronousTestCase

if platformType == "posix":
    from twisted.internet._signals import installHandler, isDefaultHandler
    from twisted.internet.fdesc import setNonBlocking
else:
    skip = "These tests can only run on POSIX platforms."


class SetWakeupSIGCHLDTests(SynchronousTestCase):
    """
    Tests for the L{signal.set_wakeup_fd} implementation of the
    L{installHandler} and L{isDefaultHandler} APIs.
    """

    def pipe(self) -> tuple[int, int]:
        """
        Create a non-blocking pipe which will be closed after the currently
        running test.
        """
        read, write = os.pipe()
        self.addCleanup(os.close, read)
        self.addCleanup(os.close, write)
        setNonBlocking(read)
        setNonBlocking(write)
        return read, write

    def setUp(self) -> None:
        """
        Save the current SIGCHLD handler as reported by L{signal.signal} and
        the current file descriptor registered with L{installHandler}.
        """
        self.signalModuleHandler = signal.getsignal(signal.SIGCHLD)
        self.oldFD = installHandler(-1)

    def tearDown(self) -> None:
        """
        Restore whatever signal handler was present when setUp ran.
        """
        # If tests set up any kind of handlers, clear them out.
        installHandler(self.oldFD)
        signal.signal(signal.SIGCHLD, self.signalModuleHandler)

    def test_isDefaultHandler(self) -> None:
        """
        L{isDefaultHandler} returns true if the SIGCHLD handler is SIG_DFL,
        false otherwise.
        """
        self.assertTrue(isDefaultHandler())
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        self.assertFalse(isDefaultHandler())
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        self.assertTrue(isDefaultHandler())
        signal.signal(signal.SIGCHLD, lambda *args: None)
        self.assertFalse(isDefaultHandler())

    def test_returnOldFD(self) -> None:
        """
        L{installHandler} returns the previously registered file descriptor.
        """
        read, write = self.pipe()
        oldFD = installHandler(write)
        self.assertEqual(installHandler(oldFD), write)

    def test_uninstallHandler(self) -> None:
        """
        C{installHandler(-1)} removes the SIGCHLD handler completely.
        """
        read, write = self.pipe()
        self.assertTrue(isDefaultHandler())
        installHandler(write)
        self.assertFalse(isDefaultHandler())
        installHandler(-1)
        self.assertTrue(isDefaultHandler())

    def test_installHandler(self) -> None:
        """
        The file descriptor passed to L{installHandler} has a byte written to
        it when SIGCHLD is delivered to the process.
        """
        read, write = self.pipe()
        installHandler(write)

        exc = self.assertRaises(OSError, os.read, read, 1)
        self.assertEqual(exc.errno, errno.EAGAIN)

        os.kill(os.getpid(), signal.SIGCHLD)

        self.assertEqual(len(os.read(read, 5)), 1)
