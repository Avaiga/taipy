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
        Preprocessor.extend(md, gui)
        ControlPattern.extend(md, gui)
        StartBlockProcessor.extend(md, gui)
        Postprocessor.extend(md, gui)
