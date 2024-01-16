# **World**{: .color-primary} Statistics

<br/>
<|layout|columns=1 1 1 1|gap=50px|
<|card|
**Deaths**{: .color-primary}
<|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Deaths']))).replace(',', ' ')}|text|class_name=h2|>
|>

<|card|
**Recovered**{: .color-primary}
<|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Recovered']))).replace(',', ' ')}|text|class_name=h2|>
|>

<|part|class_name=card|
**Confirmed**{: .color-primary}
<|{'{:,}'.format(int(np.sum(data_world_pie_absolute['Confirmed']))).replace(',', ' ')}|text|class_name=h2|>
|>
|>

<br/>

<|{selected_type}|toggle|lov={type_selector}|>

<|part|render={selected_type=='Absolute'}|
<|layout|columns=1 2|
<|{data_world_pie_absolute}|chart|type=pie|labels=Country/Region|values=Deaths|title=Distribution around the World|>

<|{data_world_evolution_absolute}|chart|properties={data_world_evolution_absolute_properties}|title=Evolution around the World|>
|>
|>

<|part|render={selected_type=='Relative'}|
<|layout|columns=1 2|
<|{data_world_pie_relative}|chart|type=pie|labels=Country/Region|values=Deaths/100k|>

<|{data_world_evolution_relative}|chart|properties={data_world_evolution_relative_properties}|>
|>
|>
