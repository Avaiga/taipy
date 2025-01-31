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
from copy import copy
from typing import Dict, Optional, Tuple

from taipy.common.config import UniqueSection
from taipy.common.config.common._template_handler import _TemplateHandler as _tpl
from taipy.common.config.config import Config


class RestConfig(UniqueSection):
    """Configuration parameters for running the `Rest^` service"""

    name: str = "REST"

    _DEFAULT_PORT: int = 5000
    _DEFAULT_HOST: str = "127.0.0.1"
    _DEFAULT_USE_HTTPS: bool = False
    _DEFAULT_SSL_CERT: Optional[str] = None
    _DEFAULT_SSL_KEY: Optional[str] = None

    def __init__(
        self,
        port: int = _DEFAULT_PORT,
        host: str = _DEFAULT_HOST,
        use_https: bool = _DEFAULT_USE_HTTPS,
        ssl_cert: Optional[str] = _DEFAULT_SSL_CERT,
        ssl_key: Optional[str] = _DEFAULT_SSL_KEY,
        **properties,
    ):
        self._port = port
        self._host = host
        self._use_https = use_https
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key
        super().__init__(**properties)

    def __copy__(self) -> "RestConfig":
        return RestConfig(
            self.port,
            self.host,
            self.use_https,
            self.ssl_cert,
            self.ssl_key,
            **copy(self._properties),
        )

    def _clean(self):
        self.port = self._DEFAULT_PORT
        self.host = self._DEFAULT_HOST
        self.use_https = self._DEFAULT_USE_HTTPS
        self.ssl_cert = self._DEFAULT_SSL_CERT
        self.ssl_key = self._DEFAULT_SSL_KEY

    def _update(self, config_as_dict: Dict, default_section=None):
        self.port = config_as_dict.pop("port", self.port)
        self.host = config_as_dict.pop("host", self.host)
        self.use_https = config_as_dict.pop("use_https", self.use_https)
        self.ssl_cert = config_as_dict.pop("ssl_cert", self.ssl_cert)
        self.ssl_key = config_as_dict.pop("ssl_key", self.ssl_key)

        self._properties.update(config_as_dict)

    def _to_dict(self):
        return {
            key: value
            for key, value in {
                "port": self.port,
                "host": self.host,
                "use_https": self.use_https,
                "ssl_cert": self.ssl_cert,
            }.items()
            if value is not None
        }

    @classmethod
    def _from_dict(cls, data: Dict):
        return RestConfig(**data)

    @classmethod
    def default_config(cls) -> "RestConfig":
        return RestConfig(
            cls._DEFAULT_PORT,
            cls._DEFAULT_HOST,
            cls._DEFAULT_USE_HTTPS,
            cls._DEFAULT_SSL_CERT,
            cls._DEFAULT_SSL_KEY,
        )

    @property
    def port(self) -> int:
        """The port on which the REST service will be running"""
        return _tpl._replace_templates(self._port)

    @port.setter
    def port(self, value: int):
        self._port = value

    @property
    def host(self) -> str:
        """The host on which the REST service will be running"""
        return _tpl._replace_templates(self._host)

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def use_https(self) -> bool:
        """Whether to use HTTPS for the REST service"""
        return _tpl._replace_templates(self._use_https)

    @use_https.setter
    def use_https(self, value: bool):
        self._use_https = value

    @property
    def ssl_cert(self) -> Optional[str]:
        """The path to the SSL certificate file"""
        return _tpl._replace_templates(self._ssl_cert)

    @ssl_cert.setter
    def ssl_cert(self, value: Optional[str]):
        self._ssl_cert = value

    @property
    def ssl_key(self) -> Optional[str]:
        """The path to the SSL key file"""
        return _tpl._replace_templates(self._ssl_key)

    @ssl_key.setter
    def ssl_key(self, value: Optional[str]):
        self._ssl_key = value

    @property
    def ssl_context(self) -> Optional[Tuple[Optional[str], Optional[str]]]:
        return (self._ssl_cert, self._ssl_key) if self._use_https else None

    @staticmethod
    def _configure(
        port: int = _DEFAULT_PORT,
        host: str = _DEFAULT_HOST,
        use_https: bool = _DEFAULT_USE_HTTPS,
        ssl_cert: Optional[str] = _DEFAULT_SSL_CERT,
        ssl_key: Optional[str] = _DEFAULT_SSL_KEY,
    ):
        section = RestConfig(
            port=port,
            host=host,
            use_https=use_https,
            ssl_cert=ssl_cert,
            ssl_key=ssl_key,
        )
        Config._register(section)
        return Config.unique_sections[RestConfig.name]
