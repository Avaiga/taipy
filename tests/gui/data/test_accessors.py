import typing as t
from unittest.mock import Mock

import pytest

from taipy.gui import Gui
from taipy.gui.data.data_accessor import (
    _DataAccessor,
    _DataAccessors,
    _InvalidDataAccessor,
)
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.utils.types import _TaipyData


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
        return {"value": 2 * int(value)}

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:  # type: ignore
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


class MyStringAccessor(_DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return [str]

    def get_data(
        self,
        var_name: str,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
    ) -> t.Dict[str, t.Any]:
        return {"value": value}

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:
        return {}

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        return value

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return payload

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return payload

    def on_add(
        self,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        new_row: t.Optional[t.List[t.Any]] = None,
    ) -> t.Optional[t.Any]:
        return new_row

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        return str(value)


class NoSupportedClassAccessor(_DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return []

    def get_data(
        self,
        var_name: str,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
    ) -> t.Dict[str, t.Any]:
        return {}

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:
        return {}

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        return value

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return value

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return value

    def on_add(
        self,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        new_row: t.Optional[t.List[t.Any]] = None,
    ) -> t.Optional[t.Any]:
        return value

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        return None


class NotInstantiableAccessor(_DataAccessor):
    def __init__(self, gui: Gui):
        raise RuntimeError("boom")

    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return [float]

    def get_data(
        self,
        var_name: str,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
    ) -> t.Dict[str, t.Any]:
        return {}

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:
        return {}

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        return value

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return value

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return value

    def on_add(
        self,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        new_row: t.Optional[t.List[t.Any]] = None,
    ) -> t.Optional[t.Any]:
        return value

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        return None


class Parent:
    pass


class Child(Parent):
    pass


class ParentAccessor(_DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return [Parent]

    def get_data(
        self,
        var_name: str,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
    ) -> t.Dict[str, t.Any]:
        return {"value": "parent"}

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:
        return {}

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        return ["parent", value]

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return {"edited": value, "payload": payload}

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return {"deleted": value, "payload": payload}

    def on_add(
        self,
        value: t.Any,
        payload: t.Dict[str, t.Any],
        new_row: t.Optional[t.List[t.Any]] = None,
    ) -> t.Optional[t.Any]:
        return {"added": value, "payload": payload, "new_row": new_row}

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        return f"{var_name}:{value.__class__.__name__}"


def mock_taipy_data(value):
    """Helper to mock _TaipyData objects."""
    mock_data = Mock(spec=_TaipyData)
    mock_data.get.return_value = value
    return mock_data


def test_custom_accessor(gui: Gui):
    """Test if get_data() uses the correct accessor."""
    data_accessors = _DataAccessors(gui)
    data = mock_taipy_data(123)

    # Testing when accessor is not registered
    data_accessor = data_accessors._get_instance(mock_taipy_data)  # type: ignore
    assert isinstance(
        data_accessor, _InvalidDataAccessor
    ), f"Expected _InvalidDataAccessor but got {type(data_accessor)}"
    result = data_accessors.get_data("var_name", data, {})
    assert result == {}

    # Testing when accessor is registered
    data_accessors._register(MyDataAccessor)

    result = data_accessors.get_data("var_name", data, {})
    assert isinstance(result, dict)
    assert result["value"] == 246

    data_accessors._unregister(MyDataAccessor)


def test_register_validates_arguments(gui: Gui):
    data_accessors = _DataAccessors(gui)

    with pytest.raises(AttributeError, match="should be a class"):
        data_accessors._register(123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="is not a subclass of DataAccessor"):
        data_accessors._register(str)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="returned an invalid value"):
        data_accessors._register(NoSupportedClassAccessor)


def test_register_non_instantiable_accessor_raises(gui: Gui):
    data_accessors = _DataAccessors(gui)

    with pytest.raises(TypeError, match="cannot be instantiated"):
        data_accessors._register(NotInstantiableAccessor)


def test_get_instance_uses_converted_unsupported_data(gui: Gui, monkeypatch):
    data_accessors = _DataAccessors(gui)
    data_accessors._register(MyStringAccessor)

    def _converter(value: t.Any):
        return "converted" if value == 10 else None

    monkeypatch.setattr(Gui, "_convert_unsupported_data", staticmethod(_converter))
    accessor = data_accessors._get_instance(mock_taipy_data(10))
    assert isinstance(accessor, MyStringAccessor)
    assert data_accessors.get_data("var_name", mock_taipy_data(10), {}) == {"value": 10}


def test_get_instance_falls_back_to_isinstance_and_caches(gui: Gui, monkeypatch):
    data_accessors = _DataAccessors(gui)
    data_accessors._register(ParentAccessor)

    monkeypatch.setattr(Gui, "_convert_unsupported_data", staticmethod(lambda _value: None))
    value = Child()
    first = data_accessors._get_instance(mock_taipy_data(value))
    second = data_accessors._get_instance(mock_taipy_data(value))
    assert isinstance(first, ParentAccessor)
    assert first is second


def test_get_instance_warns_and_returns_invalid_for_unsupported_type(gui: Gui, monkeypatch):
    data_accessors = _DataAccessors(gui)
    warnings: t.List[str] = []

    monkeypatch.setattr(Gui, "_convert_unsupported_data", staticmethod(lambda _value: None))
    monkeypatch.setattr("taipy.gui.data.data_accessor._warn", lambda message: warnings.append(message))
    accessor = data_accessors._get_instance(mock_taipy_data(object()))
    assert isinstance(accessor, _InvalidDataAccessor)
    assert len(warnings) == 1
    assert "Can't find Data Accessor for type" in warnings[0]


def test_data_accessors_delegate_methods(gui: Gui):
    data_accessors = _DataAccessors(gui)
    data_accessors._register(MyDataAccessor)
    data_accessors.set_data_format(_DataFormat.APACHE_ARROW)

    data_wrapper = mock_taipy_data(5)
    assert data_accessors.get_data("x", data_wrapper, {}) == {"value": 10}

    data_accessors._register(ParentAccessor)
    value = Child()
    edited = data_accessors.on_edit(value, {"k": 1})
    deleted = data_accessors.on_delete(value, {"k": 2})
    added = data_accessors.on_add(value, {"k": 3}, [1, 2])
    assert edited == {"edited": value, "payload": {"k": 1}}
    assert deleted == {"deleted": value, "payload": {"k": 2}}
    assert added == {"added": value, "payload": {"k": 3}, "new_row": [1, 2]}

    string_data = mock_taipy_data("abc")
    data_accessors._register(MyStringAccessor)
    assert data_accessors.to_csv("name", string_data) == "abc"
    assert data_accessors.to_pandas(string_data) == "abc"


def test_get_instance_returns_invalid_for_none(gui: Gui):
    data_accessors = _DataAccessors(gui)
    accessor = data_accessors._get_instance(mock_taipy_data(None))
    assert isinstance(accessor, _InvalidDataAccessor)
