from taipy.gui import Markdown
from data.data import data

marker_map = {"color": "magnitude", "size": "Size", "showscale": True, "colorscale": "Viridis"}
layout_map = {
    "dragmode": "zoom",
    "mapbox": {"style": "open-street-map", "center": {"lat": 38, "lon": -90}, "zoom": 3}
}

options = {"unselected": {"marker": {"opacity": 0.5}}}
data['Size'] = (data['magnitude'])*2

map_md = Markdown("pages/map/map.md")
