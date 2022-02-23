import os
import pathlib
from io import StringIO
from unittest import TestCase, mock
from unittest.mock import patch

from taipy.core.common.logger import TaipyLogger


class TestTaipyLogger(TestCase):
    def test_taipy_logger(self):
        TaipyLogger.get_logger().error("foo")
        TaipyLogger.get_logger().warning("bar")
        TaipyLogger.get_logger().info("baz")
        TaipyLogger.get_logger().debug("qux")

    def test_taipy_logger_configured_by_file(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "logger.conf")
        with mock.patch.dict(os.environ, {"TAIPY_LOGGER_CONFIG_PATH": path}):
            TaipyLogger.get_logger().error("foo")
            TaipyLogger.get_logger().warning("bar")
            TaipyLogger.get_logger().info("baz")
            TaipyLogger.get_logger().debug("qux")
