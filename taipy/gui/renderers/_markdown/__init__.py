from typing import Any

from markdown.extensions import Extension

from .control import ControlPattern
from .postproc import Postprocessor
from .preproc import Preprocessor
from .blocproc import StartBlockProcessor

__all__ = ["makeTaipyExtension"]


class TaipyExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        # md.preprocessors.add("taipy", Preprocessor(md), "_begin")
        md.preprocessors.register(Preprocessor(md), "taipy", 210)
        ControlPattern.extendMarkdown(md)
        md.parser.blockprocessors.register(
            StartBlockProcessor(md.parser), "taipy", 175
        )  # process the block tags (layout and co)
        md.treeprocessors.register(Postprocessor(md), "taipy", 200)


def makeTaipyExtension(*args: Any, **kwargs: Any) -> Extension:
    return TaipyExtension(*args, **kwargs)
