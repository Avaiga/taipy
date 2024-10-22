# Example for column name styling for header

import pandas as pd

from taipy.gui import Gui, Markdown

# Sample data in DataFrame format
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Job or Occupation": ["Engineer", "Doctor", "Artist"]
})


# Page content with table and header styling
page = Markdown("""
<|table|data={df}|columns={columns}|>
""", style={".taipy-table-name": {"color": "blue"}, ".taipy-table-job-or-occupation": {"color": "green"}})

if __name__ == "__main__":
    Gui(page).run(title="Column Name Styling Example")
