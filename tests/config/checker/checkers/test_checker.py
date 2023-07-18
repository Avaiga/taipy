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

from src.taipy.config import Config
from src.taipy.config.checker._checker import _Checker
from src.taipy.config.checker.issue_collector import IssueCollector
from tests.config.utils.checker_for_tests import CheckerForTest


def test_register_checker():
    checker = CheckerForTest
    checker._check = MagicMock()
    _Checker.add_checker(checker)
    Config.check()
    checker._check.assert_called_once()
