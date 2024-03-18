# **Nepal**{: .color-primary} Statistics

<br/>

<|layout|columns= 1 1 1 1|gap=100px|class_name=m1|

<|card|
**Total Population**{:.color-primary}
<|{total_population}|text|class_name=h2|>
|>

<|card|
**Total Male Population**{:.color-primary}
<|{total_male_population}|text|class_name=h2|>
|>

<|card|
**Total Female Population**{:.color-primary}
<|{total_female_population}|text|class_name=h2|>
|>

|>

<br/>

# Visualization in **Graphs**{:.color-primary}

<|{bargraph_data_whole}|chart|type=bar|x=District|y[1]=Total Male|y[2]=Total Female|layout={bargraph_layout_whole}|class_name=m2|>

<|layout|columns=1 1|class_name=m2|

<|{bubble_chart_whole_data}|chart|mode=markers|x=Total Male|y=Total Female|marker={bubble_chart_whole_marker}|text=Texts|>

<|{treemaps_data}|chart|type=treemap|labels=label|values=values|>

|>

<|{overlay_data_whole}|chart|mode=none|x=District|y={overlay_y_labels_whole}|options={overlay_options_whole}|>
