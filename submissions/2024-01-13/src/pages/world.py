from taipy.gui import Markdown
import numpy as np

import json

from data.data import data
import pandas as pd

type_selector = ['Absolute', 'Relative']
selected_type = type_selector[0]


def initialize_world(data):
    data_world = data.groupby(["Country/Region",
                                    'Date'])\
                            .sum()\
                            .reset_index()

    with open("data/pop.json","r") as f:        
        pop = json.load(f)
    
    data_world['Population'] = [0]*len(data_world)
    data_world['Date'] = pd.to_datetime(data_world['Date'])
    data_world['Country/Region'] = data_world['Country/Region'].astype(str)
    data_world['Province/State'] = data_world['Province/State'].astype(str)

    for i in range(len(data_world)):
        data_world['Population'][i] = pop[data_world.loc[i, "Country/Region"]][1]
    data_world = data_world.dropna()\
                            .reset_index()
    data_world['Deaths/100k'] = data_world.loc[:,'Deaths']/data_world.loc[:,'Population']*100000
    
    data_world['Deaths'] = pd.to_numeric(data_world['Deaths'], errors='coerce')


    data_world_pie_absolute = data_world.groupby(["Country/Region"])\
                                        .max()\
                                        .sort_values(by='Deaths', ascending=False)[:20]\
                                        .reset_index()

    data_world_pie_relative = data_world.groupby(["Country/Region"])\
                                        .max()\
                                        .sort_values(by='Deaths/100k', ascending=False)[:20]\
                                        .reset_index()\
                                        .drop(columns=['Deaths'])
    
    country_absolute = data_world_pie_absolute['Country/Region'].unique().tolist()
    country_relative = data_world_pie_relative.loc[:,'Country/Region'].unique().tolist()
    
             
    data_world_evolution_absolute = data_world[data_world['Country/Region'].str.contains('|'.join(country_absolute),regex=True)]
    data_world_evolution_absolute = data_world_evolution_absolute.pivot(index='Date', columns='Country/Region', values='Deaths')\
                                     .reset_index()
    
    data_world_evolution_relative = data_world[data_world['Country/Region'].str.contains('|'.join(country_relative),regex=True)]
    data_world_evolution_relative = data_world_evolution_relative.pivot(index='Date', columns='Country/Region', values='Deaths/100k')\
                                     .reset_index()
    return data_world, data_world_pie_absolute, data_world_pie_relative, data_world_evolution_absolute, data_world_evolution_relative



data_world,\
data_world_pie_absolute, data_world_pie_relative,\
data_world_evolution_absolute, data_world_evolution_relative = initialize_world(data)




data_world_evolution_absolute_properties = {"x":"Date"}
cols = [col for col in data_world_evolution_absolute.columns if col != "Date"]
for i in range(len(cols)):
    data_world_evolution_absolute_properties[f'y[{i}]'] = cols[i]


data_world_evolution_relative_properties = {"x":"Date"}
cols = [col for col in data_world_evolution_relative.columns if col != "Date"]
for i in range(len(cols)):
    data_world_evolution_relative_properties[f'y[{i}]'] = cols[i]
    
    
world_md = Markdown("""
# **World**{: .color-primary} Statistics

<|{selected_type}|toggle|lov={type_selector}|>

<|layout|columns=1 1 1 1|gap=30px|
<|card m1|
#### **Deaths**{: .color-primary} <br/>
# <|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Deaths']))).replace(',', ' ')}|text|raw|>
|>

<|card m1|
#### **Recovered**{: .color-primary} <br/>
# <|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Recovered']))).replace(',', ' ')}|text|raw|>
|>

<|card m1|
#### **Confirmed**{: .color-primary} <br/>
# <|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Confirmed']))).replace(',', ' ')}|text|raw|>
|>
|>

<br/>

<|part|render={selected_type=='Absolute'}|
<|layout|columns=1 2|gap=30px|
<|{data_world_pie_absolute}|chart|type=pie|label=Country/Region|x=Deaths|>

<|{data_world_evolution_absolute}|chart|properties={data_world_evolution_absolute_properties}|>
|>
|>

<|part|render={selected_type=='Relative'}|
<|layout|columns=1 2|gap=30px|
<|{data_world_pie_relative}|chart|type=pie|label=Country/Region|x=Deaths/100k|>

<|{data_world_evolution_relative}|chart|properties={data_world_evolution_relative_properties}|>
|>
|>
""")