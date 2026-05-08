# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import contextlib
import threading
import typing as t
import warnings
from threading import Event, Thread
from urllib.parse import quote as urlquote
from urllib.parse import urlparse

from twisted.internet import reactor
from twisted.web.proxy import ProxyClient, ProxyClientFactory
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET, Site

from .._warnings import _warn
from .is_port_open import _is_port_open

# flake8: noqa: E402
from .singleton import _Singleton

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="You don't have a working installation of the service_identity module: "
            "'No module named 'service_identity''.*",
)

if t.TYPE_CHECKING:
    from ..gui import Gui


def _modifiedHandleResponseEnd(self):
    if self._finished:
        return
    self._finished = True
    with contextlib.suppress(Exception):
        self.father.finish()
    self.transport.loseConnection()


setattr(ProxyClient, "handleResponseEnd", _modifiedHandleResponseEnd)  # noqa: B010


class _TaipyReverseProxyResource(Resource):
    proxyClientFactoryClass = ProxyClientFactory

    def __init__(self, host, path, gui: "Gui", reactor=reactor):
        Resource.__init__(self)
        self.host = host
        self.path = path
        self.reactor = reactor
        self._gui = gui

    def getChild(self, path, request):
        return _TaipyReverseProxyResource(
            self.host,
            self.path + b"/" + urlquote(path, safe=b"").encode("utf-8"),
            self._gui,
            self.reactor,
        )

    def _get_port(self):
        return self._gui._server.get_port()

    def render(self, request):
        port = self._get_port()
        host = self.host if port == 80 else "%s:%d" % (self.host, port)
        request.requestHeaders.setRawHeaders(b"host", [host.encode("ascii")])
        request.content.seek(0, 0)
        rest = self.path + b"?" + qs if (qs := urlparse(request.uri)[4]) else self.path
        clientFactory = self.proxyClientFactoryClass(
            request.method,
            rest,
            request.clientproto,
            request.getAllHeaders(),
            request.content.read(),
            request,
        )
        self.reactor.connectTCP(self.host, port, clientFactory)
        return NOT_DONE_YET


class NotebookProxy(object, metaclass=_Singleton):
    def __init__(self, gui: "Gui", listening_port: int) -> None:
        self._listening_port = listening_port
        self._gui = gui
        self._is_running = False
        self._thread: t.Optional[Thread] = None
        self._stop_event = Event()
        self._reactor_thread_id: t.Optional[int] = None

    def run(self):
        if self._is_running and self._thread and self._thread.is_alive():
            return

        host = self._gui._get_config("host", "127.0.0.1")
        port = self._listening_port

        if _is_port_open(host, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host}. "
                f"You have another server application running on the same port."
            )

        self._thread = Thread(
            target=self._run_reactor,
            args=(host, port),
            daemon=True,
            name=f"TaipyNotebookProxy-{port}"
        )

        self._stop_event.clear()
        self._thread.start()
        self._is_running = True

        import time
        time.sleep(0.1)

    def _run_reactor(self, host: str, port: int):
        try:
            ident = threading.current_thread().ident
            self._reactor_thread_id = ident if ident is not None else 0
            site = Site(_TaipyReverseProxyResource(host, b"", self._gui))
            reactor.listenTCP(port, site)

            reactor.run(installSignalHandlers=False)

        except Exception as e:
            _warn(f"Reactor error: {e}")
        finally:
            self._is_running = False
            self._reactor_thread_id = None

    def stop(self):
        if not self._is_running:
            return

        self._stop_event.set()
        self._is_running = False

        if (self._reactor_thread_id and
            threading.current_thread().ident == self._reactor_thread_id):
            reactor.stop()
        else:

            reactor.callFromThread(reactor.stop)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

            if self._thread.is_alive():
                _warn(f"Warning: Proxy thread {self._thread.name} did not terminate cleanly")

        self._thread = None
        self._reactor_thread_id = None

    def is_alive(self) -> bool:
        return (self._is_running and
                self._thread is not None and
                self._thread.is_alive())

    def __del__(self):
        with contextlib.suppress(Exception):
            self.stop()
