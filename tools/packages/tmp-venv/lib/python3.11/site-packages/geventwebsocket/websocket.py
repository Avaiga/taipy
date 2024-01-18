import struct

from socket import error

from ._compat import string_types, range_type, text_type
from .exceptions import ProtocolError
from .exceptions import WebSocketError
from .exceptions import FrameTooLargeException
from .utf8validator import Utf8Validator


MSG_SOCKET_DEAD = "Socket is dead"
MSG_ALREADY_CLOSED = "Connection is already closed"
MSG_CLOSED = "Connection closed"


class WebSocket(object):
    """
    Base class for supporting websocket operations.

    :ivar environ: The http environment referenced by this connection.
    :ivar closed: Whether this connection is closed/closing.
    :ivar stream: The underlying file like object that will be read from /
        written to by this WebSocket object.
    """

    __slots__ = ('utf8validator', 'utf8validate_last', 'environ', 'closed',
                 'stream', 'raw_write', 'raw_read', 'handler')

    OPCODE_CONTINUATION = 0x00
    OPCODE_TEXT = 0x01
    OPCODE_BINARY = 0x02
    OPCODE_CLOSE = 0x08
    OPCODE_PING = 0x09
    OPCODE_PONG = 0x0a

    def __init__(self, environ, stream, handler):
        self.environ = environ
        self.closed = False

        self.stream = stream

        self.raw_write = stream.write
        self.raw_read = stream.read

        self.utf8validator = Utf8Validator()
        self.handler = handler

    def __del__(self):
        try:
            self.close()
        except:
            # close() may fail if __init__ didn't complete
            pass

    def _decode_bytes(self, bytestring):
        """
        Internal method used to convert the utf-8 encoded bytestring into
        unicode.

        If the conversion fails, the socket will be closed.
        """

        if not bytestring:
            return ''

        try:
            return bytestring.decode('utf-8')
        except UnicodeDecodeError:
            self.close(1007)

            raise

    def _encode_bytes(self, text):
        """
        :returns: The utf-8 byte string equivalent of `text`.
        """

        if not isinstance(text, str):
            text = text_type(text or '')

        return text.encode("utf-8")

    def _is_valid_close_code(self, code):
        """
        :returns: Whether the returned close code is a valid hybi return code.
        """
        if code < 1000:
            return False

        if 1004 <= code <= 1006:
            return False

        if 1012 <= code <= 1016:
            return False

        if code == 1100:
            # not sure about this one but the autobahn fuzzer requires it.
            return False

        if 2000 <= code <= 2999:
            return False

        return True

    @property
    def current_app(self):
        if hasattr(self.handler.server.application, 'current_app'):
            return self.handler.server.application.current_app
        else:
            # For backwards compatibility reasons
            class MockApp():
                def on_close(self, *args):
                    pass

            return MockApp()

    @property
    def origin(self):
        if not self.environ:
            return

        return self.environ.get('HTTP_ORIGIN')

    @property
    def protocol(self):
        if not self.environ:
            return

        return self.environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')

    @property
    def version(self):
        if not self.environ:
            return

        return self.environ.get('HTTP_SEC_WEBSOCKET_VERSION')

    @property
    def path(self):
        if not self.environ:
            return

        return self.environ.get('PATH_INFO')

    @property
    def logger(self):
        return self.handler.logger

    def handle_close(self, header, payload):
        """
        Called when a close frame has been decoded from the stream.

        :param header: The decoded `Header`.
        :param payload: The bytestring payload associated with the close frame.
        """
        if not payload:
            self.close(1000, None)

            return

        if len(payload) < 2:
            raise ProtocolError('Invalid close frame: {0} {1}'.format(
                header, payload))

        code = struct.unpack('!H', payload[:2])[0]
        payload = payload[2:]

        if payload:
            validator = Utf8Validator()
            val = validator.validate(payload)

            if not val[0]:
                raise UnicodeError

        if not self._is_valid_close_code(code):
            raise ProtocolError('Invalid close code {0}'.format(code))

        self.close(code, payload)

    def handle_ping(self, header, payload):
        self.send_frame(payload, self.OPCODE_PONG)

    def handle_pong(self, header, payload):
        pass

    def read_frame(self):
        """
        Block until a full frame has been read from the socket.

        This is an internal method as calling this will not cleanup correctly
        if an exception is called. Use `receive` instead.

        :return: The header and payload as a tuple.
        """

        header = Header.decode_header(self.stream)

        if header.flags:
            raise ProtocolError

        if not header.length:
            return header, b''

        try:
            payload = self.raw_read(header.length)
        except error:
            payload = b''
        except Exception:
            # TODO log out this exception
            payload = b''

        if len(payload) != header.length:
            raise WebSocketError('Unexpected EOF reading frame payload')

        if header.mask:
            payload = header.unmask_payload(payload)

        return header, payload

    def validate_utf8(self, payload):
        # Make sure the frames are decodable independently
        self.utf8validate_last = self.utf8validator.validate(payload)

        if not self.utf8validate_last[0]:
            raise UnicodeError("Encountered invalid UTF-8 while processing "
                               "text message at payload octet index "
                               "{0:d}".format(self.utf8validate_last[3]))

    def read_message(self):
        """
        Return the next text or binary message from the socket.

        This is an internal method as calling this will not cleanup correctly
        if an exception is called. Use `receive` instead.
        """
        opcode = None
        message = bytearray()

        while True:
            header, payload = self.read_frame()
            f_opcode = header.opcode

            if f_opcode in (self.OPCODE_TEXT, self.OPCODE_BINARY):
                # a new frame
                if opcode:
                    raise ProtocolError("The opcode in non-fin frame is "
                                        "expected to be zero, got "
                                        "{0!r}".format(f_opcode))

                # Start reading a new message, reset the validator
                self.utf8validator.reset()
                self.utf8validate_last = (True, True, 0, 0)

                opcode = f_opcode

            elif f_opcode == self.OPCODE_CONTINUATION:
                if not opcode:
                    raise ProtocolError("Unexpected frame with opcode=0")

            elif f_opcode == self.OPCODE_PING:
                self.handle_ping(header, payload)
                continue

            elif f_opcode == self.OPCODE_PONG:
                self.handle_pong(header, payload)
                continue

            elif f_opcode == self.OPCODE_CLOSE:
                self.handle_close(header, payload)
                return

            else:
                raise ProtocolError("Unexpected opcode={0!r}".format(f_opcode))

            if opcode == self.OPCODE_TEXT:
                self.validate_utf8(payload)

            message += payload

            if header.fin:
                break

        if opcode == self.OPCODE_TEXT:
            self.validate_utf8(message)
            return self._decode_bytes(message)
        else:
            return message

    def receive(self):
        """
        Read and return a message from the stream. If `None` is returned, then
        the socket is considered closed/errored.
        """

        if self.closed:
            self.current_app.on_close(MSG_ALREADY_CLOSED)
            raise WebSocketError(MSG_ALREADY_CLOSED)

        try:
            return self.read_message()
        except UnicodeError:
            self.close(1007)
        except ProtocolError:
            self.close(1002)
        except error:
            self.close()
            self.current_app.on_close(MSG_CLOSED)

        return None

    def send_frame(self, message, opcode):
        """
        Send a frame over the websocket with message as its payload
        """
        if self.closed:
            self.current_app.on_close(MSG_ALREADY_CLOSED)
            raise WebSocketError(MSG_ALREADY_CLOSED)

        if opcode in (self.OPCODE_TEXT, self.OPCODE_PING):
            message = self._encode_bytes(message)
        elif opcode == self.OPCODE_BINARY:
            message = bytes(message)

        header = Header.encode_header(True, opcode, b'', len(message), 0)

        try:
            self.raw_write(header + message)
        except error:
            raise WebSocketError(MSG_SOCKET_DEAD)
        except:
            raise

    def send(self, message, binary=None):
        """
        Send a frame over the websocket with message as its payload
        """
        if binary is None:
            binary = not isinstance(message, string_types)

        opcode = self.OPCODE_BINARY if binary else self.OPCODE_TEXT

        try:
            self.send_frame(message, opcode)
        except WebSocketError:
            self.current_app.on_close(MSG_SOCKET_DEAD)
            raise WebSocketError(MSG_SOCKET_DEAD)

    def close(self, code=1000, message=b''):
        """
        Close the websocket and connection, sending the specified code and
        message.  The underlying socket object is _not_ closed, that is the
        responsibility of the initiator.
        """

        if self.closed:
            self.current_app.on_close(MSG_ALREADY_CLOSED)

        try:
            message = self._encode_bytes(message)

            self.send_frame(message, opcode=self.OPCODE_CLOSE)
        except WebSocketError:
            # Failed to write the closing frame but it's ok because we're
            # closing the socket anyway.
            self.logger.debug("Failed to write closing frame -> closing socket")
        finally:
            self.logger.debug("Closed WebSocket")
            self.closed = True

            self.stream = None
            self.raw_write = None
            self.raw_read = None

            self.environ = None

            #self.current_app.on_close(MSG_ALREADY_CLOSED)


