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
