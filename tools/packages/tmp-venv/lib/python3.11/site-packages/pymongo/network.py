# Copyright 2015-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Internal network layer helper methods."""
from __future__ import annotations

import datetime
import errno
import socket
import struct
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Union,
    cast,
)

from bson import _decode_all_selective
from pymongo import _csot, helpers, message, ssl_support
from pymongo.common import MAX_MESSAGE_SIZE
from pymongo.compression_support import _NO_COMPRESSION, decompress
from pymongo.errors import (
    NotPrimaryError,
    OperationFailure,
    ProtocolError,
    _OperationCancelled,
)
from pymongo.message import _UNPACK_REPLY, _OpMsg, _OpReply
from pymongo.monitoring import _is_speculative_authenticate
from pymongo.socket_checker import _errno_from_exception

if TYPE_CHECKING:
    from bson import CodecOptions
    from pymongo.client_session import ClientSession
    from pymongo.compression_support import SnappyContext, ZlibContext, ZstdContext
    from pymongo.mongo_client import MongoClient
    from pymongo.monitoring import _EventListeners
    from pymongo.pool import Connection
    from pymongo.read_concern import ReadConcern
    from pymongo.read_preferences import _ServerMode
    from pymongo.typings import _Address, _CollationIn, _DocumentOut, _DocumentType
    from pymongo.write_concern import WriteConcern

_UNPACK_HEADER = struct.Struct("<iiii").unpack


