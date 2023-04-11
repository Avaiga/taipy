import typing as t

from taipy.core import Core, Scenario
from taipy.gui import Gui, State
from taipy.gui.extension import ElementLibrary, Element, ElementProperty, PropertyType

class GuiCoreContext():

  _CORE_CHANGED_NAME = "core_changed"
  _VAR_NAME = "__CCCtx"


  def __init__(self, gui: Gui, core: Core) -> None:
    self.gui = gui
    self.core = core
    self.scenarios: t.List[Scenario]
  
  def get_scenarios(self):
     return []
  
  def create_new_scenario(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
     pass
  
  def broadcast_core_changed(self):
    self.gui.broadcast(GuiCoreContext._CORE_CHANGED_NAME)

class GuiCore(ElementLibrary):
    
  _elts = {"scenario_selector": Element("scenario", {
    "show_add_button": ElementProperty(PropertyType.dynamic_boolean, True),
    "display_cycles": ElementProperty(PropertyType.dynamic_boolean, True),
    "show_primary_flag": ElementProperty(PropertyType.dynamic_boolean, True),
    "scenario_id": ElementProperty(PropertyType.dynamic_string),
    "scenarios": ElementProperty(PropertyType.react, f"{GuiCoreContext._VAR_NAME}.get_scenarios()"),
    "on_scenario_create": ElementProperty(PropertyType.function, f"{GuiCoreContext._VAR_NAME}.create_new_scenario()"),
    "core_changed": ElementProperty(PropertyType.broadcast, GuiCoreContext._CORE_CHANGED_NAME)
  })}
  


  def get_name(self) -> str:
    return "taipy_gui_core"

  def get_elements(self) -> t.Dict[str, Element]:
    return GuiCore._elts

  def get_scripts(self) -> t.List[str]:
    return ["lib/taipy-gui-core.js"]
  
  def on_init(self, gui: Gui) -> t.Optional[t.Tuple[str, t.Any]]:
    return GuiCoreContext._VAR_NAME, GuiCoreContext(gui, Core())

page = """
# Getting started with example

<|taipy_gui_core.scenario_selector|show_add_button|display_cycles|>

"""    
Gui.add_library(GuiCore())
Gui(page).run(port=8000, use_reloader=True)
