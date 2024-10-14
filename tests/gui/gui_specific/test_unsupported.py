import pytest

from taipy.gui import Gui


def test_handle_invalid_data_no_callback(capfd):
    gui = Gui()  # No callback set
    result = gui.handle_invalid_data("invalid_data")

    out, _ = capfd.readouterr()
    assert result is None  # Should return None
    assert "Unsupported data type encountered" in out  # Correct message logged


def test_handle_invalid_data_callback_returns_none(capfd):
    def callback(value):
        return None  # Simulates a failed transformation

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data("invalid_data")
    out, _ = capfd.readouterr()

    assert result is None  # Transformation should result in None
    assert out == ""  # No output expected


def test_handle_invalid_data_callback_transforms_data():
    def callback(value):
        return "valid_data"  # Successful transformation

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data("invalid_data")
    assert result == "valid_data"  # Data transformed correctly


def test_handle_invalid_data_callback_raises_exception(capfd):
    def callback(value):
        raise ValueError("Transformation error")  # Simulate an error

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data("invalid_data")
    out, _ = capfd.readouterr()

    assert result is None  # Should return None on exception
    assert (
        "Error transforming data: Transformation error" in out
    )  # Error message logged


@pytest.mark.parametrize("input_data", [None, 123, [], {}, set()])
def test_handle_invalid_data_with_various_inputs(input_data):
    def callback(value):
        return "valid_data"  # Always returns valid data

    gui = Gui()
    gui.on_invalid_data = callback  # Set the callback

    result = gui.handle_invalid_data(input_data)
    assert result == "valid_data"  # Transformed correctly for all inputs
