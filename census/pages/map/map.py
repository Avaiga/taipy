# Import the dataset
from data.data import data as dataset

# Import necessary modules
import taipy.gui.builder as tgb
from taipy.gui import Markdown
import json
import pandas as pd
import plotly.express as px

# Path to the GeoJSON file containing geographical data
geojson_path = "data/location.geojson"

# Load the GeoJSON data
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Get the properties of the first feature in the GeoJSON data
first_feature_properties = geojson_data['features'][0]['properties']

# Group the dataset by district and sum the total population, then reset the index
district_population = dataset.groupby(
    'District')['Total population'].sum().reset_index()

# Create a choropleth map using Plotly Express
fig = px.choropleth_mapbox(
    district_population,
    geojson=geojson_data,  # GeoJSON data for the map
    locations='District',  # Column in the data to use for locations
    featureidkey="properties.District",  # Key in the GeoJSON to match locations
    color='Total population',  # Column to use for coloring
    color_continuous_scale="Viridis",  # Color scale for the map
    mapbox_style="open-street-map",  # Map style
    zoom=5,  # Center and zoom level for Nepal
    center={"lat": 28.3949, "lon": 84.1240},
    opacity=0.5,  # Opacity of the map
    # Label for the colorbar
    labels={'Total population': 'Total Population'}
)

# Remove margins from the figure layout
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Create a Markdown component for the map page
map_md = Markdown("pages/map/map.md")