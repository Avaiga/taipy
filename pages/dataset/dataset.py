from data.data import data as dataset
from taipy.gui import Markdown

table = dataset.to_dict()


dataset_md = Markdown('pages/dataset/dataset.md')
