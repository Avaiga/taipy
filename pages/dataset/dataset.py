# Import the dataset
from data.data import data as dataset

# Import the Markdown component from Taipy GUI
from taipy.gui import Markdown

# Convert the dataset to a dictionary
table = dataset.to_dict()

# Create a Markdown component for the dataset page
dataset_md = Markdown('pages/dataset/dataset.md')