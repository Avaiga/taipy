import typing as t
import warnings
import base64
import pathlib
import tempfile
from importlib import util
from pathlib import Path
from sys import getsizeof

from ..utils import _get_non_existent_file_path

if util.find_spec("magic"):
    import magic

    _has_magic_module = True


class ContentAccessor:
    def __init__(self, data_url_max_size: int) -> None:
        self.__content_paths: t.Dict[str, pathlib.Path] = {}
        self.__paths: t.Dict[pathlib.Path, str] = {}
        self.__vars: t.Dict[str, bool] = {}
        self.__data_url_max_size = data_url_max_size
        self.__temp_dir_path = Path(tempfile.gettempdir())

    def get_path(self, path: pathlib.Path) -> str:
        url_path = self.__paths.get(path)
        if url_path is None:
            self.__paths[path] = url_path = "taipyStatic" + str(len(self.__paths))
        return url_path

    def get_content_path(
        self, url_path: str, file_name: str, var_name: t.Union[str, None], bypass: t.Union[str, None]
    ) -> t.Tuple[t.Union[pathlib.Path, None], bool]:
        content_path = self.__content_paths.get(url_path)
        if not content_path:
            return (None, True)
        return (content_path, bypass is not None or self.__vars.get(var_name, True) if var_name else True)

    def register_var(self, var_name: str, image: bool, is_dynamic: bool):
        var_name = var_name if is_dynamic else f"//contentaccessor//{len(self.__vars)}"
        self.__vars[var_name] = image
        return var_name

    def __get_mime_from_file(self, path: pathlib.Path):
        if _has_magic_module:
            try:
                return magic.from_file(str(path), mime=True)
            except Exception as e:
                warnings.warn(f"({path}) cannot read mime type.\n{e}")
        return None

    def get_info(self, var_name: str, value: t.Any) -> t.Union[str, t.Tuple[str], t.Any]:  # noqa: C901
        if value is None:
            return value
        image = self.__vars.get(var_name)
        if image is None:
            return value
        newvalue = value
        mime = None
        if not isinstance(newvalue, (str, pathlib.Path)) and (
            getsizeof(newvalue) > self.__data_url_max_size or not _has_magic_module
        ):
            # write data to file
            file_name = "TaiPyContent.bin"
            if _has_magic_module:
                try:
                    mime = magic.from_buffer(value, mime=True)
                    file_name = "TaiPyContent." + mime.split("/")[-1]
                except Exception as e:
                    warnings.warn(f"{var_name} ({type(value)}) cannot be typed.\n{e}")
            file_path = _get_non_existent_file_path(self.__temp_dir_path, file_name)
            try:
                with open(file_path, "wb") as temp_file:
                    temp_file.write(value)
            except Exception as e:
                warnings.warn(f"{var_name} ({type(value)}) cannot be written to file {file_path}.\n{e}")
            newvalue = file_path
        if isinstance(newvalue, (str, pathlib.Path)):
            if isinstance(newvalue, str):
                path = pathlib.Path(newvalue)
            else:
                path = newvalue
            if path.is_file():
                if image:
                    if not mime:
                        mime = self.__get_mime_from_file(path)
                    if mime and not mime.startswith("image"):
                        warnings.warn(f"{var_name} ({path}) is not an image: {mime}")
                        return f"Invalid content: {mime}"
                dir_path = path.resolve().parent
                url_path = self.get_path(dir_path)
                self.__content_paths[url_path] = dir_path
                return (f"{url_path}/{path.name}",)
            else:
                return value
        else:
            if _has_magic_module:
                try:
                    mime = magic.from_buffer(value, mime=True)
                    if not image or mime.startswith("image"):
                        return f"data:{mime};base64," + str(base64.b64encode(value), "utf-8")
                    else:
                        warnings.warn(f"{var_name} ({type(value)}) is not an image: {mime}")
                        return f"Invalid content: {mime}"
                except Exception as e:
                    warnings.warn(f"{var_name} ({type(value)}) cannot be base64 encoded.\n{e}")
                    return "Cannot be base64 encoded"
            else:
                warnings.warn(
                    "python-magic (and python-magic-bin for win) packages need to be installed if you want to process content as array of bytes."
                )
                return "Cannot guess content type"
