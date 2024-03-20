from taipy.gui import Markdown
import numpy as np

from data.data import data

selector_country = list(np.sort(data['country'].astype(str).unique()))
selected_country = 'India'
root = Markdown("pages/root.md")
