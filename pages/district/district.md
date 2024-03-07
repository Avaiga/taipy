# **District**{: .color-primary} Statistics

<|layout|columns=1 1 1|

<|{selected_district}|selector|lov={district_list}|on_change=on_change_district|dropdown|class_name=m1|>

|>

<br/>

<|layout|columns= 1 1 1|gap=100px|class_name=m1|

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

<|layout|columns=1 1|gap=100px|class_name=m2|

<|{bargraph_data}|chart|type=bar|x=Local Level Name|y[1]=Total Male|y[2]=Total Female|layout={bargraph_layout}|>

<|{pie_chart_data}|chart|type=pie|values=values|labels=labels|>

|>

<br/>

<|layout|columns=1 1|gap=100px|class_name=m2|

<|{overlay_data}|chart|mode=none|x=Local Level Name|y={y_labels}|options={options}|>

<|{radar_data}|chart|type=scatterpolar|r=r|theta=theta|options={radar_options}|layout={radar_layout}|>

|>
