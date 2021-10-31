from typing import Optional
from .gui import Gui
from .renderers import Html, Markdown, makeTaipyExtension
from .taipyimage import TaipyImage
from .data import DataAccessor


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
