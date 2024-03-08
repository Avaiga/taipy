from taipy.gui import Gui
from data.data import data as dataset
import taipy.gui.builder as tgb

import json
import pandas as pd
import plotly.express as px

from pages.root import root_md
from pages.district.district import district_md
from pages.dataset.dataset import dataset_md
from pages.nepal.nepal import nepal_md
from pages.collect_data.collect_data import collect_data_md


geojson_path = "data/location.geojson"

with open(geojson_path) as f:
    geojson_data = json.load(f)

first_feature_properties = geojson_data['features'][0]['properties']

district_population = dataset.groupby(
    'District')['Total population'].sum().reset_index()


fig = px.choropleth_mapbox(district_population,
                           geojson=geojson_data,
                           locations='District',
                           featureidkey="properties.District",
                           color='Total population',
                           color_continuous_scale="Viridis",
                           mapbox_style="open-street-map",
                           # Center on Nepal
                           zoom=5, center={"lat": 28.3949, "lon": 84.1240},
                           opacity=0.5,
                           labels={'Total population': 'Total Population'}
                           )

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# fig.show()


map_md = """
# <center>**Map**{:.color-primary} Statistics</center>

<|chart|figure={fig}|height=800px|class_name=p2 m2|>
"""

pages = {
    "/": root_md,
    "district": district_md,
    "nepal": nepal_md,
    "map": map_md,
    "dataset": dataset_md,
    "collect_data": collect_data_md,
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
