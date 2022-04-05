# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import base64
import pathlib
import tempfile
import typing as t
import warnings
from importlib import util
from pathlib import Path
from sys import getsizeof

from ..utils import _get_non_existent_file_path

_has_magic_module = False

if util.find_spec("magic"):
    import magic

    _has_magic_module = True


class _ContentAccessor:
    def __init__(self, data_url_max_size: int) -> None:
        self.__content_paths: t.Dict[str, pathlib.Path] = {}
        self.__url_is_image: t.Dict[str, bool] = {}
        self.__paths: t.Dict[pathlib.Path, str] = {}
        self.__data_url_max_size = data_url_max_size
        self.__temp_dir_path = Path(tempfile.gettempdir())

    def get_path(self, path: pathlib.Path) -> str:
        url_path = self.__paths.get(path)
        if url_path is None:
            self.__paths[path] = url_path = "taipyStatic" + str(len(self.__paths))
        return url_path

    def get_content_path(
        self, url_path: str, file_name: str, bypass: t.Union[str, None]
    ) -> t.Tuple[t.Union[pathlib.Path, None], bool]:
        content_path = self.__content_paths.get(url_path)
        if not content_path:
            return (None, True)
        return (content_path, bypass is not None or self.__url_is_image.get(f"{url_path}/{file_name}", False))

    def __get_mime_from_file(self, path: pathlib.Path):
        if _has_magic_module:
            try:
                return magic.from_file(str(path), mime=True)
            except Exception as e:
                warnings.warn(f"({path}) cannot read mime type.\n{e}")
        return None

    def get_info(self, var_name: str, value: t.Any, image: bool) -> t.Union[str, t.Tuple[str], t.Any]:  # noqa: C901
        if value is None:
            return ""
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
            path = pathlib.Path(newvalue) if isinstance(newvalue, str) else newvalue
            if not path.is_file():
                return str(value)
            if image:
                if not mime:
                    mime = self.__get_mime_from_file(path)
                if mime and not mime.startswith("image"):
                    warnings.warn(f"{var_name} ({path}) is not an image: {mime}")
                    return f"Invalid content: {mime}"
            dir_path = path.resolve().parent
            url_path = self.get_path(dir_path)
            self.__content_paths[url_path] = dir_path
            file_url = f"{url_path}/{path.name}"
            self.__url_is_image[file_url] = image
            return (file_url,)
        elif _has_magic_module:
            try:
                mime = magic.from_buffer(value, mime=True)
                if not image or mime.startswith("image"):
                    return f"data:{mime};base64," + str(base64.b64encode(value), "utf-8")
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
