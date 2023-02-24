# Copyright 2023 Avaiga Private Limited
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
from unittest import mock
from unittest.mock import MagicMock

import pytest

from src.taipy.config import Config
from src.taipy.config.checker._checker import _Checker
from src.taipy.config.checker.issue_collector import IssueCollector
from src.taipy.config.global_app.global_app_config import GlobalAppConfig
from tests.config.utils.checker_for_tests import CheckerForTest


class TestChecker:
    def test_check(self, caplog):
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.global_config.clean_entities_enabled = True
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.global_config.clean_entities_enabled = False
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.global_config.clean_entities_enabled = "foo"
        with pytest.raises(SystemExit):
            Config.check()
        expected_error_message = (
            "`clean_entities_enabled` field of GlobalAppConfig must be populated with a boolean"
            ' value. Current value of property `clean_entities_enabled` is "foo".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.errors) == 1

        caplog.clear()

        Config.global_config.clean_entities_enabled = GlobalAppConfig._CLEAN_ENTITIES_ENABLED_TEMPLATE
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        with mock.patch.dict(os.environ, {"FOO": "true"}):
            Config.global_config.clean_entities_enabled = "ENV[FOO]"
            Config._collector = IssueCollector()
            Config.check()
            assert len(Config._collector.errors) == 0

        with mock.patch.dict(os.environ, {"FOO": "foo"}):
            Config.global_config.clean_entities_enabled = "ENV[FOO]"
            Config._collector = IssueCollector()
            with pytest.raises(SystemExit):
                Config.check()
            expected_error_message = (
                "`clean_entities_enabled` field of GlobalAppConfig must be populated with a"
                ' boolean value. Current value of property `clean_entities_enabled` is "ENV[FOO]".'
            )
            assert expected_error_message in caplog.text
            assert len(Config._collector.errors) == 1

    def test_register_checker(self):
        checker = CheckerForTest
        checker._check = MagicMock()
        _Checker.add_checker(checker)
        Config.check()
        checker._check.assert_called_once()
