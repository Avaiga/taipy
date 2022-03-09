import pathlib
import tempfile

from taipy.gui import Gui
from taipy.gui.utils import _get_non_existent_file_path


def test_empty_file_name(gui: Gui, helpers):
    assert _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").name


def test_non_existent_file(gui: Gui, helpers):
    assert not _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").exists()


def test_existent_file(gui: Gui, helpers):
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    with open(file_path, "w") as file_handler:
        file_handler.write("hello")
    assert file_path.exists()
    file_stem = file_path.stem.split(".", 1)[0]
    file_suffix = file_path.suffixes[-1]
    index = int(file_path.suffixes[0][1:]) if len(file_path.suffixes) > 1 else -1
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    assert file_path.name == f"{file_stem}.{index + 1}{file_suffix}"
    with open(file_path, "w") as file_handler:
        file_handler.write("hello 2")
    assert file_path.exists()
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    assert file_path.name == f"{file_stem}.{index + 2}{file_suffix}"
