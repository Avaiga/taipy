from taipy.gui import Gui
from my_custom_lib import MyLibrary
import random
import string

value = "a"

page = """
# A custom element

*My custom label:* <|{value}|my_custom.label|>

<|Add a character|button|>
"""

def on_action(state):
  state.value = state.value + random.choice(string.ascii_letters)

gui = Gui(page)
gui.add_library(MyLibrary())
gui.run()
