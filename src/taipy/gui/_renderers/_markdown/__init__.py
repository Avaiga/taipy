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

from typing import Any

from markdown.extensions import Extension

from .blocproc import _StartBlockProcessor
from .control import _ControlPattern
from .postproc import _Postprocessor
from .preproc import _Preprocessor


class _TaipyMarkdownExtension(Extension):
    config = {"gui": ["", "Gui object for extension"]}

    def extendMarkdown(self, md):
        from ...gui import Gui

        gui = self.config["gui"][0]
        if not isinstance(gui, Gui):
            raise RuntimeError("Gui instance is not bound to Markdown Extension")
        md.registerExtension(self)
        _Preprocessor.extend(md, gui, 210)
        _ControlPattern.extend(md, gui, 205)
        _StartBlockProcessor.extend(md, gui, 175)
        _Postprocessor.extend(md, gui, 200)
