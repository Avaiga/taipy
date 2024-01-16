from taipy.gui import Markdown
import numpy as np

import json

from data.data import data


type_selector = ['Absolute', 'Relative']
selected_type = type_selector[0]


def initialize_world(data):
    data_world = data.groupby(["Country/Region",
                                    'Date'])\
                            .sum()\
                            .reset_index()

    with open("data/pop.json","r") as f:                    
        pop = json.load(f)
    
    data_world['Population'] = data_world['Country/Region'].map(lambda x: pop.get(x, [None, 0])[1])

    data_world = data_world.dropna()\
                            .reset_index()
    data_world['Deaths/100k'] = data_world.loc[:,'Deaths']/data_world.loc[:,'Population']*100000
    
    data_world_pie_absolute = data_world[['Country/Region', 'Deaths', 'Recovered', 'Confirmed']].groupby(["Country/Region"])\
                                        .max()\
                                        .sort_values(by='Deaths', ascending=False)[:20]\
                                        .reset_index()
                                
    data_world_pie_relative = data_world[['Country/Region', 'Deaths/100k']].groupby(["Country/Region"])\
                                        .max()\
                                        .sort_values(by='Deaths/100k', ascending=False)[:20]\
                                        .reset_index()
    
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
    
    
world_md = Markdown("pages/world/world.md")