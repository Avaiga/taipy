import inspect
import random
import string
import types

try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

from .._compat import range_type, string_types
from ..exceptions import WebSocketError
from .base import BaseProtocol


def export_rpc(arg=None):
    if isinstance(arg, types.FunctionType):
        arg._rpc = arg.__name__
    return arg


def serialize(data):
    return json.dumps(data)


class Prefixes(object):
    def __init__(self):
        self.prefixes = {}

    def add(self, prefix, uri):
        self.prefixes[prefix] = uri

    def resolve(self, curie_or_uri):
        if "http://" in curie_or_uri:
            return curie_or_uri
        elif ':' in curie_or_uri:
            prefix, proc = curie_or_uri.split(':', 1)
            return self.prefixes[prefix] + proc
        else:
            raise Exception(curie_or_uri)


class RemoteProcedures(object):
    def __init__(self):
        self.calls = {}

    def register_procedure(self, uri, proc):
        self.calls[uri] = proc

    def register_object(self, uri, obj):
        for k in inspect.getmembers(obj, inspect.ismethod):
            if '_rpc' in k[1].__dict__:
                proc_uri = uri + k[1]._rpc
                self.calls[proc_uri] = (obj, k[1])

    def call(self, uri, args):
        if uri in self.calls:
            proc = self.calls[uri]

            # Do the correct call whether it's a function or instance method.
            if isinstance(proc, tuple):
                if proc[1].__self__ is None:
                    # Create instance of object and call method
                    return proc[1](proc[0](), *args)
                else:
                    # Call bound method on instance
                    return proc[1](*args)
            else:
                return self.calls[uri](*args)
        else:
            raise Exception("no such uri '{}'".format(uri))


class Channels(object):
    def __init__(self):
        self.channels = {}

    def create(self, uri, prefix_matching=False):
        if uri not in self.channels:
            self.channels[uri] = []

        # TODO: implement prefix matching

    def subscribe(self, uri, client):
        if uri in self.channels:
            self.channels[uri].append(client)

    def unsubscribe(self, uri, client):
        if uri not in self.channels:
            return

        client_index = self.channels[uri].index(client)
        self.channels[uri].pop(client_index)

        if len(self.channels[uri]) == 0:
            del self.channels[uri]

    def publish(self, uri, event, exclude=None, eligible=None):
        if uri not in self.channels:
            return

        # TODO: exclude & eligible

        msg = [WampProtocol.MSG_EVENT, uri, event]

        for client in self.channels[uri]:
            try:
                client.ws.send(serialize(msg))
            except WebSocketError:
                # Seems someone didn't unsubscribe before disconnecting
                self.channels[uri].remove(client)


class WampProtocol(BaseProtocol):
    MSG_WELCOME = 0
    MSG_PREFIX = 1
    MSG_CALL = 2
    MSG_CALL_RESULT = 3
    MSG_CALL_ERROR = 4
    MSG_SUBSCRIBE = 5
    MSG_UNSUBSCRIBE = 6
    MSG_PUBLISH = 7
    MSG_EVENT = 8

    PROTOCOL_NAME = "wamp"

    def __init__(self, *args, **kwargs):
        self.procedures = RemoteProcedures()
        self.prefixes = Prefixes()
        self.session_id = ''.join(
            [random.choice(string.digits + string.letters)
                for i in range_type(16)])

        super(WampProtocol, self).__init__(*args, **kwargs)

    def register_procedure(self, *args, **kwargs):
        self.procedures.register_procedure(*args, **kwargs)

    def register_object(self, *args, **kwargs):
        self.procedures.register_object(*args, **kwargs)

    def register_pubsub(self, *args, **kwargs):
        if not hasattr(self.server, 'channels'):
            self.server.channels = Channels()

        self.server.channels.create(*args, **kwargs)

    def do_handshake(self):
        from geventwebsocket import get_version

        welcome = [
            self.MSG_WELCOME,
            self.session_id,
            1,
            'gevent-websocket/' + get_version()
        ]
        self.app.ws.send(serialize(welcome))

    def _get_exception_info(self, e):
        uri = 'http://TODO#generic'
        desc = str(type(e))
        details = str(e)
        return [uri, desc, details]

    def rpc_call(self, data):
        call_id, curie_or_uri = data[1:3]
        args = data[3:]

        if not isinstance(call_id, string_types):
            raise Exception()
        if not isinstance(curie_or_uri, string_types):
            raise Exception()

        uri = self.prefixes.resolve(curie_or_uri)

        try:
            result = self.procedures.call(uri, args)
            result_msg = [self.MSG_CALL_RESULT, call_id, result]
        except Exception as e:
            result_msg = [self.MSG_CALL_ERROR,
                          call_id] + self._get_exception_info(e)

        self.app.on_message(serialize(result_msg))

    def pubsub_action(self, data):
        action = data[0]
        curie_or_uri = data[1]

        if not isinstance(action, int):
            raise Exception()
        if not isinstance(curie_or_uri, string_types):
            raise Exception()

        uri = self.prefixes.resolve(curie_or_uri)

        if action == self.MSG_SUBSCRIBE and len(data) == 2:
            self.server.channels.subscribe(data[1], self.handler.active_client)

        elif action == self.MSG_UNSUBSCRIBE and len(data) == 2:
            self.server.channels.unsubscribe(
                data[1], self.handler.active_client)

        elif action == self.MSG_PUBLISH and len(data) >= 3:
            payload = data[2] if len(data) >= 3 else None
            exclude = data[3] if len(data) >= 4 else None
            eligible = data[4] if len(data) >= 5 else None

            self.server.channels.publish(uri, payload, exclude, eligible)

    def on_open(self):
        self.app.on_open()
        self.do_handshake()

    def on_message(self, message):
        data = json.loads(message)

        if not isinstance(data, list):
            raise Exception('incoming data is no list')

        if data[0] == self.MSG_PREFIX and len(data) == 3:
            prefix, uri = data[1:3]
            self.prefixes.add(prefix, uri)

        elif data[0] == self.MSG_CALL and len(data) >= 3:
            return self.rpc_call(data)

        elif data[0] in (self.MSG_SUBSCRIBE, self.MSG_UNSUBSCRIBE,
                         self.MSG_PUBLISH):
            return self.pubsub_action(data)
        else:
            raise Exception("Unknown call")

