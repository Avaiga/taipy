# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from io import BytesIO

from twisted.internet import abstract, defer, protocol
from twisted.protocols import basic, loopback
from twisted.trial import unittest


class BufferingServer(protocol.Protocol):
    buffer = b""

    def dataReceived(self, data: bytes) -> None:
        self.buffer += data


class FileSendingClient(protocol.Protocol):
    def __init__(self, f: BytesIO) -> None:
        self.f = f

    def connectionMade(self) -> None:
        assert self.transport is not None
        s = basic.FileSender()
        d = s.beginFileTransfer(self.f, self.transport, lambda x: x)
        d.addCallback(lambda r: self.transport.loseConnection())


class FileSenderTests(unittest.TestCase):
    def testSendingFile(self) -> defer.Deferred[None]:
        testStr = b"xyz" * 100 + b"abc" * 100 + b"123" * 100
        s = BufferingServer()
        c = FileSendingClient(BytesIO(testStr))

        d: defer.Deferred[None] = loopback.loopbackTCP(s, c)

        def callback(x: object) -> None:
            self.assertEqual(s.buffer, testStr)

        return d.addCallback(callback)

    def testSendingEmptyFile(self) -> None:
        fileSender = basic.FileSender()
        consumer = abstract.FileDescriptor()
        consumer.connected = 1
        emptyFile = BytesIO(b"")

        d = fileSender.beginFileTransfer(emptyFile, consumer, lambda x: x)

        # The producer will be immediately exhausted, and so immediately
        # unregistered
        self.assertIsNone(consumer.producer)

        # Which means the Deferred from FileSender should have been called
        self.assertTrue(d.called, "producer unregistered with deferred being called")
