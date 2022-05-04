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

import typing as t


class Icon:
    """Small image in the User Interface.

    Icons are typically used in controls like [button](../gui/viselements/button.md)
    or items in a [menu](../gui/viselements/menu.md).

    Attributes:
        path (str): The path to the image file.
        text (Optional[str]): The text associated to the image or None if there is none.

    If a text is associated to an icon, it is rendered by the visual elements that
    uses this Icon.
    """

    @staticmethod
    def get_dict_or(value: t.Union[str, t.Any]) -> t.Union[str, dict]:
        return value._to_dict() if isinstance(value, Icon) else value

    def __init__(self, path: str, text: t.Optional[str] = None) -> None:
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
        """
        self.path = path
        self.text = text

    def _to_dict(self, a_dict: t.Optional[dict] = None) -> dict:
        if a_dict is None:
            a_dict = {}
        a_dict["path"] = self.path
        if self.text is not None:
            a_dict["text"] = self.text
        return a_dict
