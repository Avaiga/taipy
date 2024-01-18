import re
import warnings

from .protocols.base import BaseProtocol
from .exceptions import WebSocketError

try:
    from collections import OrderedDict
except ImportError:
    class OrderedDict:
        pass


class WebSocketApplication(object):
    protocol_class = BaseProtocol

    def __init__(self, ws):
        self.protocol = self.protocol_class(self)
        self.ws = ws

    def handle(self):
        self.protocol.on_open()

        while True:
            try:
                message = self.ws.receive()
            except WebSocketError:
                self.protocol.on_close()
                break

            self.protocol.on_message(message)

    def on_open(self, *args, **kwargs):
        pass

    def on_close(self, *args, **kwargs):
        pass

    def on_message(self, message, *args, **kwargs):
        self.ws.send(message, **kwargs)

    @classmethod
    def protocol_name(cls):
        return cls.protocol_class.PROTOCOL_NAME


class Resource(object):
    def __init__(self, apps=None):
        self.apps = apps if apps else []

        if isinstance(apps, dict):
            if not isinstance(apps, OrderedDict):
                warnings.warn("Using an unordered dictionary for the "
                              "app list is discouraged and may lead to "
                              "undefined behavior.", UserWarning)

            self.apps = apps.items()

    # An app can either be a standard WSGI application (an object we call with
    # __call__(self, environ, start_response)) or a class we instantiate
    # (and which can handle websockets). This function tells them apart.
    # Override this if you have apps that can handle websockets but don't
    # fulfill these criteria.
    def _is_websocket_app(self, app):
        return isinstance(app, type) and issubclass(app, WebSocketApplication)

    def _app_by_path(self, environ_path, is_websocket_request):
        # Which app matched the current path?
        for path, app in self.apps:
            if re.match(path, environ_path):
                if is_websocket_request == self._is_websocket_app(app):
                    return app
        return None

    def app_protocol(self, path):
        # app_protocol will only be called for websocket apps
        app = self._app_by_path(path, True)

        if hasattr(app, 'protocol_name'):
            return app.protocol_name()
        else:
            return ''

    def __call__(self, environ, start_response):
        environ = environ
        is_websocket_call = 'wsgi.websocket' in environ
        current_app = self._app_by_path(environ['PATH_INFO'], is_websocket_call)

        if current_app is None:
            raise Exception("No apps defined")

        if is_websocket_call:
            ws = environ['wsgi.websocket']
            current_app = current_app(ws)
            current_app.ws = ws  # TODO: needed?
            current_app.handle()
            # Always return something, calling WSGI middleware may rely on it
            return []
        else:
            return current_app(environ, start_response)
