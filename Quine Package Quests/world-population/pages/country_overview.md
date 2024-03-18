<|toggle|theme|>
<|navbar|lov={[("/insights", "🌏 Insights"), ("/country_overview", "🎄 Country Population"), ("/top_countries_in_continent", "💯 Top Countries in Continent"), ("/compare_countries", "⚡ Compare Countries"), ("/pie_charts", "🥧 Pie Charts"), ("/total_population", "➕ Total"), ("/dataset", "📅 Explore Dataset")]}|>
<|container|

# 🎄 Country **Population**{: .color-primary} Overview!

<|1 1|layout|

### Choose **Country**{: .color-primary} to **Explore**{: .color-primary}!

<br />
<|{country}|selector|lov={COUNTRIES}|dropdown|on_change=on_selection|label=Choose Country To Explore!|>
|>

#### Population **Increase**{: .color-primary}!

<|{LINE_GRAPH_DATA}|chart|y=Population|x=Years|color=#ff6049|>

#### Country **Information**{: .color-primary}

<|container|

<|{country_info_data}|table|show_all|>

|>

|>
