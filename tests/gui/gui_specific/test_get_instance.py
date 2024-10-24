from unittest.mock import MagicMock
from taipy.gui import Gui
from taipy.gui.data.data_accessor import (
    _DataAccessor,
    _DataAccessors,
    _InvalidDataAccessor,
)
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.utils.types import _TaipyData
from unittest.mock import Mock
import typing as t


def mock_taipy_data(value):
    """Helper to mock _TaipyData objects."""
    mock_data = Mock(spec=_TaipyData)
    mock_data.get.return_value = value
    return mock_data


class MyDataAccessor(_DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return [int]

    def get_data(
        self,
        var_name: str,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
    ) -> t.Dict[str, t.Any]:
        return {"value": value}

    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:  # type: ignore
        pass

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        pass

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        pass

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        pass

    def on_add(
        self,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        new_row: t.Optional[t.List[t.Any]] = None,
    ) -> t.Optional[t.Any]:
        pass

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        pass


def test_get_data_with_valid_data(gui: Gui):
    """Test if get_data() returns the correct accessor for valid data."""
    data_accessors = _DataAccessors(gui)
    data_accessors._DataAccessors__access_4_type = {int: Mock(get_data=lambda *args: "valid_data")}  # type: ignore
    result = data_accessors.get_data("var_name", mock_taipy_data(123), {})

    assert result == "valid_data"


def test_get_data_with_invalid_data(gui: Gui):
    """Test if get_data() handles invalid data correctly."""
    data_accessors = _DataAccessors(gui)
    gui._handle_invalid_data = lambda x: None  # type: ignore
    mock_taipy_data = MagicMock()
    mock_taipy_data.get.return_value = "invalid_data"
    instance = data_accessors._DataAccessors__get_instance(mock_taipy_data)  # type: ignore
    assert isinstance(
        instance, _InvalidDataAccessor
    ), f"Expected _InvalidDataAccessor but got {type(instance)}"
    result = data_accessors.get_data("var_name", mock_taipy_data, {})
    print(f"Result from get_data: {result}")

    assert result == {}, f"Expected {{}} but got {result}"


def test_get_data_transformation_successful(gui: Gui):
    """Test if get_data() transforms invalid data correctly when a callback is set."""
    data_accessors = _DataAccessors(gui)
    gui.handle_invalid_data = lambda x: 123  # type: ignore
    data_accessors._DataAccessors__access_4_type = {int: Mock(get_data=lambda *args: "valid_data")}  # type: ignore
    mock_data = mock_taipy_data(123)
    result = data_accessors.get_data("var_name", mock_data, {})
    
    assert result == "valid_data", f"Expected 'valid_data' but got {result}"
