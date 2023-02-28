# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t


class Icon:
    """Small image in the User Interface.

    Icons are typically used in controls like [button](../gui/viselements/button.md)
    or items in a [menu](../gui/viselements/menu.md).

    Attributes:
        path (str): The path to the image file.
        text (Optional[str]): The text associated to the image or None if there is none.
        svg (Optional[bool]): True if the image is svg.

    If a text is associated to an icon, it is rendered by the visual elements that
    uses this Icon.
    """

    @staticmethod
    def get_dict_or(value: t.Union[str, t.Any]) -> t.Union[str, dict]:
        return value._to_dict() if isinstance(value, Icon) else value

    def __init__(self, path: str, text: t.Optional[str] = None, light_path: t.Optional[bool]= None, dark_path: t.Optional[bool]= None, svg: t.Optional[bool]= None) -> None:
        """Initialize a new Icon.

        Arguments:
            path (str): The path to an image file.<br/>
                This path must be relative to and inside the root directory of the
                application (where the Python file that created the `Gui` instance
                is located).<br/>
                In situations where the image file is located outside the application
                directory, a _path mapping_ must be used: the _path_mapping_ parameter
                of the `Gui^` constructor makes it possible to access a resource anywhere
                on the server filesystem, as if it were located in a subdirectory of
                the application directory.
            text (Optional[str]): The text associated to the image. If _text_ is None,
                there is no text associated to this image.
            light_path (Optional[str]): The path to the light theme image (fallback to _path_ if not defined).
            dark_path (Optional[str]): The path to the dark theme image (fallback to _path_ if not defined).
            svg (Optional[bool]): Indicates that the _path_ should be treated as an SVG resource (defaults to True if _path_ ends with .svg).
        """
        self.path = path
        self.text = text
        if svg is not None:
            self.svg = svg
        if light_path is not None:
            self.light_path = light_path
        if dark_path is not None:
            self.dark_path = dark_path

    def _to_dict(self, a_dict: t.Optional[dict] = None) -> dict:
        if a_dict is None:
            a_dict = {}
        a_dict["path"] = self.path
        if self.text is not None:
            a_dict["text"] = self.text
        if hasattr(self, "svg") and self.svg is not None:
            a_dict["svg"] = self.svg
        if hasattr(self, "light_path") and self.light_path is not None:
            a_dict["light_path"] = self.light_path
        if hasattr(self, "dark_path") and self.dark_path is not None:
            a_dict["dark_path"] = self.dark_path
        return a_dict
