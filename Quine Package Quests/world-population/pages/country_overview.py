# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")
years_list = list(filter(lambda x: x.endswith("Population"), DATA.columns)) # All years present in dataset columns

# All Countries List 
COUNTRIES = list(DATA["Country/Territory"].unique())

# Chosen Country  
country = COUNTRIES[0]

# Choosen Country All Data From Dataset
COUNTRY_DATA = (DATA.iloc[COUNTRIES.index(country)])

# Creating Data Object
LINE_GRAPH_DATA = {
    "Population": list(COUNTRY_DATA[5:13]),
    "Years": list(map(lambda x: x.replace("Population", "").strip(), years_list)), # Formatting Years
}

# Country information Table Contents
country_info_data = {
    "Attribute": COUNTRY_DATA.index.tolist(),
    "Content": COUNTRY_DATA.values.tolist(),
}

# Country selector handler 
def on_selection(state):
    COUNTRY_DATA = (DATA.iloc[COUNTRIES.index(state.country)])
    state.country_info_data = {
        "Attribute": COUNTRY_DATA.index.tolist(),
        "Content": COUNTRY_DATA.values.tolist()
     }
    state.LINE_GRAPH_DATA = {
        "Population": list(COUNTRY_DATA[5:13]),
        "Years": list(map(lambda x: x.replace("Population", "").strip(), years_list)), # Formatting Years
    }

# Creating Page 
country_overview_page = Markdown("country_overview.md")