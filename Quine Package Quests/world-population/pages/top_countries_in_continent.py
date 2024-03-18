# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Selection Menus
years_list = list(filter(lambda x: x.endswith("Population"), DATA.columns)) # All years present in dataset columns
CONTINENTS = list(DATA["Continent"].unique())
YEARS = list(map(lambda x: x.replace("Population", "").strip(), years_list))

# Choosen Value
continent = CONTINENTS[0]
year = YEARS[0]

# Chart content
chart_data = DATA.loc[DATA["Continent"]==continent].sort_values(by=[f"{year} Population"], ascending=False)[['Country/Territory', f"{year} Population"]]
chart_data.rename(columns = {f"{year} Population":'Population', "Country/Territory" : "Countries/Territories" }, inplace = True)

# On Year/Continent Selection!
def on_selection(state):
    new_chart = DATA.loc[DATA["Continent"]==state.continent].sort_values(by=[f"{state.year} Population"], ascending=False)[['Country/Territory', f"{state.year} Population"]]
    new_chart.rename(columns = {f"{state.year} Population":'Population', "Country/Territory" : "Countries/Territories" }, inplace = True)
    state.chart_data = new_chart

# Creating Page 
top_countries_in_continent = Markdown("top_countries_in_continent.md")