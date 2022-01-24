import typing as t
import warnings
import base64
import pathlib
from importlib import util

if util.find_spec("magic"):
    import magic


class ContentAccessor:
    def __init__(self) -> None:
        self.__content_paths: t.Dict[str, pathlib.Path] = {}
        self.__paths: t.Dict[pathlib.Path, str] = {}
        self.__vars: t.Dict[str, bool] = {}

    def get_path(self, path: pathlib.Path) -> str:
        url_path = self.__paths.get(path)
        if url_path is None:
            self.__paths[path] = url_path = "taipyStatic" + str(len(self.__paths))
        return url_path

    def __getHeaders(
        self, path: pathlib.Path, file_name: str, var_name: t.Union[str, None], bypass: bool
    ) -> t.Dict[str, t.Any]:
        image = self.__vars.get(var_name) if var_name else True
        if not image:
            file = path / file_name
            mime = None
            if not bypass and util.find_spec("magic"):
                mime = self.__get_mime_from_file(file)
            mime = "application/octet-stream" if not mime else mime
            return {
                "Content-Type": f"{mime}; charset=utf-8",
                "Content-Disposition": f'attachment; filename="{file_name}"; filename*="{file_name}"',
                "Content-Length": file.stat().st_size,
            }
        return {}

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
        if util.find_spec("magic"):
            try:
                return magic.from_file(str(path), mime=True)
            except Exception as e:
                warnings.warn(f"({path}) cannot read mime type.\n{e}")
        return None

    def get_info(self, var_name: str, value: t.Any) -> t.Union[str, t.Tuple[str], t.Any]:
        image = self.__vars.get(var_name)
        if image is None:
            return value
        if isinstance(value, str):
            path = pathlib.Path(value)
            if path.is_file():
                if image:
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
            if util.find_spec("magic"):
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
