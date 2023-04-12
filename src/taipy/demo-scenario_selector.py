import typing as t

from gui_core.GuiCoreLib import GuiCore, GuiCoreContext
from taipy.core import Core, Scenario
from taipy.gui import Gui, State
from taipy.gui.extension import ElementLibrary, Element, ElementProperty, PropertyType

page = """
# Getting started with example

<|taipy_gui_core.scenario_selector|show_add_button|display_cycles|>

"""    
Gui.add_library(GuiCore())
Gui(page).run(port=8000, use_reloader=True)
