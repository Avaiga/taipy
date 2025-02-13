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
import os
from unittest.mock import patch

import pytest

from taipy.common.config.config import Config
from taipy.common.config.exceptions import MissingEnvVariableError
from taipy.rest.config.rest_config import RestConfig
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_rest_config_no_values():
    assert Config.rest.port == 5000
    assert Config.rest.host == "127.0.0.1"
    assert Config.rest.use_https is False
    assert Config.rest.ssl_cert is None
    assert Config.rest.ssl_key is None

def test_rest_config_default_values():
    Config.configure_rest()
    assert Config.rest.port == RestConfig._DEFAULT_PORT
    assert Config.rest.host == RestConfig._DEFAULT_HOST
    assert Config.rest.use_https is RestConfig._DEFAULT_USE_HTTPS
    assert Config.rest.ssl_cert is RestConfig._DEFAULT_SSL_CERT
    assert Config.rest.ssl_key is RestConfig._DEFAULT_SSL_KEY

def test_rest_config_only_part_of_custom_values():
    Config.configure_rest(
        use_https=True,
        ssl_cert="cert.pem",
        ssl_key="key.pem"
    )
    assert Config.rest.port == RestConfig._DEFAULT_PORT
    assert Config.rest.host == RestConfig._DEFAULT_HOST
    assert Config.rest.use_https is True
    assert Config.rest.ssl_cert == "cert.pem"
    assert Config.rest.ssl_key == "key.pem"

def test_rest_config_custom_values_and_toml_override():
    # We override some default values with the Python API
    Config.configure_rest(
        port=8080,
        host="0.0.0.0",
    )
    assert Config.rest.port == 8080
    assert Config.rest.host == "0.0.0.0"
    assert Config.rest.use_https is RestConfig._DEFAULT_USE_HTTPS
    assert Config.rest.ssl_cert is RestConfig._DEFAULT_SSL_CERT
    assert Config.rest.ssl_key is RestConfig._DEFAULT_SSL_KEY

    # now we load a toml file
    toml_cfg = NamedTemporaryFile(
        content="""
[TAIPY]

[REST]
port = 2
host = "192.168.0.87"
use_https = "true:bool"
ssl_cert = "cert.pem"
ssl_key = "key.pem"
"""
    )
    Config.load(toml_cfg.filename)
    assert Config.rest.port == 2
    assert Config.rest.host == "192.168.0.87"
    assert Config.rest.use_https is True
    assert Config.rest.ssl_cert == "cert.pem"
    assert Config.rest.ssl_key == "key.pem"


def test_rest_config_custom_values_and_missing_env_var_override():
    #we use env variables
    Config.configure_rest(
        port="ENV[PORT]:int",
        host="ENV[HOST]",
        ssl_cert="ENV[SSL_CERT]",
        ssl_key="ENV[SSL_KEY]"
    )
    Config.rest.use_https = "ENV[USE_HTTPS]"
    with pytest.raises(MissingEnvVariableError):
        _ = Config.rest.port
    with pytest.raises(MissingEnvVariableError):
        _ = Config.rest.host
    with pytest.raises(MissingEnvVariableError):
        _ = Config.rest.use_https
    with pytest.raises(MissingEnvVariableError):
        _ = Config.rest.ssl_cert
    with pytest.raises(MissingEnvVariableError):
        _ = Config.rest.ssl_key

def test_rest_config_custom_values_and_env_var_override():
    with patch.dict(os.environ, {
        "PORT": "3",
        "HOST": "1.2.3.4",
        "USE_HTTPS": "true",
        "SSL_CERT": "cert.pem",
        "SSL_KEY": "key.pem"
    }):
        # we use env variables
        Config.configure_rest(
            port="ENV[PORT]:int",
            host="ENV[HOST]",
            use_https="ENV[USE_HTTPS]:bool",
            ssl_cert="ENV[SSL_CERT]",
            ssl_key="ENV[SSL_KEY]"
        )
        assert Config.rest.port == 3
        assert Config.rest.host == "1.2.3.4"
        assert Config.rest.use_https is True
        assert Config.rest.ssl_cert == "cert.pem"
        assert Config.rest.ssl_key == "key.pem"


def test_rest_config_copy():
    rest_config = Config.configure_rest(
        port=8080, host="0.0.0.0", use_https=True, ssl_cert="cert.pem", ssl_key="key.pem"
    )
    rest_config_copy = rest_config.__copy__()

    assert rest_config_copy.port == 8080
    assert rest_config_copy.host == "0.0.0.0"
    assert rest_config_copy.use_https is True
    assert rest_config_copy.ssl_cert == "cert.pem"
    assert rest_config_copy.ssl_key == "key.pem"

    # Ensure it's a deep copy
    rest_config_copy.port = 9090
    assert rest_config.port == 8080


def test_rest_default_config_is_valid():
    issues = Config.check()

    assert len(issues.errors) == 0
    assert len(issues.warnings) == 0
    assert len(issues.infos) == 0


def test_rest_config_checker_valid_config():
    Config.configure_rest(port=8080, host="0.0.0.0", use_https=True, ssl_cert="cert.pem", ssl_key="key.pem")
    issues = Config.check()

    assert len(issues.errors) == 0
    assert len(issues.warnings) == 0
    assert len(issues.infos) == 0


def test_rest_config_checker_invalid_port_and_host():
    Config.configure_rest(port=70000, host="")  # Invalid port and host
    with pytest.raises(SystemExit):
        Config.check()

    issues = Config._collector
    assert len(issues.errors) == 2
    assert len(issues.warnings) == 0
    assert len(issues.infos) == 0
    assert "port" in issues.errors[0].field
    assert "host" in issues.errors[1].field


def test_rest_config_checker_https_missing_cert_and_key():
    Config.configure_rest(use_https=True)  # Missing ssl_cert and ssl_key
    with pytest.raises(SystemExit):
        Config.check()

    issues = Config._collector
    assert len(issues.errors) == 2
    assert len(issues.warnings) == 0
    assert len(issues.infos) == 0
    assert "ssl_cert" in issues.errors[0].field
    assert "ssl_key" in issues.errors[1].field


def test_rest_config_checker_https_invalid_cert_and_key():
    Config.configure_rest(use_https=True, ssl_cert=123, ssl_key=456)  # Invalid types for ssl_cert and ssl_key
    with pytest.raises(SystemExit):
        Config.check()

    issues = Config._collector
    assert len(issues.errors) == 2
    assert len(issues.warnings) == 0
    assert len(issues.infos) == 0
    assert "ssl_cert" in issues.errors[0].field
    assert "ssl_key" in issues.errors[1].field
