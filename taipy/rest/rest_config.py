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

from taipy.config import Config, Section, _inject_section
from typing import Optional, Dict, Union, Literal

class RestSection(Section):
    name: str = "REST"

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

    def _clean(self):
        self._port = 5000
        self._host = "127.0.0.1"
        self._use_https = False
        self._ssl_cert = None
        self._ssl_key = None

    def _to_dict(self) -> Dict[str, Union[int, str, bool, None]]:
        return {
            "port": self._port,
            "host": self._host,
            "use_https": self._use_https,
            "ssl_cert": self._ssl_cert,
            "ssl_key": self._ssl_key
        }

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Union[int, str, bool, None]], id=None, config: Optional[Config] = None):
        section = cls()
        section._port = config_as_dict.get("port", 5000)
        section._host = config_as_dict.get("host", "127.0.0.1")
        section._use_https = config_as_dict.get("use_https", False)
        section._ssl_cert = config_as_dict.get("ssl_cert")
        ssl_key = config_as_dict.get("ssl_key")
        section._ssl_key = ssl_key if ssl_key is None or isinstance(ssl_key, str) else None
        return section

    def _update(self, as_dict: Dict[str, Union[int, str, bool, None]], default_section=None):
        self._port = as_dict.get("port", self._port)
        self._host = as_dict.get("host", self._host)
        self._use_https = as_dict.get("use_https", self._use_https)
        self._ssl_cert = as_dict.get("ssl_cert", self._ssl_cert)
        ssl_key = as_dict.get("ssl_key", self._ssl_key)
        self._ssl_key = ssl_key if ssl_key is None or isinstance(ssl_key, str) else None


def configure_rest(port: int = 5000, host: str = "127.0.0.1", use_https: bool = False,
                   ssl_cert: Optional[str] = None, ssl_key: Optional[str] = None):
    config = Config.rest
    config.port = port
    config.host = host
    config.use_https = use_https
    config.ssl_cert = ssl_cert
    config.ssl_key = ssl_key

_inject_section("rest", "rest", default=RestSection(), configuration_methods=[("configure_rest", configure_rest)])
