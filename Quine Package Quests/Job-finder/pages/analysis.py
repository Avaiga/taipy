from taipy import Gui 
import pandas as pd
from taipy.gui import builder as tgb
import plotly.graph_objects as go
import plotly.offline as pyo


data = pd.read_csv('data/aggregate/aggregate.csv')

location_counts = data['location'].value_counts(sort=True)

location_fig = go.Figure(data=go.Bar(x=location_counts.index, y=location_counts.values))
location_fig.update_layout(title_text='Location counts', xaxis_title='index', yaxis_title='values')

# md='''
# # Analysis of sourced data

# <|{location_counts}|chart|type=bar|x=index|y=values|>'''

# Figures are as observed on March 18, 2024
demand={
    "python developer": 7947,
    "data analyst": 5221,
    "machine learning engineer": 27829,
    "software engineer": 46596,
    "backend developer": 18583,
    "devops engineer": 1785,
    "automation engineer": 12976,
    "network engineer": 10513,
    "vuejs developer": 1444,
    "react developer": 6112,
    "nodejs developer": 4883,
    "frontend developer": 12399,
    "full stack developer": 7006,
    "ui developer": 9303,
    "web application developer": 19582,
    "javascript engineer": 6797,
    "mobile app developer": 4191,
}



demand = pd.DataFrame.from_dict(demand, orient = 'index', columns=['demand'])
demand.reset_index(inplace=True)
demand.columns=['Query','Demand']


with tgb.Page() as analysis_page:
    tgb.text('Analysis of sourced data',class_name='h1')
    tgb.html('br')
    tgb.text('Demand of jobs as sourced on 18 March 2024.', class_name='h4')
    with tgb.part('card'):
        tgb.text('Demand of jobs sourced')
        tgb.table('{demand}')
    #tgb.html()

# todo : add the plotly charts - store as image then use html(md is hard, no docs for py)
#Gui(analysis_page).run()