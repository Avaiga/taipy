from markdown.extensions import Extension
from typing import Any
from .preproc import TaipyPreprocessor
from .field import FieldPattern
from .number import NumberPattern
from .slider import SliderPattern
from .button import ButtonPattern
from .date_selector import DateSelectorPattern
from .table import TablePattern

__all__ = ['makeTaipyExtension']

class TaipyExtension(Extension):

  def extendMarkdown(self, md):
    md.registerExtension(self)
    md.preprocessors.add('taipy', TaipyPreprocessor(), '_begin')
    FieldPattern.extendMarkdown(md)
    NumberPattern.extendMarkdown(md)
    SliderPattern.extendMarkdown(md)
    ButtonPattern.extendMarkdown(md)
    DateSelectorPattern.extendMarkdown(md)
    TablePattern.extendMarkdown(md)

def makeTaipyExtension(*args: Any, **kwargs: Any) -> Extension:
  return TaipyExtension(*args, **kwargs)
