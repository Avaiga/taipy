from taipy.gui import Gui, notify
from graphs import bar_graph, bubble_chart
from data.data import data as dataset


def on_change_district(state):
    state.bargraph_data, state.bargraph_layout = bar_graph(
        state.selected_district)
    state.bubble_chart_data, state.bubble_chart_marker = bubble_chart(
        state.selected_district)


district = """
# **District**{: .color-primary} Statistics

<|layout|columns=1 1 1|

<|{selected_district}|selector|lov={district_list}|on_change=on_change_district|dropdown|>

|>

<br/>


<|layout|columns= 1 1 1|gap=100px|

<|card|
**Total Population**{:.color-primary}
<|50000|text|class_name=h2|>
|>

<|card|
**Total Population**{:.color-primary}
<|50000|text|class_name=h2|>
|>

<|card|
**Total Population**{:.color-primary}
<|50000|text|class_name=h2|>
|>

|>

<br/>

# Visualization in **Graphs**{: .color-primary} 

<|layout|columns=1 1|gap=100px|

<|{bargraph_data}|chart|type=bar|x=Local Level Name|y[1]=Total Male|y[2]=Total Female|layout={bargraph_layout}|>

<|{bubble_chart_data}|chart|mode=markers|x=Total Male|y=Total Female|marker={bubble_chart_marker}|text=Texts|>

|>
"""

district_list = dataset['District'].unique().tolist()
selected_district = district_list[0]

bargraph_data, bargraph_layout = bar_graph('Taplejung')
bubble_chart_data, bubble_chart_marker = bubble_chart(
    'Taplejung')


pages = {
    "/": "<center><|toggle|theme|><|navbar|></center>",
    "District": district,
    "Nepal": "Nepal",
    "Map": "Map"
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
