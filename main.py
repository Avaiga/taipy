from taipy.gui import Gui

from pages.root import root_md
from pages.district.district import district_md
from pages.dataset.dataset import dataset_md
from pages.nepal.nepal import nepal_md


pages = {
    "/": root_md,
    "district": district_md,
    "nepal": nepal_md,
    "map": "Map",
    "dataset": dataset_md
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="From Taipy Quine Quest-007", use_reloader=True)
