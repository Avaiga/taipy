import pytest
from taipy.gui import Gui

def test_table_on_delete_repro():
    gui = Gui()

    # The new helper must exist and be callable
    assert hasattr(gui, "_get_var_from_name")

    # Mock a variable in case Taipy uses an internal dict
    if not hasattr(gui, "_variables"):
        gui._variables = {}
    gui._variables["dummy"] = "mocked_value"

    # The helper should return the mocked value
    assert gui._get_var_from_name("dummy") == "mocked_value"

    # Finally, table_on_delete() should not raise any exception
    try:
        gui.table_on_delete(None, "dummy", {"index": 0})
    except Exception as e:
        pytest.fail(f"table_on_delete raised an unexpected error: {e}")
