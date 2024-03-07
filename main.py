from taipy.gui import Gui

from utils.graphs import bubble_chart_whole

from pages.root import root_md
from pages.district.district import district_md

nepal = """
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

<|layout|columns=1 1|class_name=m2|


|>
"""

total_population, total_male_population, total_female_population = (
    1000, 1000, 1000)

pages = {
    "/": root_md,
    "district": district_md,
    "nepal": nepal,
    "map": "Map"
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
