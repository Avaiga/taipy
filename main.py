from taipy.gui import Gui, notify
from graphs import bar_graph, bubble_chart, overlayed_chart, radar_chart
from data.data import data as dataset


def on_change_district(state):
    state.bargraph_data, state.bargraph_layout = bar_graph(
        state.selected_district)
    state.bubble_chart_data, state.bubble_chart_marker = bubble_chart(
        state.selected_district)
    state.total_population, state.total_male_population, state.total_female_population = getDistrictStats(
        state.selected_district)
    state.overlay_data, state.y_labels, state.options = overlayed_chart(
        state.selected_district)
    state.radar_data, state.radar_options, state.radar_layout = radar_chart(
        state.selected_district)


def getDistrictStats(district: str):
    district_data = dataset[dataset['District'] == district]

    # Calculate total population, male population, and female population
    total_population = str(district_data['Total population'].sum())
    total_male_population = str(district_data['Total Male'].sum())
    total_female_population = str(district_data['Total Female'].sum())

    return total_population, total_male_population, total_female_population


district = """
# **District**{: .color-primary} Statistics

<|layout|columns=1 1 1|

<|{selected_district}|selector|lov={district_list}|on_change=on_change_district|dropdown|>

|>

<br/>


<|layout|columns= 1 1 1|gap=100px|

<|card|
**Total Population**{:.color-primary}
<|{total_population}|text|class_name=h2|>
|>

<|card|
**Total Population**{:.color-primary}
<|{total_male_population}|text|class_name=h2|>
|>

<|card|
**Total Population**{:.color-primary}
<|{total_female_population}|text|class_name=h2|>
|>

|>

<br/>

# Visualization in **Graphs**{:.color-primary} 

<|layout|columns=1 1|gap=100px|class_name=m2|

<|{bargraph_data}|chart|type=bar|x=Local Level Name|y[1]=Total Male|y[2]=Total Female|layout={bargraph_layout}|>

<|{bubble_chart_data}|chart|mode=markers|x=Total Male|y=Total Female|marker={bubble_chart_marker}|text=Texts|>

|>

<br/>

<|layout|columns=1 1|gap=100px|class_name=m2|

<|{overlay_data}|chart|mode=none|x=Local Level Name|y={y_labels}|options={options}|>

<|{radar_data}|chart|type=scatterpolar|r=r|theta=theta|options={radar_options}|layout={radar_layout}|>

|>
"""
district_list = dataset['District'].unique().tolist()
selected_district = district_list[0]


total_population, total_male_population, total_female_population = getDistrictStats(
    selected_district)

bargraph_data, bargraph_layout = bar_graph(selected_district)
bubble_chart_data, bubble_chart_marker = bubble_chart(selected_district)
overlay_data, y_labels, options = overlayed_chart(selected_district)
radar_data, radar_options, radar_layout = radar_chart(selected_district)

pages = {
    "/": "<center><|toggle|theme|><|navbar|></center>",
    "District": district,
    "Nepal": "Nepal",
    "Map": "Map"
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
