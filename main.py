from taipy.gui import Gui

district = """
# **District**{: .color-primary} Statistics

<|layout|columns=1 1 1|

<|{selected_district}|selector|lov={district_list}|dropdown|>

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

<|Graph goes here|text|class_name=h1|>
"""

district_list = ['KTM', 'PKR']
selected_district = 'KTM'

pages = {
    "/": "<center><|toggle|theme|><|navbar|></center>",
    "District": district,
    "Nepal": "Nepal",
    "Map": "Map"
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
