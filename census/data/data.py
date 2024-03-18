# Import the pandas library
import pandas as pd

# Specify the file path to the CSV data
path_to_data = "data/data.csv"

# Read the CSV data into a pandas DataFrame
# The pd.read_csv() function reads the CSV file from the specified file path
# and returns a DataFrame object containing the data
data = pd.read_csv(path_to_data)