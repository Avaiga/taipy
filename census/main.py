# Import the Gui class from the taipy.gui module
from taipy.gui import Gui

# Import the Python modules representing different pages/components of the web application
from pages.root import root_md
from pages.district.district import district_md
from pages.dataset.dataset import dataset_md
from pages.nepal.nepal import nepal_md
from pages.collect_data.collect_data import collect_data_md
from pages.map.map import map_md

# Create a dictionary mapping URLs to their corresponding Python modules
pages = {
    "/": root_md,  # Root URL mapped to root_md module
    "district": district_md,  # "district" URL mapped to district_md module
    "nepal": nepal_md,  # "nepal" URL mapped to nepal_md module
    "map": map_md,  # "map" URL mapped to map_md module
    "dataset": dataset_md,  # "dataset" URL mapped to dataset_md module
    # "collect_data" URL mapped to collect_data_md module
    "collect_data": collect_data_md,
}

# Check if the script is being run as the main program
if __name__ == "__main__":
    # Create an instance of the Gui class, passing in the pages dictionary
    # Start the Taipy web server and serve the web application
    Gui(pages=pages).run(
        title="From Taipy Quine Quest-007",  # Set the title of the web application
        use_reloader=True  # Enable auto-reloading when source files are modified
    )
