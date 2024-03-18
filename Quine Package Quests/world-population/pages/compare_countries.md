<|toggle|theme|>
<|navbar|lov={[("/insights", "🌏 Insights"), ("/country_overview", "🎄 Country Population"), ("/top_countries_in_continent", "💯 Top Countries in Continent"), ("/compare_countries", "⚡ Compare Countries"), ("/pie_charts", "🥧 Pie Charts"), ("/total_population", "➕ Total"), ("/dataset", "📅 Explore Dataset")]}|>
<|container|

# ⚡ Compare **Countries**{: .color-primary} Population!

<|1 1|layout|

### Choose **1st**{: .color-primary} Country!

<|{country1}|selector|lov={COUNTRIES}|dropdown|on_change=choose_country|>

### Choose **2nd**{: .color-primary} Country!

<|{country2}|selector|lov={COUNTRIES}|dropdown|on_change=choose_country|>
|>
<br />

<|{LINE_GRAPH_DATA}|chart|mode=lines|x=Years|y[1]=Country1|y[2]=Country2|y[3]=World Average|line[1]=longdash|line[2]=longdashdot|line[3]=dot|>

|>
