# Copyright 2021-2024 Avaiga Private Limited
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
import typing as t
import warnings
from threading import Thread
from urllib.parse import quote as urlquote
from urllib.parse import urlparse

from twisted.internet import reactor
from twisted.web.proxy import ProxyClient, ProxyClientFactory
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET, Site

from .is_port_open import _is_port_open

# flake8: noqa: E402
from .singleton import _Singleton

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="You do not have a working installation of the service_identity module: 'No module named 'service_identity''.*",  # noqa: E501
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
        return self._gui._server._port

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

    def run(self):
        if self._is_running:
            return
        host = self._gui._get_config("host", "127.0.0.1")
        port = self._listening_port
        if _is_port_open(host, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host}. You have another server application running on the same port."  # noqa: E501
            )
        site = Site(_TaipyReverseProxyResource(host, b"", self._gui))
        reactor.listenTCP(port, site)
        Thread(target=reactor.run, args=(False,)).start()
        self._is_running = True

    def stop(self):
        if not self._is_running:
            return
        self._is_running = False
        reactor.stop()
