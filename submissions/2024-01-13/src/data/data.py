import pandas as pd

path_to_data = "data/covid-19-all.csv"
data = pd.read_csv(path_to_data, low_memory=False)