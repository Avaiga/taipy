# Example for column name styling

from taipy.gui import Gui
import pandas as pd

# Sample data in DataFrame format
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Occupation": ["Engineer", "Doctor", "Artist"]
})

# Define column properties
columns = [
    {"field": "Name", "header": "Name", "header_style": "color: blue; font-weight: bold;"},
    {"field": "Age", "header": "Age", "header_style": "color: blue; font-weight: bold;"},
    {"field": "Occupation", "header": "Occupation", "header_style": "color: blue; font-weight: bold;"}
]

# Page content with table and header styling
page = """
<|table|data={df}|columns={columns}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Column Name Styling Example")