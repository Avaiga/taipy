import pytest
from taipy.gui import Gui


@pytest.fixture(scope="function")
def gui():
    yield Gui(__name__)
    # Delete Gui instance and state of some class after each test
    Gui._test_cleanup()
    del Gui._instances[Gui]