def command(
    conn: Connection,
    dbname: str,
    spec: MutableMapping[str, Any],
    is_mongos: bool,
    read_preference: Optional[_ServerMode],
    codec_options: CodecOptions[_DocumentType],
    session: Optional[ClientSession],
    client: Optional[MongoClient],
    check: bool = True,
    allowable_errors: Optional[Sequence[Union[str, int]]] = None,
    address: Optional[_Address] = None,
    listeners: Optional[_EventListeners] = None,
    max_bson_size: Optional[int] = None,
    read_concern: Optional[ReadConcern] = None,
    parse_write_concern_error: bool = False,
    collation: Optional[_CollationIn] = None,
    compression_ctx: Union[SnappyContext, ZlibContext, ZstdContext, None] = None,
    use_op_msg: bool = False,
    unacknowledged: bool = False,
    user_fields: Optional[Mapping[str, Any]] = None,
    exhaust_allowed: bool = False,
    write_concern: Optional[WriteConcern] = None,
) -> _DocumentType:
    """Execute a command over the socket, or raise socket.error.

    :Parameters:
      - `conn`: a Connection instance
      - `dbname`: name of the database on which to run the command
      - `spec`: a command document as an ordered dict type, eg SON.
      - `is_mongos`: are we connected to a mongos?
      - `read_preference`: a read preference
      - `codec_options`: a CodecOptions instance
      - `session`: optional ClientSession instance.
      - `client`: optional MongoClient instance for updating $clusterTime.
      - `check`: raise OperationFailure if there are errors
      - `allowable_errors`: errors to ignore if `check` is True
      - `address`: the (host, port) of `conn`
      - `listeners`: An instance of :class:`~pymongo.monitoring.EventListeners`
      - `max_bson_size`: The maximum encoded bson size for this server
      - `read_concern`: The read concern for this command.
      - `parse_write_concern_error`: Whether to parse the ``writeConcernError``
        field in the command response.
      - `collation`: The collation for this command.
      - `compression_ctx`: optional compression Context.
      - `use_op_msg`: True if we should use OP_MSG.
      - `unacknowledged`: True if this is an unacknowledged command.
      - `user_fields` (optional): Response fields that should be decoded
        using the TypeDecoders from codec_options, passed to
        bson._decode_all_selective.
      - `exhaust_allowed`: True if we should enable OP_MSG exhaustAllowed.
    """
    name = next(iter(spec))
    ns = dbname + ".$cmd"
    speculative_hello = False

    # Publish the original command document, perhaps with lsid and $clusterTime.
    orig = spec
    if is_mongos and not use_op_msg:
        assert read_preference is not None
        spec = message._maybe_add_read_preference(spec, read_preference)
    if read_concern and not (session and session.in_transaction):
        if read_concern.level:
            spec["readConcern"] = read_concern.document
        if session:
            session._update_read_concern(spec, conn)
    if collation is not None:
        spec["collation"] = collation

    publish = listeners is not None and listeners.enabled_for_commands
    if publish:
        start = datetime.datetime.now()
        speculative_hello = _is_speculative_authenticate(name, spec)

    if compression_ctx and name.lower() in _NO_COMPRESSION:
        compression_ctx = None

    if client and client._encrypter and not client._encrypter._bypass_auto_encryption:
        spec = orig = client._encrypter.encrypt(dbname, spec, codec_options)

    # Support CSOT
    if client:
        conn.apply_timeout(client, spec)
    _csot.apply_write_concern(spec, write_concern)

    if use_op_msg:
        flags = _OpMsg.MORE_TO_COME if unacknowledged else 0
        flags |= _OpMsg.EXHAUST_ALLOWED if exhaust_allowed else 0
        request_id, msg, size, max_doc_size = message._op_msg(
            flags, spec, dbname, read_preference, codec_options, ctx=compression_ctx
        )
        # If this is an unacknowledged write then make sure the encoded doc(s)
        # are small enough, otherwise rely on the server to return an error.
        if unacknowledged and max_bson_size is not None and max_doc_size > max_bson_size:
            message._raise_document_too_large(name, size, max_bson_size)
    else:
        request_id, msg, size = message._query(
            0, ns, 0, -1, spec, None, codec_options, compression_ctx
        )

    if max_bson_size is not None and size > max_bson_size + message._COMMAND_OVERHEAD:
        message._raise_document_too_large(name, size, max_bson_size + message._COMMAND_OVERHEAD)

    if publish:
        encoding_duration = datetime.datetime.now() - start
        assert listeners is not None
        assert address is not None
        listeners.publish_command_start(
            orig, dbname, request_id, address, service_id=conn.service_id
        )
        start = datetime.datetime.now()

    try:
        conn.conn.sendall(msg)
        if use_op_msg and unacknowledged:
            # Unacknowledged, fake a successful command response.
            reply = None
            response_doc: _DocumentOut = {"ok": 1}
        else:
            reply = receive_message(conn, request_id)
            conn.more_to_come = reply.more_to_come
            unpacked_docs = reply.unpack_response(
                codec_options=codec_options, user_fields=user_fields
            )

            response_doc = unpacked_docs[0]
            if client:
                client._process_response(response_doc, session)
            if check:
                helpers._check_command_response(
                    response_doc,
                    conn.max_wire_version,
                    allowable_errors,
                    parse_write_concern_error=parse_write_concern_error,
                )
    except Exception as exc:
        if publish:
            duration = (datetime.datetime.now() - start) + encoding_duration
            if isinstance(exc, (NotPrimaryError, OperationFailure)):
                failure: _DocumentOut = exc.details  # type: ignore[assignment]
            else:
                failure = message._convert_exception(exc)
            assert listeners is not None
            assert address is not None
            listeners.publish_command_failure(
                duration,
                failure,
                name,
                request_id,
                address,
                service_id=conn.service_id,
                database_name=dbname,
            )
        raise
    if publish:
        duration = (datetime.datetime.now() - start) + encoding_duration
        assert listeners is not None
        assert address is not None
        listeners.publish_command_success(
            duration,
            response_doc,
            name,
            request_id,
            address,
            service_id=conn.service_id,
            speculative_hello=speculative_hello,
            database_name=dbname,
        )

    if client and client._encrypter and reply:
        decrypted = client._encrypter.decrypt(reply.raw_command_response())
        response_doc = cast(
            "_DocumentOut", _decode_all_selective(decrypted, codec_options, user_fields)[0]
        )

    return response_doc  # type: ignore[return-value]


_UNPACK_COMPRESSION_HEADER = struct.Struct("<iiB").unpack


