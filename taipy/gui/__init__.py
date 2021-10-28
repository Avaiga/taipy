from typing import Optional
from ._md_ext import makeTaipyExtension
from .gui import Gui
from .renderers import Html, Markdown
from .taipyimage import TaipyImage
from .data import DataAccessor


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
