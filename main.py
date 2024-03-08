from taipy.gui import Gui
from data.data import data as dataset

from pages.root import root_md
from pages.district.district import district_md
from pages.dataset.dataset import dataset_md
from pages.nepal.nepal import nepal_md


collect_data_md = """

# <center> **Collect Data**{:.color-primary} for National Population and Housing Census</center>


<br/>

<|container|

<input|class_name=card|

<|layout|columns= 1 1|gap=30px|

<district|
## **District**{:.color-primary}
<|{selected_district}|selector|lov={district_list}|on_change=on_change_district|dropdown|>
|district>

<local_level_name|
## **Local Level Name**{:.color-primary}
<|{selected_local_level}|selector|lov={local_level_name_list}|dropdown|>
|local_level_name>

|>

<|layout|columns=1 1 1 1|gap=10px|

<male|
## **Male**{: .color-primary} Population

<|{male_population}|input|label=Total Male Population|>
|male>

<female|
## **Female**{: .color-primary} Population

<|{female_population}|input|label=Total Female Population|>
|female>

<household|
## **Household**{: .color-primary} Number

<|{household_member}|input|label=Total Household Number|>
|household>

<family|
## **Family**{: .color-primary} Member

<|{household_member}|input|label=Total Family Member|>
|family>

|>

|input>

|>

<center>
<|Submit Data|button|class_name= m4 p1|>
</center>
"""

district_list = dataset['District'].unique().tolist()
selected_district = district_list[0]

local_level_name_list = dataset[
    dataset['District'] == selected_district]['Local Level Name'].to_list()
selected_local_level = local_level_name_list[0]

male_population = 0
female_population = 0
household_member = 0
household_member = 0


def on_change_district(state):
    state.local_level_name_list = dataset[
        dataset['District']
        == state.selected_district
    ]["Local Level Name"].to_list()
    state.selected_local_level = state.local_level_name_list[0]

    state.male_population = 0
    state.female_population = 0
    state.household_member = 0
    state.household_member = 0


pages = {
    "/": root_md,
    "district": district_md,
    "nepal": nepal_md,
    "map": "Map",
    "dataset": dataset_md,
    "collect_data": collect_data_md
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
