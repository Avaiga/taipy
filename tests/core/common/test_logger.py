import os
import pathlib
from io import StringIO
from unittest import TestCase, mock
from unittest.mock import patch

from taipy.core.common._taipy_logger import _TaipyLogger


class TestTaipyLogger(TestCase):
    def test_taipy_logger(self):
        _TaipyLogger._get_logger().error("foo")
        _TaipyLogger._get_logger().warning("bar")
        _TaipyLogger._get_logger().info("baz")
        _TaipyLogger._get_logger().debug("qux")

    def test_taipy_logger_configured_by_file(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "logger.conf")
        with mock.patch.dict(os.environ, {"TAIPY_LOGGER_CONFIG_PATH": path}):
            _TaipyLogger._get_logger().error("foo")
            _TaipyLogger._get_logger().warning("bar")
            _TaipyLogger._get_logger().info("baz")
            _TaipyLogger._get_logger().debug("qux")
