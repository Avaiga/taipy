from abc import ABC, abstractmethod
import typing as t
import warnings
import inspect

from ..utils import _get_dict_value


class DataAccessor(ABC):

    _WS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    @abstractmethod
    def get_supported_classes() -> t.Union[t.Callable, t.List[t.Callable], t.Tuple[t.Callable]]:
        return None

    @abstractmethod
    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        return value

    @abstractmethod
    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return False

    @abstractmethod
    def get_data(self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return payload

    @abstractmethod
    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return {}


class _DataAccessors(object):
    def __init__(self) -> None:
        self.__access_4_type: t.Dict[str, DataAccessor] = {}

        from .pandas_data_accessor import PandasDataAccessor

        self._register(PandasDataAccessor)

    def _register(self, cls: t.Type[DataAccessor]) -> None:
        if inspect.isclass(cls):
            if issubclass(cls, DataAccessor):
                names = cls.get_supported_classes()
                if not names:
                    raise TypeError(f"method {cls.__name__}.get_supported_classes returned an invalid value")
                if names and not isinstance(names, (t.List, t.Tuple)):
                    names = [
                        names,
                    ]
                for name in names:
                    if inspect.isclass(cls):
                        self.__access_4_type[name] = cls()
                    else:
                        raise TypeError(f"{name.__name__} is not a class")
            else:
                raise TypeError(f"Class {cls.__name__} is not a subclass of DataAccessAbstract")
        else:
            raise AttributeError(f"The argument of 'DataAccessRegistry.register' should be a class")

    def __get_instance(self, value: t.Any) -> DataAccessor:
        try:
            return self.__access_4_type[value.__class__]
        except Exception as e:
            warnings.warn(f"Can't find Data Accessor for type {value.__class__}")

    def _cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        inst = _get_dict_value(self.__access_4_type, value.__class__)
        return inst.cast_string_value(var_name, value) if inst else value

    def _is_data_access(self, var_name: str, value: t.Any) -> bool:
        inst = _get_dict_value(self.__access_4_type, value.__class__)
        return inst and inst.is_data_access(var_name, value)

    def _get_data(self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return self.__get_instance(value).get_data(var_name, value, payload)

    def _get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return self.__get_instance(value).get_col_types(var_name, value)
