import pandas as pd
from taipy.gui import Markdown
from graphs.graphs import PieChart, BarGraph

data = pd.read_csv('DataSet\Diwali Sales Data.csv', encoding= 'latin1')


def on_change_Occu(state):

    state.pie_data = PieChart(state.occu)

    state.Orders = Stats(state.occu)



def Stats(occus: str):
    occupation_data = data[data['Occupation'] == occus]
    Orders = str(occupation_data['Orders'].sum())
    return Orders


occupation = data['Occupation'].unique().tolist()
state  = data['State'].unique().tolist()

occu= occupation[0]
states = state[0]

Orders = Stats(occu)

bar_data, bar_design = BarGraph()
pie_data = PieChart(states)


dashboard_ui = Markdown("web_pages/dashboard/dashboard_ui.md")