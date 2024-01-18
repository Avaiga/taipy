# -*- test-case-name: twisted.internet.test -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module provides base support for Twisted to interact with the glib/gtk
mainloops.

The classes in this module should not be used directly, but rather you should
import gireactor or gtk3reactor for GObject Introspection based applications,
or glib2reactor or gtk2reactor for applications using legacy static bindings.
"""


import sys
from typing import Any, Callable, Dict, Set

from zope.interface import implementer

from twisted.internet import posixbase
from twisted.internet.abstract import FileDescriptor
from twisted.internet.interfaces import IReactorFDSet, IReadDescriptor, IWriteDescriptor
from twisted.python import log
from twisted.python.monkey import MonkeyPatcher
from ._signals import _UnixWaker


def ensureNotImported(moduleNames, errorMessage, preventImports=[]):
    """
    Check whether the given modules were imported, and if requested, ensure
    they will not be importable in the future.

    @param moduleNames: A list of module names we make sure aren't imported.
    @type moduleNames: C{list} of C{str}

    @param preventImports: A list of module name whose future imports should
        be prevented.
    @type preventImports: C{list} of C{str}

    @param errorMessage: Message to use when raising an C{ImportError}.
    @type errorMessage: C{str}

    @raise ImportError: with given error message if a given module name
        has already been imported.
    """
    for name in moduleNames:
        if sys.modules.get(name) is not None:
            raise ImportError(errorMessage)

    # Disable module imports to avoid potential problems.
    for name in preventImports:
        sys.modules[name] = None


class GlibWaker(_UnixWaker):
    """
    Run scheduled events after waking up.
    """

    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor

    def doRead(self) -> None:
        super().doRead()
        self.reactor._simulate()


def _signalGlue():
    """
    Integrate glib's wakeup file descriptor usage and our own.

    Python supports only one wakeup file descriptor at a time and both Twisted
    and glib want to use it.

    This is a context manager that can be wrapped around the whole glib
    reactor main loop which makes our signal handling work with glib's signal
    handling.
    """
    from gi import _ossighelper as signalGlue  # type: ignore[import]

    patcher = MonkeyPatcher()
    patcher.addPatch(signalGlue, "_wakeup_fd_is_active", True)
    return patcher


def _loopQuitter(
    idleAdd: Callable[[Callable[[], None]], None], loopQuit: Callable[[], None]
) -> Callable[[], None]:
    """
    Combine the C{glib.idle_add} and C{glib.MainLoop.quit} functions into a
    function suitable for crashing the reactor.
    """
    return lambda: idleAdd(loopQuit)


@implementer(IReactorFDSet)
class GlibReactorBase(posixbase.PosixReactorBase, posixbase._PollLikeMixin):
    """
    Base class for GObject event loop reactors.

    Notification for I/O events (reads and writes on file descriptors) is done
    by the gobject-based event loop. File descriptors are registered with
    gobject with the appropriate flags for read/write/disconnect notification.

    Time-based events, the results of C{callLater} and C{callFromThread}, are
    handled differently. Rather than registering each event with gobject, a
    single gobject timeout is registered for the earliest scheduled event, the
    output of C{reactor.timeout()}. For example, if there are timeouts in 1, 2
    and 3.4 seconds, a single timeout is registered for 1 second in the
    future. When this timeout is hit, C{_simulate} is called, which calls the
    appropriate Twisted-level handlers, and a new timeout is added to gobject
    by the C{_reschedule} method.

    To handle C{callFromThread} events, we use a custom waker that calls
    C{_simulate} whenever it wakes up.

    @ivar _sources: A dictionary mapping L{FileDescriptor} instances to
        GSource handles.

    @ivar _reads: A set of L{FileDescriptor} instances currently monitored for
        reading.

    @ivar _writes: A set of L{FileDescriptor} instances currently monitored for
        writing.

    @ivar _simtag: A GSource handle for the next L{simulate} call.
    """

    # Install a waker that knows it needs to call C{_simulate} in order to run
    # callbacks queued from a thread:
    def _wakerFactory(self) -> GlibWaker:
        return GlibWaker(self)

    def __init__(self, glib_module: Any, gtk_module: Any, useGtk: bool = False) -> None:
        self._simtag = None
        self._reads: Set[IReadDescriptor] = set()
        self._writes: Set[IWriteDescriptor] = set()
        self._sources: Dict[FileDescriptor, int] = {}
        self._glib = glib_module

        self._POLL_DISCONNECTED = (
            glib_module.IOCondition.HUP
            | glib_module.IOCondition.ERR
            | glib_module.IOCondition.NVAL
        )
        self._POLL_IN = glib_module.IOCondition.IN
        self._POLL_OUT = glib_module.IOCondition.OUT

        # glib's iochannel sources won't tell us about any events that we haven't
        # asked for, even if those events aren't sensible inputs to the poll()
        # call.
        self.INFLAGS = self._POLL_IN | self._POLL_DISCONNECTED
        self.OUTFLAGS = self._POLL_OUT | self._POLL_DISCONNECTED

        super().__init__()

        self._source_remove = self._glib.source_remove
        self._timeout_add = self._glib.timeout_add

        self.context = self._glib.main_context_default()
        self._pending = self.context.pending
        self._iteration = self.context.iteration
        self.loop = self._glib.MainLoop()
        self._crash = _loopQuitter(self._glib.idle_add, self.loop.quit)
        self._run = self.loop.run

    def _reallyStartRunning(self):
        """
        Make sure the reactor's signal handlers are installed despite any
        outside interference.
        """
        # First, install SIGINT and friends:
        super()._reallyStartRunning()

        # Next, since certain versions of gtk will clobber our signal handler,
        # set all signal handlers again after the event loop has started to
        # ensure they're *really* set.
        #
        # We don't actually know which versions of gtk do this so this might
        # be obsolete.  If so, that would be great and this whole method can
        # go away.  Someone needs to find out, though.
        #
        # https://github.com/twisted/twisted/issues/11762

        def reinitSignals():
            self._signals.uninstall()
            self._signals.install()

        self.callLater(0, reinitSignals)

    # The input_add function in pygtk1 checks for objects with a
    # 'fileno' method and, if present, uses the result of that method
    # as the input source. The pygtk2 input_add does not do this. The
    # function below replicates the pygtk1 functionality.

    # In addition, pygtk maps gtk.input_add to _gobject.io_add_watch, and
    # g_io_add_watch() takes different condition bitfields than
    # gtk_input_add(). We use g_io_add_watch() here in case pygtk fixes this
    # bug.
    def input_add(self, source, condition, callback):
        if hasattr(source, "fileno"):
            # handle python objects
            def wrapper(ignored, condition):
                return callback(source, condition)

            fileno = source.fileno()
        else:
            fileno = source
            wrapper = callback
        return self._glib.io_add_watch(
            fileno,
            self._glib.PRIORITY_DEFAULT_IDLE,
            condition,
            wrapper,
        )

    def _ioEventCallback(self, source, condition):
        """
        Called by event loop when an I/O event occurs.
        """
        log.callWithLogger(source, self._doReadOrWrite, source, source, condition)
        return True  # True = don't auto-remove the source

    def _add(self, source, primary, other, primaryFlag, otherFlag):
        """
        Add the given L{FileDescriptor} for monitoring either for reading or
        writing. If the file is already monitored for the other operation, we
        delete the previous registration and re-register it for both reading
        and writing.
        """
        if source in primary:
            return
        flags = primaryFlag
        if source in other:
            self._source_remove(self._sources[source])
            flags |= otherFlag
        self._sources[source] = self.input_add(source, flags, self._ioEventCallback)
        primary.add(source)

    def addReader(self, reader):
        """
        Add a L{FileDescriptor} for monitoring of data available to read.
        """
        self._add(reader, self._reads, self._writes, self.INFLAGS, self.OUTFLAGS)

    def addWriter(self, writer):
        """
        Add a L{FileDescriptor} for monitoring ability to write data.
        """
        self._add(writer, self._writes, self._reads, self.OUTFLAGS, self.INFLAGS)

    def getReaders(self):
        """
        Retrieve the list of current L{FileDescriptor} monitored for reading.
        """
        return list(self._reads)

    def getWriters(self):
        """
        Retrieve the list of current L{FileDescriptor} monitored for writing.
        """
        return list(self._writes)

    def removeAll(self):
        """
        Remove monitoring for all registered L{FileDescriptor}s.
        """
        return self._removeAll(self._reads, self._writes)

    def _remove(self, source, primary, other, flags):
        """
        Remove monitoring the given L{FileDescriptor} for either reading or
        writing. If it's still monitored for the other operation, we
        re-register the L{FileDescriptor} for only that operation.
        """
        if source not in primary:
            return
        self._source_remove(self._sources[source])
        primary.remove(source)
        if source in other:
            self._sources[source] = self.input_add(source, flags, self._ioEventCallback)
        else:
            self._sources.pop(source)

    def removeReader(self, reader):
        """
        Stop monitoring the given L{FileDescriptor} for reading.
        """
        self._remove(reader, self._reads, self._writes, self.OUTFLAGS)

    def removeWriter(self, writer):
        """
        Stop monitoring the given L{FileDescriptor} for writing.
        """
        self._remove(writer, self._writes, self._reads, self.INFLAGS)

    def iterate(self, delay=0):
        """
        One iteration of the event loop, for trial's use.

        This is not used for actual reactor runs.
        """
        self.runUntilCurrent()
        while self._pending():
            self._iteration(0)

    def crash(self):
        """
        Crash the reactor.
        """
        posixbase.PosixReactorBase.crash(self)
        self._crash()

    def stop(self):
        """
        Stop the reactor.
        """
        posixbase.PosixReactorBase.stop(self)
        # The base implementation only sets a flag, to ensure shutting down is
        # not reentrant. Unfortunately, this flag is not meaningful to the
        # gobject event loop. We therefore call wakeUp() to ensure the event
        # loop will call back into Twisted once this iteration is done. This
        # will result in self.runUntilCurrent() being called, where the stop
        # flag will trigger the actual shutdown process, eventually calling
        # crash() which will do the actual gobject event loop shutdown.
        self.wakeUp()

    def run(self, installSignalHandlers=True):
        """
        Run the reactor.
        """
        with _signalGlue():
            self.callWhenRunning(self._reschedule)
            self.startRunning(installSignalHandlers=installSignalHandlers)
            if self._started:
                self._run()

    def callLater(self, *args, **kwargs):
        """
        Schedule a C{DelayedCall}.
        """
        result = posixbase.PosixReactorBase.callLater(self, *args, **kwargs)
        # Make sure we'll get woken up at correct time to handle this new
        # scheduled call:
        self._reschedule()
        return result

    def _reschedule(self):
        """
        Schedule a glib timeout for C{_simulate}.
        """
        if self._simtag is not None:
            self._source_remove(self._simtag)
            self._simtag = None
        timeout = self.timeout()
        if timeout is not None:
            self._simtag = self._timeout_add(
                int(timeout * 1000),
                self._simulate,
                priority=self._glib.PRIORITY_DEFAULT_IDLE,
            )

    def _simulate(self):
        """
        Run timers, and then reschedule glib timeout for next scheduled event.
        """
        self.runUntilCurrent()
        self._reschedule()
