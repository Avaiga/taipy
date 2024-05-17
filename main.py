from taipy.gui import Gui
import json

# Import extension library fromt the package directory name
# from <package_dir_name> import Library

default_value = 100

style = {'position': 'relative', 'display': 'inline-block', 'borderRadius': '20px', 'overflow': 'hidden'}

max_value = 90
min_value = 0

layout = {'paper_bgcolor': 'lavender', 'font': {'color': "darkblue", 'family': "Arial"}}

page = """
# Extension library
<|50.54|metric|style={style}|max={max_value}|min={min_value}|threshold=70|layout={layout}|>
"""

gui = Gui(page=page)

if __name__ == "__main__":
  # Run main app
  print("Running main app")
  gui.run(port=8085, use_reloader=True, debug=True)

  # <|{default_value}|library.metrics|delta=20|format=%.2f%%|format_delta=%.2f%%|     suffix prefix>
  # <|{default_value}|library.metrics|delta=-20|format=%.2f%%|format_delta=%.2f%%|>
