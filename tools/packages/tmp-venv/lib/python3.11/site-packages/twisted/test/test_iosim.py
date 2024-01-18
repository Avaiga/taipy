# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.test.iosim}.
"""
from __future__ import annotations

from typing import Literal

from zope.interface import implementer

from twisted.internet.interfaces import IPushProducer
from twisted.internet.protocol import Protocol
from twisted.internet.task import Clock
from twisted.test.iosim import FakeTransport, connect, connectedServerAndClient
from twisted.trial.unittest import TestCase


class FakeTransportTests(TestCase):
    """
    Tests for L{FakeTransport}.
    """

    def test_connectionSerial(self) -> None:
        """
        Each L{FakeTransport} receives a serial number that uniquely identifies
        it.
        """
        a = FakeTransport(object(), True)
        b = FakeTransport(object(), False)
        self.assertIsInstance(a.serial, int)
        self.assertIsInstance(b.serial, int)
        self.assertNotEqual(a.serial, b.serial)

    def test_writeSequence(self) -> None:
        """
        L{FakeTransport.writeSequence} will write a sequence of L{bytes} to the
        transport.
        """
        a = FakeTransport(object(), False)

        a.write(b"a")
        a.writeSequence([b"b", b"c", b"d"])

        self.assertEqual(b"".join(a.stream), b"abcd")

    def test_writeAfterClose(self) -> None:
        """
        L{FakeTransport.write} will accept writes after transport was closed,
        but the data will be silently discarded.
        """
        a = FakeTransport(object(), False)
        a.write(b"before")
        a.loseConnection()
        a.write(b"after")

        self.assertEqual(b"".join(a.stream), b"before")


@implementer(IPushProducer)
class StrictPushProducer:
    """
    An L{IPushProducer} implementation which produces nothing but enforces
    preconditions on its state transition methods.
    """

    _state = "running"

    def stopProducing(self) -> None:
        if self._state == "stopped":
            raise ValueError("Cannot stop already-stopped IPushProducer")
        self._state = "stopped"

    def pauseProducing(self) -> None:
        if self._state != "running":
            raise ValueError(f"Cannot pause {self._state} IPushProducer")
        self._state = "paused"

    def resumeProducing(self) -> None:
        if self._state != "paused":
            raise ValueError(f"Cannot resume {self._state} IPushProducer")
        self._state = "running"


class StrictPushProducerTests(TestCase):
    """
    Tests for L{StrictPushProducer}.
    """

    def _initial(self) -> StrictPushProducer:
        """
        @return: A new L{StrictPushProducer} which has not been through any state
            changes.
        """
        return StrictPushProducer()

    def _stopped(self) -> StrictPushProducer:
        """
        @return: A new, stopped L{StrictPushProducer}.
        """
        producer = StrictPushProducer()
        producer.stopProducing()
        return producer

    def _paused(self) -> StrictPushProducer:
        """
        @return: A new, paused L{StrictPushProducer}.
        """
        producer = StrictPushProducer()
        producer.pauseProducing()
        return producer

    def _resumed(self) -> StrictPushProducer:
        """
        @return: A new L{StrictPushProducer} which has been paused and resumed.
        """
        producer = StrictPushProducer()
        producer.pauseProducing()
        producer.resumeProducing()
        return producer

    def assertStopped(self, producer: StrictPushProducer) -> None:
        """
        Assert that the given producer is in the stopped state.

        @param producer: The producer to verify.
        @type producer: L{StrictPushProducer}
        """
        self.assertEqual(producer._state, "stopped")

    def assertPaused(self, producer: StrictPushProducer) -> None:
        """
        Assert that the given producer is in the paused state.

        @param producer: The producer to verify.
        @type producer: L{StrictPushProducer}
        """
        self.assertEqual(producer._state, "paused")

    def assertRunning(self, producer: StrictPushProducer) -> None:
        """
        Assert that the given producer is in the running state.

        @param producer: The producer to verify.
        @type producer: L{StrictPushProducer}
        """
        self.assertEqual(producer._state, "running")

    def test_stopThenStop(self) -> None:
        """
        L{StrictPushProducer.stopProducing} raises L{ValueError} if called when
        the producer is stopped.
        """
        self.assertRaises(ValueError, self._stopped().stopProducing)

    def test_stopThenPause(self) -> None:
        """
        L{StrictPushProducer.pauseProducing} raises L{ValueError} if called when
        the producer is stopped.
        """
        self.assertRaises(ValueError, self._stopped().pauseProducing)

    def test_stopThenResume(self) -> None:
        """
        L{StrictPushProducer.resumeProducing} raises L{ValueError} if called when
        the producer is stopped.
        """
        self.assertRaises(ValueError, self._stopped().resumeProducing)

    def test_pauseThenStop(self) -> None:
        """
        L{StrictPushProducer} is stopped if C{stopProducing} is called on a paused
        producer.
        """
        producer = self._paused()
        producer.stopProducing()
        self.assertStopped(producer)

    def test_pauseThenPause(self) -> None:
        """
        L{StrictPushProducer.pauseProducing} raises L{ValueError} if called on a
        paused producer.
        """
        producer = self._paused()
        self.assertRaises(ValueError, producer.pauseProducing)

    def test_pauseThenResume(self) -> None:
        """
        L{StrictPushProducer} is resumed if C{resumeProducing} is called on a
        paused producer.
        """
        producer = self._paused()
        producer.resumeProducing()
        self.assertRunning(producer)

    def test_resumeThenStop(self) -> None:
        """
        L{StrictPushProducer} is stopped if C{stopProducing} is called on a
        resumed producer.
        """
        producer = self._resumed()
        producer.stopProducing()
        self.assertStopped(producer)

    def test_resumeThenPause(self) -> None:
        """
        L{StrictPushProducer} is paused if C{pauseProducing} is called on a
        resumed producer.
        """
        producer = self._resumed()
        producer.pauseProducing()
        self.assertPaused(producer)

    def test_resumeThenResume(self) -> None:
        """
        L{StrictPushProducer.resumeProducing} raises L{ValueError} if called on a
        resumed producer.
        """
        producer = self._resumed()
        self.assertRaises(ValueError, producer.resumeProducing)

    def test_stop(self) -> None:
        """
        L{StrictPushProducer} is stopped if C{stopProducing} is called in the
        initial state.
        """
        producer = self._initial()
        producer.stopProducing()
        self.assertStopped(producer)

    def test_pause(self) -> None:
        """
        L{StrictPushProducer} is paused if C{pauseProducing} is called in the
        initial state.
        """
        producer = self._initial()
        producer.pauseProducing()
        self.assertPaused(producer)

    def test_resume(self) -> None:
        """
        L{StrictPushProducer} raises L{ValueError} if C{resumeProducing} is called
        in the initial state.
        """
        producer = self._initial()
        self.assertRaises(ValueError, producer.resumeProducing)


class IOPumpTests(TestCase):
    """
    Tests for L{IOPump}.
    """

    def _testStreamingProducer(self, mode: Literal["server", "client"]) -> None:
        """
        Connect a couple protocol/transport pairs to an L{IOPump} and then pump
        it.  Verify that a streaming producer registered with one of the
        transports does not receive invalid L{IPushProducer} method calls and
        ends in the right state.

        @param mode: C{u"server"} to test a producer registered with the
            server transport.  C{u"client"} to test a producer registered with
            the client transport.
        """
        serverProto = Protocol()
        serverTransport = FakeTransport(serverProto, isServer=True)

        clientProto = Protocol()
        clientTransport = FakeTransport(clientProto, isServer=False)

        pump = connect(
            serverProto,
            serverTransport,
            clientProto,
            clientTransport,
            greet=False,
        )

        producer = StrictPushProducer()
        victim = {
            "server": serverTransport,
            "client": clientTransport,
        }[mode]
        victim.registerProducer(producer, streaming=True)

        pump.pump()
        self.assertEqual("running", producer._state)

    def test_serverStreamingProducer(self) -> None:
        """
        L{IOPump.pump} does not call C{resumeProducing} on a L{IPushProducer}
        (stream producer) registered with the server transport.
        """
        self._testStreamingProducer(mode="server")

    def test_clientStreamingProducer(self) -> None:
        """
        L{IOPump.pump} does not call C{resumeProducing} on a L{IPushProducer}
        (stream producer) registered with the client transport.
        """
        self._testStreamingProducer(mode="client")

    def test_timeAdvances(self) -> None:
        """
        L{IOPump.pump} advances time in the given L{Clock}.
        """
        time_passed = []
        clock = Clock()
        _, _, pump = connectedServerAndClient(Protocol, Protocol, clock=clock)
        clock.callLater(0, lambda: time_passed.append(True))
        self.assertFalse(time_passed)
        pump.pump()
        self.assertTrue(time_passed)
