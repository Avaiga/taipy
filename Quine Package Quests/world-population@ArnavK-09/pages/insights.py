# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Getting population from columns 5-13
POPULATION_SUM = DATA.iloc[:,5:13].sum() 

# Sorting Values
GRAPH_DATA = POPULATION_SUM.sort_values(ascending=True)

# Creating Data Object
LINE_GRAPH_DATA = {
    "Population": GRAPH_DATA.values,
    "Years": list(map(lambda x: x.replace("Population", "").strip(), GRAPH_DATA.index)), # Formatting Years
}

# Creating Page 
insights_page = Markdown("insights.md")