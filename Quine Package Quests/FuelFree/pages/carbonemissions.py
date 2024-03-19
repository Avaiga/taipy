from taipy.gui import Markdown
import pandas as pd

# Read the data
DATA = pd.read_csv("./data.csv")

YEARS = DATA.columns[1:].tolist()
COUNTRIES = DATA["Country Name"].tolist()

# Default Values -> Africa Eastern and Angola
country1 = COUNTRIES[1]  
country2 = COUNTRIES[4]  

COUNTRY_DATA1 = DATA[DATA["Country Name"] == country1].iloc[0, 1:]
COUNTRY_DATA2 = DATA[DATA["Country Name"] == country2].iloc[0, 1:]


def choose_country(state):
    COUNTRY_DATA1 = DATA[DATA["Country Name"] == state.country1].iloc[0, 1:]
    COUNTRY_DATA2 = DATA[DATA["Country Name"] == state.country2].iloc[0, 1:]
    state.LINE_GRAPH_DATA = {
        "Years": YEARS, 
        "Country1": list(COUNTRY_DATA1),
        "Country2": list(COUNTRY_DATA2),
    }

LINE_GRAPH_DATA = {
    "Years": YEARS,
    "Country1": list(COUNTRY_DATA1),
    "Country2": list(COUNTRY_DATA2),
}

carbonemissionspage = Markdown("carbonemissions.md")
carbonemissionspage.choose_country = choose_country
carbonemissionspage.LINE_GRAPH_DATA = LINE_GRAPH_DATA
