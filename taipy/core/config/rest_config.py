from taipy.config import Config, Section, _inject_section
from typing import Optional

class RestSection(Section):
    def __init__(self):
        super().__init__(id="rest") 
        self._port: int = 5000
        self._host: str = "127.0.0.1"
        self._use_https: bool = False
        self._ssl_cert: Optional[str] = None
        self._ssl_key: Optional[str] = None


    @property
    def name(self) -> str:
        return "rest"

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value: int):
        self._port = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def use_https(self):
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


default_rest_section = RestSection()

def configure_rest(port: int = 5000, 
                   host: str = "127.0.0.1", 
                   use_https: bool = False, 
                   ssl_cert: Optional[str] = None, 
                   ssl_key: Optional[str] = None):
    if use_https:
        if ssl_cert is None or ssl_key is None:
            raise ValueError("SSL certificate and key are required when use_https is True")
    config = RestSection()
    config.port = port
    config.host = host
    config.use_https = use_https
    config.ssl_cert = ssl_cert
    config.ssl_key = ssl_key
    Config._register(config)

configuration_methods = [("configure_rest", configure_rest)]

_inject_section(RestSection, "rest", default_rest_section, configuration_methods)
