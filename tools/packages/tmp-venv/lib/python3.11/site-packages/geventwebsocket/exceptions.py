from socket import error as socket_error


class WebSocketError(socket_error):
    """
    Base class for all websocket errors.
    """


class ProtocolError(WebSocketError):
    """
    Raised if an error occurs when de/encoding the websocket protocol.
    """


class FrameTooLargeException(ProtocolError):
    """
    Raised if a frame is received that is too large.
    """
