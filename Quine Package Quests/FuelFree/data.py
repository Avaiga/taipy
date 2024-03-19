# Importing the necessary modules
from taipy import Gui
import graphs
import pandas as pd

# Constants
OE = "OddEven"
PT = "PublicTransport"
EV = "ElectricVehicle"
DATE = "Date"
BREAKTYPE = "Break"
COOLPINK = "#f8b4ce"
COOLGREEN = "#a2c9ba"
PASTELYELLOW = "#f8ecb4"

# Path to CSV file
path_to_csv = "test.csv"

# Function to refresh data
def refresh_data():
    # Resetting variables in graphs.py
    graphs.PTnum = 0
    graphs.OEnum = 0
    graphs.EVnum = 0
    graphs.date_lis = []
    graphs.OE_breaks = []
    graphs.PT_breaks = []
    graphs.EV_breaks = []

    # Reading CSV and updating data in graphs.py
    dataset = graphs.readCSV(path_to_csv)
    date_lis = graphs.get_date_lis()
    date_lis = graphs.date_to_list(dataset, date_lis)
    graphs.add_all_data(dataset, date_lis)

# Retrieving data from graphs.py
PT_lis = graphs.get_PT()
OE_lis = graphs.get_OE()
EV_lis = graphs.get_EV()
date_lis = graphs.get_date_lis()

# Property chart configuration
property_chart = {
    "type": "bar",
    "x": DATE,
    "rebuild": True,
    "render": True,
    "y[1]": PT,
    "y[2]": OE,
    "y[3]": EV,
    "color[1]": COOLPINK,
    "color[2]": COOLGREEN,
    "color[3]": PASTELYELLOW,
}
