# This Python script tries to locate the taipy.gui package, and
# prints its absolute path if it finds it.
import importlib.util
import os

taipy_gui = importlib.util.find_spec("taipy.gui")
if taipy_gui is None:
    print("Cannot find 'taipy.gui'\nPlease run 'pip install taipy-gui'.")
else:
    print(f"Taipy GUI location: {os.path.dirname(taipy_gui.origin)}")
