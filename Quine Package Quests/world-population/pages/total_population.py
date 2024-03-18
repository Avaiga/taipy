# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Getting all years 
years_list = list(filter(lambda x: x.endswith("Population"), DATA.columns)) # All years present in dataset columns
YEARS = list(map(lambda x: x.replace("Population", "").strip(), years_list))

# Choosen Year 
year = YEARS[0]

# Returns world population of year 
def total_population(year: int):
    population = DATA["{} Population".format(str(year))].sum()
    return f"👥 {population:,} +"

# World Population of current year 
world_population = (total_population(year))

# Selection Handler 
def update_year(state):
    state.world_population = world_population = total_population(state.year)

# Creating Page
total_population_page = Markdown("total_population.md")