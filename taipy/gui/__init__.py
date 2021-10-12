from typing import Optional
from ._md_ext import makeTaipyExtension
from .gui import Gui
from .renderers import Html, Markdown
from .taipyimage import TaipyImage


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
