
import numpy as np
from taipy.gui import Markdown

from data.data import data

marker_map = {"color":"Deaths", "size": "Size", "showscale":True, "colorscale":"Viridis"}
layout_map = {
            "dragmode": "zoom",
            "mapbox": { "style": "open-street-map", "center": { "lat": 38, "lon": -90 }, "zoom": 3}
            }
options = {"unselected":{"marker":{"opacity":0.5}}}

def initialize_map(data):
    data['Province/State'] = data['Province/State'].fillna(data["Country/Region"])
    data_province = data.groupby(["Country/Region",
                                  'Province/State',
                                  'Longitude',
                                  'Latitude'])\
                         .max()
                         

    data_province_displayed = data_province[data_province['Deaths']>10].reset_index()

    data_province_displayed['Size'] = np.sqrt(data_province_displayed.loc[:,'Deaths']/data_province_displayed.loc[:,'Deaths'].max())*80 + 3
    data_province_displayed['Text'] = data_province_displayed.loc[:,'Deaths'].astype(str) + ' deaths </br> ' + data_province_displayed.loc[:,'Province/State']
    return data_province_displayed


data_province_displayed = initialize_map(data)

map_md = Markdown("pages/map/map.md")
