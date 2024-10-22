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

import logging
from unittest import mock

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue import Issue
from taipy.common.config.checker.issue_collector import IssueCollector


class MyCustomChecker(_ConfigChecker):
    def _check(self) -> IssueCollector:  # type: ignore
        pass


def test__error():
    with mock.patch.object(logging.Logger, "error"):
        collector = IssueCollector()
        assert len(collector.all) == 0
        _ConfigChecker(_Config(), collector)._error("field", 17, "my message")
        assert len(collector.all) == 1
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert collector.errors[0] == Issue(IssueCollector._ERROR_LEVEL, "field", 17, "my message", "_ConfigChecker")

        MyCustomChecker(_Config(), collector)._error("foo", "bar", "baz")
        assert len(collector.all) == 2
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert collector.errors[0] == Issue(IssueCollector._ERROR_LEVEL, "field", 17, "my message", "_ConfigChecker")
        assert collector.errors[1] == Issue(IssueCollector._ERROR_LEVEL, "foo", "bar", "baz", "MyCustomChecker")


def test__warning():
    collector = IssueCollector()
    assert len(collector.all) == 0
    _ConfigChecker(_Config(), collector)._warning("field", 17, "my message")
    assert len(collector.all) == 1
    assert len(collector.warnings) == 1
    assert len(collector.errors) == 0
    assert len(collector.infos) == 0
    assert collector.warnings[0] == Issue(IssueCollector._WARNING_LEVEL, "field", 17, "my message", "_ConfigChecker")

    MyCustomChecker(_Config(), collector)._warning("foo", "bar", "baz")
    assert len(collector.all) == 2
    assert len(collector.warnings) == 2
    assert len(collector.errors) == 0
    assert len(collector.infos) == 0
    assert collector.warnings[0] == Issue(IssueCollector._WARNING_LEVEL, "field", 17, "my message", "_ConfigChecker")
    assert collector.warnings[1] == Issue(IssueCollector._WARNING_LEVEL, "foo", "bar", "baz", "MyCustomChecker")


def test__info():
    collector = IssueCollector()
    assert len(collector.all) == 0
    _ConfigChecker(_Config(), collector)._info("field", 17, "my message")
    assert len(collector.all) == 1
    assert len(collector.infos) == 1
    assert len(collector.errors) == 0
    assert len(collector.warnings) == 0
    assert collector.infos[0] == Issue(IssueCollector._INFO_LEVEL, "field", 17, "my message", "_ConfigChecker")

    MyCustomChecker(_Config(), collector)._info("foo", "bar", "baz")
    assert len(collector.all) == 2
    assert len(collector.infos) == 2
    assert len(collector.errors) == 0
    assert len(collector.warnings) == 0
    assert collector.infos[0] == Issue(IssueCollector._INFO_LEVEL, "field", 17, "my message", "_ConfigChecker")
    assert collector.infos[1] == Issue(IssueCollector._INFO_LEVEL, "foo", "bar", "baz", "MyCustomChecker")
