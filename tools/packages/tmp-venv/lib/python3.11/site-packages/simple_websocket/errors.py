from wsproto.frame_protocol import CloseReason


class ConnectionError(RuntimeError):  # pragma: no cover
    """Connection error exception class."""
    def __init__(self, status_code=None):
        self.status_code = status_code
        super().__init__(f'Connection error: {status_code}')


class ConnectionClosed(RuntimeError):
    """Connection closed exception class."""
    def __init__(self, reason=CloseReason.NO_STATUS_RCVD, message=None):
        self.reason = reason
        self.message = message
        super().__init__(f'Connection closed: {reason} {message or ""}')
