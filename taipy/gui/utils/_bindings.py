from datetime import datetime
from random import random
import typing as t

from ._map_dict import _MapDict
from ..data.data_scope import _DataScopes

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Bindings:
    def __init__(self, gui: "Gui") -> None:
        self.__gui = gui
        self.__scopes = _DataScopes()

    def _bind(self, name: str, value: t.Any) -> None:
        if hasattr(self, name):
            raise ValueError(f"Variable '{name}' is already bound")
        if not name.isidentifier():
            raise ValueError(f"Variable name '{name}' is invalid")
        if isinstance(value, dict):
            setattr(self._get_data_scope(), name, _MapDict(value))
        else:
            setattr(self._get_data_scope(), name, value)
        # prop = property(self.__value_getter(name), self.__value_setter(name))
        setattr(_Bindings, name, self.__get_property(name))

    def __get_property(self, name):
        def __setter(ud: _Bindings, value: t.Any):
            if isinstance(value, dict):
                value = _MapDict(value, None)
            ud.__gui._update_var(name, value)

        def __getter(ud: _Bindings) -> t.Any:
            value = getattr(ud._get_data_scope(), name)
            if isinstance(value, _MapDict):
                return _MapDict(value._dict, lambda k, v: ud.__gui._update_var(f"{name}.{k}", v))
            else:
                return value
        return property(__getter, __setter)  # Getter, Setter

    def _set_single_client(self, value: bool) -> None:
        self.__scopes.set_single_client(value)

    def _get_single_client(self) -> bool:
        return self.__scopes.get_single_client()

    def _set_client_id(self, message: dict):
        self.__scopes._set_client_id(message.get("client_id"))

    def _get_or_create_scope(self, id: str):
        if not id:
            id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{random()}"
            self.__gui._send_ws_id(id)
        self.__scopes.create_scope(id)

    def _new_scopes(self):
        self.__scopes = _DataScopes()

    def _get_data_scope(self):
        return self.__scopes.get_scope()

    def _get_all_scopes(self):
        return self.__scopes.get_all_scopes()
