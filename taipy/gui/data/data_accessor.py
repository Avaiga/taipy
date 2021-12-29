import inspect
from types import NoneType
import typing as t
import warnings
from abc import ABC, abstractmethod

from ..utils import _get_dict_value
from .data_format import DataFormat

if t.TYPE_CHECKING:
    from ..gui import Gui


class DataAccessor(ABC):

    _WS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    @abstractmethod
    def get_supported_classes() -> t.Union[t.Type, t.List[t.Type], t.Tuple[t.Type]]:
        pass

    @abstractmethod
    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        pass

    @abstractmethod
    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        pass

    @abstractmethod
    def get_data(
        self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
        pass

    @abstractmethod
    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        pass


class _InvalidDataAccessor(DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.Union[t.Type, t.List[t.Type], t.Tuple[t.Type]]:
        return NoneType

    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        return None

    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return False

    def get_data(
        self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
        return {}

    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return {}


class _DataAccessors(object):
    def __init__(self) -> None:
        self.__access_4_type: t.Dict[str, DataAccessor] = {}

        self.__invalid_data_accessor = _InvalidDataAccessor()

        self.__data_format = DataFormat.JSON

        from .pandas_data_accessor import PandasDataAccessor

        self._register(PandasDataAccessor)

    def _register(self, cls: t.Type[DataAccessor]) -> None:
        if inspect.isclass(cls):
            if issubclass(cls, DataAccessor):
                names = cls.get_supported_classes()
                if not names:
                    raise TypeError(f"method {cls.__name__}.get_supported_classes returned an invalid value")
                if names and not isinstance(names, (t.List, t.Tuple)):  # type: ignore
                    names = [
                        names,  # type: ignore
                    ]
                for name in names:
                    if inspect.isclass(cls):
                        self.__access_4_type[name] = cls()  # type: ignore
                    else:
                        raise TypeError(f"{name.__name__} is not a class")
            else:
                raise TypeError(f"Class {cls.__name__} is not a subclass of DataAccessAbstract")
        else:
            raise AttributeError("The argument of 'DataAccessRegistry.register' should be a class")

    def __get_instance(self, value: t.Any) -> DataAccessor:  # type: ignore
        try:
            return self.__access_4_type[value.__class__]
        except Exception:
            warnings.warn(f"Can't find Data Accessor for type {value.__class__}")
        return self.__invalid_data_accessor

    def _cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        inst = _get_dict_value(self.__access_4_type, value.__class__)
        return inst.cast_string_value(var_name, value) if inst else value

    def _is_data_access(self, var_name: str, value: t.Any) -> bool:
        inst = _get_dict_value(self.__access_4_type, value.__class__)
        return inst and inst.is_data_access(var_name, value)

    def _get_data(self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return self.__get_instance(value).get_data(guiApp, var_name, value, payload, self.__data_format)

    def _get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return self.__get_instance(value).get_col_types(var_name, value)

    def _set_data_format(self, data_format: DataFormat):
        self.__data_format = data_format
