# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Returns worl average population according to years
def get_world_average_population(YEARS):
    world_average = []
    for index, year in enumerate(YEARS):
        year_sum = DATA["{} Population".format(year)].mean()
        world_average.append(year_sum)
    return world_average

# All Countries List 
COUNTRIES = list(DATA["Country/Territory"].unique())

# Getting all years 
years_list = list(filter(lambda x: x.endswith("Population"), DATA.columns)) # All years present in dataset columns
YEARS = list(map(lambda x: x.replace("Population", "").strip(), years_list))

# Chosen Default Values  
country1 = COUNTRIES[92] # India
country2 = COUNTRIES[41] # China

# Choosen Country All Data From Dataset
COUNTRY_DATA1 = (DATA.iloc[COUNTRIES.index(country1)])
COUNTRY_DATA2 = (DATA.iloc[COUNTRIES.index(country2)])

# world average population
world_average_population = get_world_average_population(YEARS)

# Selection Handler for Country
def choose_country(state):
    COUNTRY_DATA1 = (DATA.iloc[COUNTRIES.index(state.country1)])
    COUNTRY_DATA2 = (DATA.iloc[COUNTRIES.index(state.country2)])
    state.LINE_GRAPH_DATA = {
        "Years": YEARS, 
        "World Average": world_average_population,
        "Country1": list(COUNTRY_DATA1[5:13]),
        "Country2": list(COUNTRY_DATA2[5:13]),
    }

# Graph Data
LINE_GRAPH_DATA = {
    "Years": YEARS,
    "World Average": world_average_population,
    "Country1": list(COUNTRY_DATA1[5:13]),
    "Country2": list(COUNTRY_DATA2[5:13]),
}

# Creating Page 
compare_countries_page = Markdown("compare_countries.md")