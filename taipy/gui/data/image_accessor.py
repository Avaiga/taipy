import typing as t
import warnings
import base64
import pathlib
from importlib import util

if util.find_spec("magic"):
    import magic

from .data_accessor import DataAccessor
from .data_format import DataFormat


class ImageAccessor(DataAccessor):

    __paths: t.Dict[pathlib.Path, str] = {}

    @staticmethod
    def _get_path(path: pathlib.Path) -> str:
        url_path = ImageAccessor.__paths.get(path)
        if url_path is None:
            ImageAccessor.__paths[path] = url_path = "taipyStatic" + str(len(ImageAccessor.__paths))
        return url_path

    @staticmethod
    def get_supported_classes() -> t.Union[t.Type, t.List[t.Type], t.Tuple[t.Type]]:
        return []

    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        if isinstance(value, str):
            path = pathlib.Path(value)
            if path.is_file():
                dir_path = path.resolve().parent
                url_path = ImageAccessor._get_path(dir_path)
                return (f"{url_path}/{path.name}", url_path, dir_path.as_posix())
            else:
                return value
        else:
            if util.find_spec("magic"):
                try:
                    mime = magic.from_buffer(value, mime=True)
                    if mime.startswith("image"):
                        return f"data:{mime};base64," + base64.urlsafe_b64encode(value).decode("utf-8")
                    else:
                        warnings.warn(f"{var_name} ({type(value)}) is not an image: {mime}")
                        return f"Invalid content: {mime}"
                except Exception as e:
                    warnings.warn(f"{var_name} ({type(value)}) cannot be base64 encoded.\n{e}")
                    return "Cannot be base64 encoded"
            else:
                warnings.warn(
                    "python-magic (and python-magic-bin for win) packages need to be installed if you want to process images as array of bytes."
                )
                return "Cannot guess content type"

    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return False

    def get_data(
        self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
        return {}

    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return {}
