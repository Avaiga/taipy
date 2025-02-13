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
from typing import Any, Dict, Optional, Tuple

from taipy.common.config import UniqueSection
from taipy.common.config._config import _Config
from taipy.common.config.common._template_handler import _TemplateHandler as _tpl
from taipy.common.config.config import Config


class RestConfig(UniqueSection):
    """Configuration parameters for running the `Rest^` service"""

    name: str = "REST"

    _PORT_KEY: str = "port"
    _DEFAULT_PORT: int = 5000
    _HOST_KEY: str = "host"
    _DEFAULT_HOST: str = "127.0.0.1"
    _USE_HTTPS_KEY: str = "use_https"
    _DEFAULT_USE_HTTPS: bool = False
    _SSL_CERT_KEY: str = "ssl_cert"
    _DEFAULT_SSL_CERT: Optional[str] = None
    _SSL_KEY_KEY: str = "ssl_key"
    _DEFAULT_SSL_KEY: Optional[str] = None

    def __init__(
        self,
        port: Optional[int] = _DEFAULT_PORT,
        host: Optional[str] = _DEFAULT_HOST,
        use_https: Optional[bool] = _DEFAULT_USE_HTTPS,
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
            self._port,
            self._host,
            self._use_https,
            self._ssl_cert,
            self._ssl_key,
            **copy(self._properties),
        )

    def _clean(self):
        self._port = self._DEFAULT_PORT
        self._host = self._DEFAULT_HOST
        self._use_https = self._DEFAULT_USE_HTTPS
        self._ssl_cert = self._DEFAULT_SSL_CERT
        self._ssl_key = self._DEFAULT_SSL_KEY
        self._properties.clear()

    def _update(self, config_as_dict: Dict, default_section=None):
        self._port = config_as_dict.pop(self._PORT_KEY, self.port)
        self._host = config_as_dict.pop(self._HOST_KEY, self.host)
        self._use_https = config_as_dict.pop(self._USE_HTTPS_KEY, self.use_https)
        self._ssl_cert = config_as_dict.pop(self._SSL_CERT_KEY, self.ssl_cert)
        self._ssl_key = config_as_dict.pop(self._SSL_KEY_KEY, self.ssl_key)
        self._properties.update(config_as_dict)

    def _to_dict(self):
        as_dict = {
            key: value
            for key, value in {
                self._PORT_KEY: self._port,
                self._HOST_KEY: self._host,
                self._USE_HTTPS_KEY: self._use_https,
                self._SSL_CERT_KEY: self._ssl_cert,
                self._SSL_KEY_KEY: self._ssl_key
            }.items()
            if value is not None
        }
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id=None, config: Optional[_Config] = None):
        port = as_dict.pop(cls._PORT_KEY, None)
        host = as_dict.pop(cls._HOST_KEY, None)
        use_https = as_dict.pop(cls._USE_HTTPS_KEY, None)
        ssl_cert = as_dict.pop(cls._SSL_CERT_KEY, None)
        ssl_key = as_dict.pop(cls._SSL_KEY_KEY, None)
        return RestConfig(port, host, use_https, ssl_cert, ssl_key, **as_dict)

    @classmethod
    def default_config(cls) -> "RestConfig":
        """Return a RestConfig with all the default values.

        Returns:
            The default rest configuration.
        """
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
        """The ssl_context as a tuple of the certificate and the key files"""
        return (self.ssl_cert, self.ssl_key) if self.use_https else None

    @staticmethod
    def _configure_rest(
        port: Optional[int] = None,
        host: Optional[str] = None,
        use_https: Optional[bool] = None,
        ssl_cert: Optional[str] = None,
        ssl_key: Optional[str] = None,
        **properties
    ) -> "RestConfig":
        """Configure the Rest service.

        Arguments:
            port (Optional[int]): The port on which the REST service will be running
            host (Optional[str]): The host on which the REST service will be running
            use_https (Optional[bool]): Whether to use HTTPS for the REST service
            ssl_cert (Optional[str]): The path to the SSL certificate file
            ssl_key (Optional[str]): The path to the SSL key file
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments configure the behavior of the `Rest^` service.

        Returns:
            The Rest configuration.
        """
        section = RestConfig(
            port=port,
            host=host,
            use_https=use_https,
            ssl_cert=ssl_cert,
            ssl_key=ssl_key,
            **properties
        )
        Config._register(section)
        return Config.unique_sections[RestConfig.name]
