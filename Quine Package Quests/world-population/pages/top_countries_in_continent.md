<|toggle|theme|>
<|navbar|lov={[("/insights", "🌏 Insights"), ("/country_overview", "🎄 Country Population"), ("/top_countries_in_continent", "💯 Top Countries in Continent"), ("/compare_countries", "⚡ Compare Countries"), ("/pie_charts", "🥧 Pie Charts"), ("/total_population", "➕ Total"), ("/dataset", "📅 Explore Dataset")]}|>
<|container|

# 💯 Top **Countries**{: .color-primary} Population in **Continent**{: .color-primary}!

<|1 1|layout|

### Choose **Continent**{: .color-primary}!

<|{continent}|selector|lov={CONTINENTS}|dropdown|on_change=on_selection|>

### Choose **Year**{: .color-primary}!

<|{year}|selector|lov={YEARS}|dropdown|on_change=on_selection|>
|>
<br />
<|{chart_data}|chart|type=bar|x=Countries/Territories|y=Population|>
|>
