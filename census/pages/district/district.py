# Import required functions from utils.graphs module
from utils.graphs import bar_graph, overlayed_chart, radar_chart, pie_chart

# Import the dataset
from data.data import data as dataset

# Import Markdown component from Taipy GUI
from taipy.gui import Markdown

# Function to update state when district selection changes
def on_change_district(state):
    # Update bargraph data and layout
    state.bargraph_data, state.bargraph_layout = bar_graph(
        state.selected_district)

    # Update pie chart data
    state.pie_chart_data = pie_chart(state.selected_district)

    # Get district statistics (total population, male population, female population)
    state.total_population, state.total_male_population, state.total_female_population = getDistrictStats(
        state.selected_district)

    # Update overlayed chart data, labels, and options
    state.overlay_data, state.y_labels, state.options = overlayed_chart(
        state.selected_district)

    # Update radar chart data, options, and layout
    state.radar_data, state.radar_options, state.radar_layout = radar_chart(
        state.selected_district)

# Function to get district statistics


def getDistrictStats(district: str):
    # Filter dataset for the given district
    district_data = dataset[dataset['District'] == district]

    # Calculate total population, male population, and female population
    total_population = str(district_data['Total population'].sum())
    total_male_population = str(district_data['Total Male'].sum())
    total_female_population = str(district_data['Total Female'].sum())

    return total_population, total_male_population, total_female_population


# Get a list of unique districts from the dataset
district_list = dataset['District'].unique().tolist()

# Set the initially selected district to the first district in the list
selected_district = district_list[0]

# Get initial district statistics for the selected district
total_population, total_male_population, total_female_population = getDistrictStats(
    selected_district)

# Get initial data for various charts and graphs
bargraph_data, bargraph_layout = bar_graph(selected_district)
overlay_data, y_labels, options = overlayed_chart(selected_district)
radar_data, radar_options, radar_layout = radar_chart(selected_district)
pie_chart_data = pie_chart(selected_district)

# Create a Markdown component for the district page
district_md = Markdown("pages/district/district.md")