def receive_message(
    conn: Connection, request_id: Optional[int], max_message_size: int = MAX_MESSAGE_SIZE
) -> Union[_OpReply, _OpMsg]:
    """Receive a raw BSON message or raise socket.error."""
    if _csot.get_timeout():
        deadline = _csot.get_deadline()
    else:
        timeout = conn.conn.gettimeout()
        if timeout:
            deadline = time.monotonic() + timeout
        else:
            deadline = None
    # Ignore the response's request id.
    length, _, response_to, op_code = _UNPACK_HEADER(_receive_data_on_socket(conn, 16, deadline))
    # No request_id for exhaust cursor "getMore".
    if request_id is not None:
        if request_id != response_to:
            raise ProtocolError(f"Got response id {response_to!r} but expected {request_id!r}")
    if length <= 16:
        raise ProtocolError(
            f"Message length ({length!r}) not longer than standard message header size (16)"
        )
    if length > max_message_size:
        raise ProtocolError(
            f"Message length ({length!r}) is larger than server max "
            f"message size ({max_message_size!r})"
        )
    if op_code == 2012:
        op_code, _, compressor_id = _UNPACK_COMPRESSION_HEADER(
            _receive_data_on_socket(conn, 9, deadline)
        )
        data = decompress(_receive_data_on_socket(conn, length - 25, deadline), compressor_id)
    else:
        data = _receive_data_on_socket(conn, length - 16, deadline)

    try:
        unpack_reply = _UNPACK_REPLY[op_code]
    except KeyError:
        raise ProtocolError(
            f"Got opcode {op_code!r} but expected {_UNPACK_REPLY.keys()!r}"
        ) from None
    return unpack_reply(data)


_POLL_TIMEOUT = 0.5


def wait_for_read(conn: Connection, deadline: Optional[float]) -> None:
    """Block until at least one byte is read, or a timeout, or a cancel."""
    context = conn.cancel_context
    # Only Monitor connections can be cancelled.
    if context:
        sock = conn.conn
        timed_out = False
        while True:
            # SSLSocket can have buffered data which won't be caught by select.
            if hasattr(sock, "pending") and sock.pending() > 0:
                readable = True
            else:
                # Wait up to 500ms for the socket to become readable and then
                # check for cancellation.
                if deadline:
                    remaining = deadline - time.monotonic()
                    # When the timeout has expired perform one final check to
                    # see if the socket is readable. This helps avoid spurious
                    # timeouts on AWS Lambda and other FaaS environments.
                    if remaining <= 0:
                        timed_out = True
                    timeout = max(min(remaining, _POLL_TIMEOUT), 0)
                else:
                    timeout = _POLL_TIMEOUT
                readable = conn.socket_checker.select(sock, read=True, timeout=timeout)
            if context.cancelled:
                raise _OperationCancelled("hello cancelled")
            if readable:
                return
            if timed_out:
                raise socket.timeout("timed out")


# Errors raised by sockets (and TLS sockets) when in non-blocking mode.
BLOCKING_IO_ERRORS = (BlockingIOError, *ssl_support.BLOCKING_IO_ERRORS)


def _receive_data_on_socket(conn: Connection, length: int, deadline: Optional[float]) -> memoryview:
    buf = bytearray(length)
    mv = memoryview(buf)
    bytes_read = 0
    while bytes_read < length:
        try:
            wait_for_read(conn, deadline)
            # CSOT: Update timeout. When the timeout has expired perform one
            # final non-blocking recv. This helps avoid spurious timeouts when
            # the response is actually already buffered on the client.
            if _csot.get_timeout() and deadline is not None:
                conn.set_conn_timeout(max(deadline - time.monotonic(), 0))
            chunk_length = conn.conn.recv_into(mv[bytes_read:])
        except BLOCKING_IO_ERRORS:
            raise socket.timeout("timed out") from None
        except OSError as exc:
            if _errno_from_exception(exc) == errno.EINTR:
                continue
            raise
        if chunk_length == 0:
            raise OSError("connection closed")

        bytes_read += chunk_length

    return mv
