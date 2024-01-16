from taipy.gui import Markdown 

import numpy as np

from data.data import data

selector_country = list(np.sort(data['Country/Region'].astype(str).unique()))
selected_country = 'France'

root = Markdown("pages/root.md")