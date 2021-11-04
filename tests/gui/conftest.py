import pytest

from taipy.gui import Gui

from .helpers import Helpers


@pytest.fixture(scope="function")
def gui(helpers):
    yield Gui(__name__)
    # Delete Gui instance and state of some classes after each test
    helpers.test_cleanup()


@pytest.fixture
def helpers():
    return Helpers
