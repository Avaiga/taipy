import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
import plotly.io as pio


data = pd.read_csv('data/aggregate/aggregate.csv')

location_counts = data['location'].value_counts(sort=True)

location_fig = go.Figure(data=go.Bar(x=location_counts.index, y=location_counts.values))
location_fig.update_layout(title_text='Location counts', xaxis_title='index', yaxis_title='values')


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


demand_fig = go.Figure(data=go.Bar(x=demand['Query'], y=demand['Demand']))
demand_fig.update_layout(title_text='Job Demand', xaxis_title='Job', yaxis_title='Demand')
graph_div = pyo.plot(demand_fig, output_type='div')

with open('static/demand.html','w') as f:
    f.write(graph_div)

pio.write_image(demand_fig,'static/job_demand.png')
pio.write_image(location_fig, 'static/location_counts.png')