from taipy.gui import Markdown
import plotly.graph_objects as go

from data.data import data
pi_data = data.groupby('continent')
continent = []
continent_count_earthquake = []
for (name, group) in pi_data:
    continent.append(name)
    continent_count_earthquake.append(len(group))
total_earthquake = len(data)
fig = go.Figure(data=[go.Pie(labels=continent, values=continent_count_earthquake)])

world_md = Markdown("pages/world/world.md")
