from typing import TYPE_CHECKING, List

from twisted.trial.unittest import SynchronousTestCase
from .reactormixins import ReactorBuilder

if TYPE_CHECKING:
    fakeBase = SynchronousTestCase
else:
    fakeBase = object


def noop() -> None:
    """
    Do-nothing callable. Stub for testing.
    """


noop()  # Exercise for coverage, since it will never be called below.


class CoreFoundationSpecificTests(ReactorBuilder, fakeBase):
    """
    Tests for platform interactions of the CoreFoundation-based reactor.
    """

    _reactors = ["twisted.internet.cfreactor.CFReactor"]

    def test_whiteboxStopSimulating(self) -> None:
        """
        CFReactor's simulation timer is None after CFReactor crashes.
        """
        r = self.buildReactor()
        r.callLater(0, r.crash)
        r.callLater(100, noop)
        self.runReactor(r)
        self.assertIs(r._currentSimulator, None)

    def test_callLaterLeakage(self) -> None:
        """
        callLater should not leak global state into CoreFoundation which will
        be invoked by a different reactor running the main loop.

        @note: this test may actually be usable for other reactors as well, so
            we may wish to promote it to ensure this invariant across other
            foreign-main-loop reactors.
        """
        r = self.buildReactor()
        delayed = r.callLater(0, noop)
        r2 = self.buildReactor()

        def stopBlocking() -> None:
            r2.callLater(0, r2stop)

        def r2stop() -> None:
            r2.stop()

        r2.callLater(0, stopBlocking)
        self.runReactor(r2)
        self.assertEqual(r.getDelayedCalls(), [delayed])

    def test_whiteboxIterate(self) -> None:
        """
        C{.iterate()} should remove the CFTimer that will run Twisted's
        callLaters from the loop, even if one is still pending.  We test this
        state indirectly with a white-box assertion by verifying the
        C{_currentSimulator} is set to C{None}, since CoreFoundation does not
        allow us to enumerate all active timers or sources.
        """
        r = self.buildReactor()
        x: List[int] = []
        r.callLater(0, x.append, 1)
        delayed = r.callLater(100, noop)
        r.iterate()
        self.assertIs(r._currentSimulator, None)
        self.assertEqual(r.getDelayedCalls(), [delayed])
        self.assertEqual(x, [1])

    def test_noTimers(self) -> None:
        """
        The loop can wake up just fine even if there are no timers in it.
        """
        r = self.buildReactor()
        stopped = []

        def doStop() -> None:
            r.stop()
            stopped.append("yes")

        def sleepThenStop() -> None:
            r.callFromThread(doStop)

        r.callLater(0, r.callInThread, sleepThenStop)
        # Can't use runReactor here because it does a callLater.  This is
        # therefore a somewhat risky test: inherently, this is the "no timed
        # events anywhere in the reactor" test case and so we can't have a
        # timeout for it.
        r.run()
        self.assertEqual(stopped, ["yes"])


globals().update(CoreFoundationSpecificTests.makeTestCaseClasses())
