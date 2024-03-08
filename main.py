from taipy.gui import Gui
from data.data import data as dataset
from pages.root import root_md
from pages.district.district import district_md

from pages.nepal.nepal import nepal_md

table = dataset.to_dict()

dataset_md = """
# Preliminary Data of **National Population**{:.color-primary} and **Housing Census 2021**{:.color-primary}

### <center>**Source**: [Open Data Nepal](https://opendatanepal.com/dataset/preliminary-data-of-national-population-and-housing-census-2021)</center>

<center>
<|{table}|table|class_name=m1 rows-bordered rows-similar|filter=True|rebuild|page_size=50|width=90%|>
</center>

"""
pages = {
    "/": root_md,
    "district": district_md,
    "nepal": nepal_md,
    "map": "Map",
    "dataset": dataset_md
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
