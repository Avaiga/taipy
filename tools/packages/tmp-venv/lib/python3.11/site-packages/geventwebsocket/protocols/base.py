class BaseProtocol(object):
    PROTOCOL_NAME = ''

    def __init__(self, app):
        self._app = app

    def on_open(self):
        self.app.on_open()

    def on_message(self, message):
        self.app.on_message(message)

    def on_close(self, reason=None):
        self.app.on_close(reason)

    @property
    def app(self):
        if self._app:
            return self._app
        else:
            raise Exception("No application coupled")

    @property
    def server(self):
        if not hasattr(self.app, 'ws'):
            return None

        return self.app.ws.handler.server

    @property
    def handler(self):
        if not hasattr(self.app, 'ws'):
            return None

        return self.app.ws.handler