class Stream(object):
    """
    Wraps the handler's socket/rfile attributes and makes it in to a file like
    object that can be read from/written to by the lower level websocket api.
    """

    __slots__ = ('handler', 'read', 'write')

    def __init__(self, handler):
        self.handler = handler
        self.read = handler.rfile.read
        self.write = handler.socket.sendall


class Header(object):
    __slots__ = ('fin', 'mask', 'opcode', 'flags', 'length')

    FIN_MASK = 0x80
    OPCODE_MASK = 0x0f
    MASK_MASK = 0x80
    LENGTH_MASK = 0x7f

    RSV0_MASK = 0x40
    RSV1_MASK = 0x20
    RSV2_MASK = 0x10

    # bitwise mask that will determine the reserved bits for a frame header
    HEADER_FLAG_MASK = RSV0_MASK | RSV1_MASK | RSV2_MASK

    def __init__(self, fin=0, opcode=0, flags=0, length=0):
        self.mask = ''
        self.fin = fin
        self.opcode = opcode
        self.flags = flags
        self.length = length

    def mask_payload(self, payload):
        payload = bytearray(payload)
        mask = bytearray(self.mask)

        for i in range_type(self.length):
            payload[i] ^= mask[i % 4]

        return payload

    # it's the same operation
    unmask_payload = mask_payload

    def __repr__(self):
        opcodes = {
            0: 'continuation(0)',
            1: 'text(1)',
            2: 'binary(2)',
            8: 'close(8)',
            9: 'ping(9)',
            10: 'pong(10)'
        }
        flags = {
            0x40: 'RSV1 MASK',
            0x20: 'RSV2 MASK',
            0x10: 'RSV3 MASK'
        }

        return ("<Header fin={0} opcode={1} length={2} flags={3} mask={4} at "
                "0x{5:x}>").format(
                    self.fin,
                    opcodes.get(self.opcode, 'reserved({})'.format(self.opcode)),
                    self.length,
                    flags.get(self.flags, 'reserved({})'.format(self.flags)),
                    self.mask, id(self)
        )

    @classmethod
    def decode_header(cls, stream):
        """
        Decode a WebSocket header.

        :param stream: A file like object that can be 'read' from.
        :returns: A `Header` instance.
        """
        read = stream.read
        data = read(2)

        if len(data) != 2:
            raise WebSocketError("Unexpected EOF while decoding header")

        first_byte, second_byte = struct.unpack('!BB', data)

        header = cls(
            fin=first_byte & cls.FIN_MASK == cls.FIN_MASK,
            opcode=first_byte & cls.OPCODE_MASK,
            flags=first_byte & cls.HEADER_FLAG_MASK,
            length=second_byte & cls.LENGTH_MASK)

        has_mask = second_byte & cls.MASK_MASK == cls.MASK_MASK

        if header.opcode > 0x07:
            if not header.fin:
                raise ProtocolError(
                    "Received fragmented control frame: {0!r}".format(data))

            # Control frames MUST have a payload length of 125 bytes or less
            if header.length > 125:
                raise FrameTooLargeException(
                    "Control frame cannot be larger than 125 bytes: "
                    "{0!r}".format(data))

        if header.length == 126:
            # 16 bit length
            data = read(2)

            if len(data) != 2:
                raise WebSocketError('Unexpected EOF while decoding header')

            header.length = struct.unpack('!H', data)[0]
        elif header.length == 127:
            # 64 bit length
            data = read(8)

            if len(data) != 8:
                raise WebSocketError('Unexpected EOF while decoding header')

            header.length = struct.unpack('!Q', data)[0]

        if has_mask:
            mask = read(4)

            if len(mask) != 4:
                raise WebSocketError('Unexpected EOF while decoding header')

            header.mask = mask

        return header

    @classmethod
    def encode_header(cls, fin, opcode, mask, length, flags):
        """
        Encodes a WebSocket header.

        :param fin: Whether this is the final frame for this opcode.
        :param opcode: The opcode of the payload, see `OPCODE_*`
        :param mask: Whether the payload is masked.
        :param length: The length of the frame.
        :param flags: The RSV* flags.
        :return: A bytestring encoded header.
        """
        first_byte = opcode
        second_byte = 0
        extra = b""
        result = bytearray()

        if fin:
            first_byte |= cls.FIN_MASK

        if flags & cls.RSV0_MASK:
            first_byte |= cls.RSV0_MASK

        if flags & cls.RSV1_MASK:
            first_byte |= cls.RSV1_MASK

        if flags & cls.RSV2_MASK:
            first_byte |= cls.RSV2_MASK

        # now deal with length complexities
        if length < 126:
            second_byte += length
        elif length <= 0xffff:
            second_byte += 126
            extra = struct.pack('!H', length)
        elif length <= 0xffffffffffffffff:
            second_byte += 127
            extra = struct.pack('!Q', length)
        else:
            raise FrameTooLargeException

        if mask:
            second_byte |= cls.MASK_MASK

        result.append(first_byte)
        result.append(second_byte)
        result.extend(extra)

        if mask:
            result.extend(mask)

        return result
