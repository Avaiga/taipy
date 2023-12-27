# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
from typing import Any, Dict, List

from taipy.gui import Gui

# Busiest US airports
# Source: https://en.wikipedia.org/wiki/List_of_busiest_airports_by_passenger_traffic
airports: Dict[str, Dict[str, float]] = {
    "AMS": {"lat": 52.31047296675518, "lon": 4.76819929439927},
    "ATL": {"lat": 33.64086185344307, "lon": -84.43600501711686},
    "AYT": {"lat": 36.90419539293911, "lon": 30.801855337974292},
    "BOS": {"lat": 42.36556559649881, "lon": -71.00960311751096},
    "CAN": {"lat": 23.38848323741897, "lon": 113.30277713668413},
    "CDG": {"lat": 49.008029034119915, "lon": 2.550879924581871},
    "CJU": {"lat": 33.51035978854847, "lon": 126.4913319405336},
    "CKG": {"lat": 29.71931573810283, "lon": 106.64211731662628},
    "CLT": {"lat": 35.214730980190616, "lon": -80.9474735034797},
    "CSX": {"lat": 28.196638298182446, "lon": 113.22083329905352},
    "CTU": {"lat": 30.567492917634063, "lon": 103.94912193845805},
    "CUN": {"lat": 21.04160313837335, "lon": -86.87407057500725},
    "DEL": {"lat": 28.556426221725868, "lon": 77.10031185913002},
    "DEN": {"lat": 39.85589532386815, "lon": -104.67329901305273},
    "DFW": {"lat": 32.89998507111719, "lon": -97.04044513206443},
    "DME": {"lat": 55.41032513421412, "lon": 37.902386927376234},
    "DTW": {"lat": 42.216145762248594, "lon": -83.35541784824225},
    "DXB": {"lat": 25.253155060720765, "lon": 55.365672799304534},
    "EWR": {"lat": 40.68951508829295, "lon": -74.17446240095387},
    "FLL": {"lat": 26.072469069499288, "lon": -80.1502073285754},
    "FRA": {"lat": 50.037870541116, "lon": 8.562119610188235},
    "GMP": {"lat": 37.558628944763534, "lon": 126.79445244110332},
    "GRU": {"lat": -23.430691200492866, "lon": -46.473107371367846},
    "HGH": {"lat": 30.2359856421667, "lon": 120.43880486944619},
    "HND": {"lat": 35.54938443207139, "lon": 139.77979568388005},
    "IAH": {"lat": 29.98997826322153, "lon": -95.33684707873988},
    "IST": {"lat": 41.27696594578831, "lon": 28.73004303446375},
    "JFK": {"lat": 40.64129497654287, "lon": -73.77813830094803},
    "KMG": {"lat": 24.99723271310971, "lon": 102.74030761670535},
    "LAS": {"lat": 36.08256046166282, "lon": -115.15700045025673},
    "LAX": {"lat": 33.94157995977848, "lon": -118.40848708486908},
    "MAD": {"lat": 40.49832400063489, "lon": -3.5676196584173754},
    "MCO": {"lat": 28.419119921670067, "lon": -81.30451008534465},
    "MEX": {"lat": 19.436096410278736, "lon": -99.07204777544095},
    "MIA": {"lat": 25.795823878101675, "lon": -80.28701871639629},
    "MSP": {"lat": 44.88471735079015, "lon": -93.22233824616785},
    "ORD": {"lat": 41.98024003208415, "lon": -87.9089657513565},
    "PEK": {"lat": 40.079816213451416, "lon": 116.60309064055198},
    "PHX": {"lat": 33.43614430802288, "lon": -112.01128270596944},
    "PKX": {"lat": 39.50978840400886, "lon": 116.41050689906415},
    "PVG": {"lat": 31.144398958515847, "lon": 121.80823008537978},
    "SAW": {"lat": 40.9053709590178, "lon": 29.316838841845318},
    "SEA": {"lat": 47.448024349661814, "lon": -122.30897973141963},
    "SFO": {"lat": 37.62122788155908, "lon": -122.37901977603573},
    "SHA": {"lat": 31.192227319334787, "lon": 121.33425408454256},
    "SLC": {"lat": 40.78985913031307, "lon": -111.97911351851535},
    "SVO": {"lat": 55.97381026156798, "lon": 37.412288430689664},
    "SZX": {"lat": 22.636827890877626, "lon": 113.81454162446936},
    "WUH": {"lat": 30.776589409566686, "lon": 114.21244949898504},
    "XIY": {"lat": 34.437119809208546, "lon": 108.7573508575816},
}

