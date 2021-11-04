import pytest

from taipy.gui import Gui
from taipy.gui.renderers.builder import Builder


def test_cleanup():
    Builder._reset_key()


@pytest.fixture(scope="function")
def gui():
    yield Gui(__name__)
    # Delete Gui instance and state of some class after each test
    test_cleanup()
    del Gui._instances[Gui]
