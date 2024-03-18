<|toggle|theme|>
<|navbar|lov={[("/insights", "🌏 Insights"), ("/country_overview", "🎄 Country Population"), ("/top_countries_in_continent", "💯 Top Countries in Continent"), ("/compare_countries", "⚡ Compare Countries"), ("/pie_charts", "🥧 Pie Charts"), ("/total_population", "➕ Total"), ("/dataset", "📅 Explore Dataset")]}|>
<|container|

# 🥧 World **Population**{: .color-primary} Pie Exploration!
<br />
<|1 1|layout|

### Choose **Year**{: .color-primary}!

<|{year}|selector|lov={YEARS}|dropdown|on_change=update_year|>

|>

<br />
### **<|{year}|text|raw=True|>**{: .color-primary} Population!

<|{pie_data}|chart|type=pie|values=Population|options={pie_options}|labels=Country|>
|>
