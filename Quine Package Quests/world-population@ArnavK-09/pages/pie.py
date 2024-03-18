# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Year 
years_list = list(filter(lambda x: x.endswith("Population"), DATA.columns)) # All years present in dataset columns
YEARS = list(map(lambda x: x.replace("Population", "").strip(), years_list))
year = YEARS[0]

# Excrating Pie Charts Data
pie_data = {
  "Country": list(DATA["Country/Territory"]),
  "Population": list(DATA["2022 Population"])
}

# Selection Handler 
def update_year(state):
    state.pie_data = {
      "Country": list(DATA["Country/Territory"]),
      "Population": list(DATA[f"{state.year} Population"])
    }

# Pie configuration
pie_options = {
    "textinfo": "none"
}

# Creating Page 
pie_page = Markdown("pie.md")