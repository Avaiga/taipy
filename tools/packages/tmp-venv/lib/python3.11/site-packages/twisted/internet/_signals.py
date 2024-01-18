# -*- test-case-name: twisted.internet.test.test_sigchld -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module is used to integrate child process termination into a
reactor event loop.  This is a challenging feature to provide because
most platforms indicate process termination via SIGCHLD and do not
provide a way to wait for that signal and arbitrary I/O events at the
same time.  The naive implementation involves installing a Python
SIGCHLD handler; unfortunately this leads to other syscalls being
interrupted (whenever SIGCHLD is received) and failing with EINTR
(which almost no one is prepared to handle).  This interruption can be
disabled via siginterrupt(2) (or one of the equivalent mechanisms);
however, if the SIGCHLD is delivered by the platform to a non-main
thread (not a common occurrence, but difficult to prove impossible),
the main thread (waiting on select() or another event notification
API) may not wake up leading to an arbitrary delay before the child
termination is noticed.

The basic solution to all these issues involves enabling SA_RESTART (ie,
disabling system call interruption) and registering a C signal handler which
writes a byte to a pipe.  The other end of the pipe is registered with the
event loop, allowing it to wake up shortly after SIGCHLD is received.  See
L{_SIGCHLDWaker} for the implementation of the event loop side of this
solution.  The use of a pipe this way is known as the U{self-pipe
trick<http://cr.yp.to/docs/selfpipe.html>}.

From Python version 2.6, C{signal.siginterrupt} and C{signal.set_wakeup_fd}
provide the necessary C signal handler which writes to the pipe to be
registered with C{SA_RESTART}.
"""

from __future__ import annotations

import contextlib
import errno
import os
import signal
import socket
from types import FrameType
from typing import Callable, Optional, Sequence

from zope.interface import Attribute, Interface, implementer

from attrs import define, frozen
from typing_extensions import Protocol, TypeAlias

from twisted.internet.interfaces import IReadDescriptor
from twisted.python import failure, log, util
from twisted.python.runtime import platformType

if platformType == "posix":
    from . import fdesc, process

SignalHandler: TypeAlias = Callable[[int, Optional[FrameType]], None]


def installHandler(fd: int) -> int:
    """
    Install a signal handler which will write a byte to C{fd} when
    I{SIGCHLD} is received.

    This is implemented by installing a SIGCHLD handler that does nothing,
    setting the I{SIGCHLD} handler as not allowed to interrupt system calls,
    and using L{signal.set_wakeup_fd} to do the actual writing.

    @param fd: The file descriptor to which to write when I{SIGCHLD} is
        received.

    @return: The file descriptor previously configured for this use.
    """
    if fd == -1:
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    else:

        def noopSignalHandler(*args):
            pass

        signal.signal(signal.SIGCHLD, noopSignalHandler)
        signal.siginterrupt(signal.SIGCHLD, False)
    return signal.set_wakeup_fd(fd)


def isDefaultHandler():
    """
    Determine whether the I{SIGCHLD} handler is the default or not.
    """
    return signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL


class SignalHandling(Protocol):
    """
    The L{SignalHandling} protocol enables customizable signal-handling
    behaviors for reactors.

    A value that conforms to L{SignalHandling} has install and uninstall hooks
    that are called by a reactor at the correct times to have the (typically)
    process-global effects necessary for dealing with signals.
    """

    def install(self) -> None:
        """
        Install the signal handlers.
        """

    def uninstall(self) -> None:
        """
        Restore signal handlers to their original state.
        """


@frozen
class _WithoutSignalHandling:
    """
    A L{SignalHandling} implementation that does no signal handling.

    This is the implementation of C{installSignalHandlers=False}.
    """

    def install(self) -> None:
        """
        Do not install any signal handlers.
        """

    def uninstall(self) -> None:
        """
        Do nothing because L{install} installed nothing.
        """


@frozen
class _WithSignalHandling:
    """
    A reactor core helper that can manage signals: it installs signal handlers
    at start time.
    """

    _sigInt: SignalHandler
    _sigBreak: SignalHandler
    _sigTerm: SignalHandler

    def install(self) -> None:
        """
        Install the signal handlers for the Twisted event loop.
        """
        if signal.getsignal(signal.SIGINT) == signal.default_int_handler:
            # only handle if there isn't already a handler, e.g. for Pdb.
            signal.signal(signal.SIGINT, self._sigInt)
        signal.signal(signal.SIGTERM, self._sigTerm)

        # Catch Ctrl-Break in windows
        SIGBREAK = getattr(signal, "SIGBREAK", None)
        if SIGBREAK is not None:
            signal.signal(SIGBREAK, self._sigBreak)

    def uninstall(self) -> None:
        """
        At the moment, do nothing (for historical reasons).
        """
        # This should really do something.
        # https://github.com/twisted/twisted/issues/11761


@define
class _MultiSignalHandling:
    """
    An implementation of L{SignalHandling} which propagates protocol
    method calls to a number of other implementations.

    This supports composition of multiple signal handling implementations into
    a single object so the reactor doesn't have to be concerned with how those
    implementations are factored.

    @ivar _signalHandlings: The other C{SignalHandling} implementations to
        which to propagate calls.

    @ivar _installed: If L{install} has been called but L{uninstall} has not.
        This is used to avoid double cleanup which otherwise results (at least
        during test suite runs) because twisted.internet.reactormixins doesn't
        keep track of whether a reactor has run or not but always invokes its
        cleanup logic.
    """

    _signalHandlings: Sequence[SignalHandling]
    _installed: bool = False

    def install(self) -> None:
        for d in self._signalHandlings:
            d.install()
        self._installed = True

    def uninstall(self) -> None:
        if self._installed:
            for d in self._signalHandlings:
                d.uninstall()
            self._installed = False


@define
class _ChildSignalHandling:
    """
    Signal handling behavior which supports I{SIGCHLD} for notification about
    changes to child process state.

    @ivar _childWaker: L{None} or a reference to the L{_SIGCHLDWaker} which is
        used to properly notice child process termination.  This is L{None}
        when this handling behavior is not installed and non-C{None}
        otherwise.  This is mostly an unfortunate implementation detail due to
        L{_SIGCHLDWaker} allocating file descriptors as a side-effect of its
        initializer.
    """

    _addInternalReader: Callable[[IReadDescriptor], object]
    _removeInternalReader: Callable[[IReadDescriptor], object]
    _childWaker: Optional[_SIGCHLDWaker] = None

    def install(self) -> None:
        """
        Extend the basic signal handling logic to also support handling
        SIGCHLD to know when to try to reap child processes.
        """
        # This conditional should probably not be necessary.
        # https://github.com/twisted/twisted/issues/11763
        if self._childWaker is None:
            self._childWaker = _SIGCHLDWaker()
            self._addInternalReader(self._childWaker)
        self._childWaker.install()

        # Also reap all processes right now, in case we missed any
        # signals before we installed the SIGCHLD waker/handler.
        # This should only happen if someone used spawnProcess
        # before calling reactor.run (and the process also exited
        # already).
        process.reapAllProcesses()

    def uninstall(self) -> None:
        """
        If a child waker was created and installed, uninstall it now.

        Since this disables reactor functionality and is only called when the
        reactor is stopping, it doesn't provide any directly useful
        functionality, but the cleanup of reactor-related process-global state
        that it does helps in unit tests involving multiple reactors and is
        generally just a nice thing.
        """
        assert self._childWaker is not None

        # XXX This would probably be an alright place to put all of the
        # cleanup code for all internal readers (here and in the base class,
        # anyway).  See #3063 for that cleanup task.
        self._removeInternalReader(self._childWaker)
        self._childWaker.uninstall()
        self._childWaker.connectionLost(failure.Failure(Exception("uninstalled")))

        # We just spoiled the current _childWaker so throw it away.  We can
        # make a new one later if need be.
        self._childWaker = None


class _IWaker(Interface):
    """
    Interface to wake up the event loop based on the self-pipe trick.

    The U{I{self-pipe trick}<http://cr.yp.to/docs/selfpipe.html>}, used to wake
    up the main loop from another thread or a signal handler.
    This is why we have wakeUp together with doRead

    This is used by threads or signals to wake up the event loop.
    """

    disconnected = Attribute("")

    def wakeUp():
        """
        Called when the event should be wake up.
        """

    def doRead():
        """
        Read some data from my connection and discard it.
        """

    def connectionLost(reason: failure.Failure) -> None:
        """
        Called when connection was closed and the pipes.
        """


@implementer(_IWaker)
class _SocketWaker(log.Logger):
    """
    The I{self-pipe trick<http://cr.yp.to/docs/selfpipe.html>}, implemented
    using a pair of sockets rather than pipes (due to the lack of support in
    select() on Windows for pipes), used to wake up the main loop from
    another thread.
    """

    disconnected = 0

    def __init__(self) -> None:
        """Initialize."""
        # Following select_trigger (from asyncore)'s example;
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        with contextlib.closing(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ) as server:
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            client.connect(server.getsockname())
            reader, clientaddr = server.accept()
        client.setblocking(False)
        reader.setblocking(False)
        self.r = reader
        self.w = client
        self.fileno = self.r.fileno

    def wakeUp(self):
        """Send a byte to my connection."""
        try:
            util.untilConcludes(self.w.send, b"x")
        except OSError as e:
            if e.args[0] != errno.WSAEWOULDBLOCK:
                raise

    def doRead(self):
        """
        Read some data from my connection.
        """
        try:
            self.r.recv(8192)
        except OSError:
            pass

    def connectionLost(self, reason):
        self.r.close()
        self.w.close()


@implementer(IReadDescriptor)
class _FDWaker(log.Logger):
    """
    The I{self-pipe trick<http://cr.yp.to/docs/selfpipe.html>}, used to wake
    up the main loop from another thread or a signal handler.

    L{_FDWaker} is a base class for waker implementations based on
    writing to a pipe being monitored by the reactor.

    @ivar o: The file descriptor for the end of the pipe which can be
        written to wake up a reactor monitoring this waker.

    @ivar i: The file descriptor which should be monitored in order to
        be awoken by this waker.
    """

    disconnected = 0

    i: int
    o: int

    def __init__(self) -> None:
        """Initialize."""
        self.i, self.o = os.pipe()
        fdesc.setNonBlocking(self.i)
        fdesc._setCloseOnExec(self.i)
        fdesc.setNonBlocking(self.o)
        fdesc._setCloseOnExec(self.o)
        self.fileno = lambda: self.i

    def doRead(self) -> None:
        """
        Read some bytes from the pipe and discard them.
        """
        fdesc.readFromFD(self.fileno(), lambda data: None)

    def connectionLost(self, reason):
        """Close both ends of my pipe."""
        if not hasattr(self, "o"):
            return
        for fd in self.i, self.o:
            try:
                os.close(fd)
            except OSError:
                pass
        del self.i, self.o


@implementer(_IWaker)
class _UnixWaker(_FDWaker):
    """
    This class provides a simple interface to wake up the event loop.

    This is used by threads or signals to wake up the event loop.
    """

    def wakeUp(self):
        """Write one byte to the pipe, and flush it."""
        # We don't use fdesc.writeToFD since we need to distinguish
        # between EINTR (try again) and EAGAIN (do nothing).
        if self.o is not None:
            try:
                util.untilConcludes(os.write, self.o, b"x")
            except OSError as e:
                # XXX There is no unit test for raising the exception
                # for other errnos. See #4285.
                if e.errno != errno.EAGAIN:
                    raise


if platformType == "posix":
    _Waker = _UnixWaker
else:
    # Primarily Windows and Jython.
    _Waker = _SocketWaker  # type: ignore[misc,assignment]


class _SIGCHLDWaker(_FDWaker):
    """
    L{_SIGCHLDWaker} can wake up a reactor whenever C{SIGCHLD} is received.
    """

    def install(self) -> None:
        """
        Install the handler necessary to make this waker active.
        """
        installHandler(self.o)

    def uninstall(self) -> None:
        """
        Remove the handler which makes this waker active.
        """
        installHandler(-1)

    def doRead(self) -> None:
        """
        Having woken up the reactor in response to receipt of
        C{SIGCHLD}, reap the process which exited.

        This is called whenever the reactor notices the waker pipe is
        writeable, which happens soon after any call to the C{wakeUp}
        method.
        """
        super().doRead()
        process.reapAllProcesses()
