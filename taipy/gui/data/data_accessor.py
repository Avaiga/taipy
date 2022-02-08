import inspect
import typing as t
import warnings
from abc import ABC, abstractmethod

from .data_format import DataFormat

if t.TYPE_CHECKING:
    from ..gui import Gui


class DataAccessor(ABC):

    _WS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    @abstractmethod
    def get_supported_classes() -> t.Union[str, t.List[str], t.Tuple[str]]:
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
    def get_supported_classes() -> t.Union[str, t.List[str], t.Tuple[str]]:
        return str(type(None))

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
                # check existence
                inst: t.Optional[DataAccessor] = None
                for name in names:
                    inst = self.__access_4_type.get(name)
                    if inst:
                        break
                if not inst:
                    try:
                        inst = cls()
                    except Exception as e:
                        raise TypeError(f"Class {cls.__name__} cannot be instanciated") from e
                if inst:
                    for name in names:
                        self.__access_4_type[name] = inst  # type: ignore
            else:
                raise TypeError(f"Class {cls.__name__} is not a subclass of DataAccessor")
        else:
            raise AttributeError("The argument of 'DataAccessors.register' should be a class")

    def __get_instance(self, value: t.Any, var_type: t.Optional[str] = None) -> DataAccessor:  # type: ignore
        access = self.__access_4_type.get(var_type or type(value).__name__)
        if access is None:
            warnings.warn(f"Can't find Data Accessor for type {var_type or type(value).__name__}")
            return self.__invalid_data_accessor
        return access

    def _cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        inst = self.__access_4_type.get(type(value).__name__)
        return inst.cast_string_value(var_name, value) if inst else value

    def _is_data_access(self, var_name: str, value: t.Any) -> bool:
        inst = self.__access_4_type.get(type(value).__name__)
        return inst and inst.is_data_access(var_name, value)

    def _get_data(self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return self.__get_instance(value).get_data(guiApp, var_name, value, payload, self.__data_format)

    def _get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return self.__get_instance(value).get_col_types(var_name, value)

    def _set_data_format(self, data_format: DataFormat):
        self.__data_format = data_format
