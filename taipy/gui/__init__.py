from typing import Optional

from .data import DataAccessor
from .gui import Gui
from .renderers import Html, Markdown, makeTaipyExtension
from .taipyimage import TaipyImage


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
