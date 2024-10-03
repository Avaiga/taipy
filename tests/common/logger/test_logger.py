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

import os
import pathlib
from unittest import TestCase, mock

from taipy.common.logger._taipy_logger import _TaipyLogger


class TestTaipyLogger(TestCase):
    def test_taipy_logger(self):
        _TaipyLogger._get_logger().info("baz")
        _TaipyLogger._get_logger().debug("qux")

    def test_taipy_logger_configured_by_file(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "logger.conf")
        with mock.patch.dict(os.environ, {"TAIPY_LOGGER_CONFIG_PATH": path}):
            _TaipyLogger._get_logger().info("baz")
            _TaipyLogger._get_logger().debug("qux")
