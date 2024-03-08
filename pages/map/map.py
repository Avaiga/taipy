from data.data import data as dataset
import taipy.gui.builder as tgb
from taipy.gui import Markdown

import json
import pandas as pd
import plotly.express as px


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

map_md = Markdown("pages/map/map.md")
