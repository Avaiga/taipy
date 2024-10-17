from taipy.config import Config, Section, _inject_section
from typing import Optional

class RestSection(Section):
    @property
    def name(self) -> str:
        return "REST"

    def __init__(self):
        self._port: int = 5000
        self._host: str = "127.0.0.1"
        self._use_https: bool = False
        self._ssl_cert: Optional[str] = None
        self._ssl_key: Optional[str] = None

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int):
        self._port = value

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def use_https(self) -> bool:
        return self._use_https

    @use_https.setter
    def use_https(self, value: bool):
        self._use_https = value

    @property
    def ssl_cert(self) -> Optional[str]:
        return self._ssl_cert

    @ssl_cert.setter
    def ssl_cert(self, value: Optional[str]):
        self._ssl_cert = value

    @property
    def ssl_key(self) -> Optional[str]:
        return self._ssl_key

    @ssl_key.setter
    def ssl_key(self, value: Optional[str]):
        self._ssl_key = value

def configure_rest(port: int = 5000, host: str = "127.0.0.1", use_https: bool = False,
                   ssl_cert: Optional[str] = None, ssl_key: Optional[str] = None):
    config = Config.rest
    config.port = port
    config.host = host
    config.use_https = use_https
    config.ssl_cert = ssl_cert
    config.ssl_key = ssl_key

_inject_section("rest", "rest", default=RestSection(), configuration_methods=[("configure_rest", configure_rest)])

