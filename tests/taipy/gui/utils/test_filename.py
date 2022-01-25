import pytest
import tempfile
from taipy.gui import Gui
from taipy.gui.utils import _get_non_existent_file_path
import pathlib


def test_empty_file_name(gui: Gui, helpers):
    assert _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").name


def test_non_existent_file(gui: Gui, helpers):
    assert not _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").exists()
