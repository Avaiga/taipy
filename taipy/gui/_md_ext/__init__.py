from typing import Any

from markdown.extensions import Extension

from .control import ControlPattern
from .preproc import Preprocessor

__all__ = ["makeTaipyExtension"]


class TaipyExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.add("taipy", Preprocessor(), "_begin")
        ControlPattern.extendMarkdown(md)


def makeTaipyExtension(*args: Any, **kwargs: Any) -> Extension:
    return TaipyExtension(*args, **kwargs)
