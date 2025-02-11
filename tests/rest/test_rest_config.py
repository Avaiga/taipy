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

from taipy.common.config._config import _Config
from taipy.common.config.checker.issue_collector import IssueCollector
from taipy.common.config.config import Config
from taipy.rest.config.rest_checker import _RestConfigChecker
from taipy.rest.config.rest_config import RestConfig


def test_rest_config_default_values():
    assert rest_config.port == 5000
    assert rest_config.host == "127.0.0.1"
    assert rest_config.use_https is False
    assert rest_config.ssl_cert is None
    assert rest_config.ssl_key is None


def test_rest_config_custom_values():
    rest_config = Config.configure_rest(
        port=8080, host="0.0.0.0", use_https=True, ssl_cert="cert.pem", ssl_key="key.pem"
    )

    assert rest_config.port == 8080
    assert rest_config.host == "0.0.0.0"
    assert rest_config.use_https is True
    assert rest_config.ssl_cert == "cert.pem"
    assert rest_config.ssl_key == "key.pem"


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


def test_rest_config_checker_valid_config():
    config = _Config()
    collector = IssueCollector()
    rest_config = RestConfig()
    rest_config._configure(port=8080, host="0.0.0.0", use_https=True, ssl_cert="cert.pem", ssl_key="key.pem")

    config._sections[RestConfig.name] = {"test_rest_config": rest_config}
    checker = _RestConfigChecker(config, collector)
    issues = checker._check()

    assert len(issues.errors) == 0
    assert len(issues.warnings) == 0


def test_rest_config_checker_invalid_port():
    config = _Config()
    collector = IssueCollector()
    rest_config = RestConfig()
    rest_config._configure(port=70000)  # Invalid port

    config._sections[RestConfig.name] = {"test_rest_config": rest_config}
    checker = _RestConfigChecker(config, collector)
    issues = checker._check()

    assert len(issues.errors) == 1
    assert "port" in issues.errors[0].field


def test_rest_config_checker_invalid_host():
    config = _Config()
    collector = IssueCollector()
    rest_config = RestConfig()
    rest_config._configure(host="")  # Invalid host

    config._sections[RestConfig.name] = {"test_rest_config": rest_config}
    checker = _RestConfigChecker(config, collector)
    issues = checker._check()

    assert len(issues.errors) == 1
    assert "host" in issues.errors[0].field


def test_rest_config_checker_https_missing_cert_and_key():
    config = _Config()
    collector = IssueCollector()
    rest_config = RestConfig()
    rest_config._configure(use_https=True)  # Missing ssl_cert and ssl_key

    config._sections[RestConfig.name] = {"test_rest_config": rest_config}
    checker = _RestConfigChecker(config, collector)
    issues = checker._check()

    assert len(issues.errors) == 1
    assert "ssl_cert/ssl_key" in issues.errors[0].field


def test_rest_config_checker_https_invalid_cert_and_key():
    config = _Config()
    collector = IssueCollector()
    rest_config = RestConfig()
    rest_config._configure(use_https=True, ssl_cert=123, ssl_key=456)  # Invalid types for ssl_cert and ssl_key

    config._sections[RestConfig.name] = {"test_rest_config": rest_config}
    checker = _RestConfigChecker(config, collector)
    issues = checker._check()

    assert len(issues.errors) == 1
    assert "ssl_cert/ssl_key" in issues.errors[0].field
