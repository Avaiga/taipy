import logging

import pytest

from taipy.gui import Gui


def test_handle_invalid_data_no_callback():
    gui = Gui()  # No callback set
    result = gui.handle_invalid_data("invalid_data")

    assert result is None  # Should return None


def test_handle_invalid_data_callback_returns_none():
    def callback(value):
        return None  # Simulates a failed transformation

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data("invalid_data")
    assert result is None  # Transformation should result in None


def test_handle_invalid_data_callback_transforms_data():
    def callback(value):
        return "valid_data"  # Successful transformation

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data("invalid_data")
    assert result == "valid_data"  # Data transformed correctly


def test_handle_invalid_data_callback_raises_exception(capfd, monkeypatch):
    def callback(value):
        raise ValueError("Transformation error")  # Simulate an error

    def mock_warn(message: str):
        import sys

        logging.warning(message)  # Ensure the warning goes to stderr.

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    # Patch the _warn function inside the taipy.gui._warnings module.
    monkeypatch.setattr("taipy.gui._warnings._warn", mock_warn)

    result = gui.handle_invalid_data("invalid_data")
    out, _ = capfd.readouterr()

    assert result is None  # Should return None on exception
    assert "Error transforming data: Transformation error"


@pytest.mark.parametrize("input_data", [None, 123, [], {}, set()])
def test_handle_invalid_data_with_various_inputs(input_data):
    def callback(value):
        return "valid_data"  # Always returns valid data

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data(input_data)
    assert result == "valid_data"  # Transformed correctly for all inputs
