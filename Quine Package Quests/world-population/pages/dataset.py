# Imports 
from taipy.gui import Markdown
import pandas as pd

# Our data file 
DATA = pd.read_csv("./data.csv")

# Creating Page 
dataset_page = Markdown("dataset.md")