# Inter US airports flights
# Source: https://www.faa.gov/air_traffic/by_the_numbers
flights: List[Dict[str, Any]] = [
    {"from": "ATL", "to": "DFW", "traffic": 580},
    {"from": "ATL", "to": "MIA", "traffic": 224},
    {"from": "BOS", "to": "LAX", "traffic": 168},
    {"from": "DEN", "to": "DFW", "traffic": 558},
    {"from": "DFW", "to": "BOS", "traffic": 422},
    {"from": "DFW", "to": "CLT", "traffic": 360},
    {"from": "DFW", "to": "JFK", "traffic": 56},
    {"from": "DFW", "to": "LAS", "traffic": 569},
    {"from": "DFW", "to": "SEA", "traffic": 392},
    {"from": "DTW", "to": "DFW", "traffic": 260},
    {"from": "EWR", "to": "DFW", "traffic": 310},
    {"from": "EWR", "to": "ORD", "traffic": 168},
    {"from": "FLL", "to": "DFW", "traffic": 336},
    {"from": "FLL", "to": "ORD", "traffic": 168},
    {"from": "IAH", "to": "DFW", "traffic": 324},
    {"from": "JFK", "to": "FLL", "traffic": 112},
    {"from": "JFK", "to": "LAS", "traffic": 112},
    {"from": "JFK", "to": "LAX", "traffic": 548},
    {"from": "JFK", "to": "ORD", "traffic": 56},
    {"from": "LAS", "to": "MIA", "traffic": 168},
    {"from": "LAX", "to": "DFW", "traffic": 914},
    {"from": "LAX", "to": "EWR", "traffic": 54},
    {"from": "LAX", "to": "LAS", "traffic": 222},
    {"from": "LAX", "to": "MCO", "traffic": 56},
    {"from": "LAX", "to": "MIA", "traffic": 392},
    {"from": "LAX", "to": "SFO", "traffic": 336},
    {"from": "MCO", "to": "DFW", "traffic": 500},
    {"from": "MCO", "to": "JFK", "traffic": 224},
    {"from": "MCO", "to": "ORD", "traffic": 224},
    {"from": "MIA", "to": "BOS", "traffic": 392},
    {"from": "MIA", "to": "DEN", "traffic": 112},
    {"from": "MIA", "to": "DFW", "traffic": 560},
    {"from": "MIA", "to": "DTW", "traffic": 112},
    {"from": "MIA", "to": "EWR", "traffic": 168},
    {"from": "MIA", "to": "IAH", "traffic": 168},
    {"from": "MIA", "to": "JFK", "traffic": 392},
    {"from": "MIA", "to": "MCO", "traffic": 448},
    {"from": "MSP", "to": "DFW", "traffic": 326},
    {"from": "MSP", "to": "MIA", "traffic": 56},
    {"from": "ORD", "to": "BOS", "traffic": 430},
    {"from": "ORD", "to": "DEN", "traffic": 112},
    {"from": "ORD", "to": "DFW", "traffic": 825},
    {"from": "ORD", "to": "LAS", "traffic": 280},
    {"from": "ORD", "to": "LAX", "traffic": 496},
    {"from": "ORD", "to": "MIA", "traffic": 505},
    {"from": "ORD", "to": "MSP", "traffic": 160},
    {"from": "ORD", "to": "PHX", "traffic": 280},
    {"from": "ORD", "to": "SEA", "traffic": 214},
    {"from": "ORD", "to": "SFO", "traffic": 326},
    {"from": "PHX", "to": "DFW", "traffic": 550},
    {"from": "PHX", "to": "MIA", "traffic": 56},
    {"from": "SEA", "to": "JFK", "traffic": 56},
    {"from": "SFO", "to": "DFW", "traffic": 526},
    {"from": "SFO", "to": "JFK", "traffic": 278},
    {"from": "SFO", "to": "MIA", "traffic": 168},
    {"from": "SLC", "to": "DFW", "traffic": 280},
]

data = []
max_traffic = 0
for flight in flights:
    airport_from = airports[flight["from"]]
    airport_to = airports[flight["to"]]
    # Define data source to plot this flight
    data.append({"lat": [airport_from["lat"], airport_to["lat"]], "lon": [airport_from["lon"], airport_to["lon"]]})
    # Store the maximum traffic
    if flight["traffic"] > max_traffic:
        max_traffic = flight["traffic"]

properties = {
    # Chart data
    "data": data,
    # Chart type
    "type": "scattergeo",
    # Keep lines only
    "mode": "lines",
    # Flights display as redish lines
    "line": {"width": 2, "color": "E22"},
    "layout": {
        # Focus on the USA region
        "geo": {"scope": "usa"}
    },
}

# Set the proper data source and opacity for each trace
for i, flight in enumerate(flights):
    # lat[trace_index] = "[index_in_data]/lat"
    properties[f"lat[{i+1}]"] = f"{i}/lat"
    # lon[trace_index] = "[index_in_data]/lon"
    properties[f"lon[{i+1}]"] = f"{i}/lon"
    # Set flight opacity (max traffic -> max opacity)
    # Hide legend for all flights
    properties[f"options[{i+1}]"] = {"opacity": flight["traffic"] / max_traffic, "showlegend": False}

page = """
# Maps - Multiple Lines

<|chart|properties={properties}|>
"""

Gui(page).run()
