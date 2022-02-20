from typing import Any

from markdown.extensions import Extension

from .blocproc import StartBlockProcessor
from .control import ControlPattern
from .postproc import Postprocessor
from .preproc import Preprocessor


class TaipyMarkdownExtension(Extension):

    config = {"gui": ["", "Gui object for extension"]}

    def extendMarkdown(self, md):
        from ...gui import Gui

        gui = self.config["gui"][0]
        if not isinstance(gui, Gui):
            raise RuntimeError("Gui instance is not bindded to Markdown Extension")
        md.registerExtension(self)
        Preprocessor.extend(md, gui, 210)
        ControlPattern.extend(md, gui, 205)
        StartBlockProcessor.extend(md, gui, 175)
        Postprocessor.extend(md, gui, 200)
