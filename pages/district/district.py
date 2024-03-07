from utils.graphs import bar_graph, overlayed_chart, radar_chart, pie_chart

from data.data import data as dataset

from taipy.gui import Markdown


def on_change_district(state):
    state.bargraph_data, state.bargraph_layout = bar_graph(
        state.selected_district)
    state.pie_chart_data = pie_chart(
        state.selected_district)
    state.total_population, state.total_male_population, state.total_female_population = getDistrictStats(
        state.selected_district)
    state.overlay_data, state.y_labels, state.options = overlayed_chart(
        state.selected_district)
    state.radar_data, state.radar_options, state.radar_layout = radar_chart(
        state.selected_district)


def getDistrictStats(district: str):
    district_data = dataset[dataset['District'] == district]

    # Calculate total population, male population, and female population
    total_population = str(district_data['Total population'].sum())
    total_male_population = str(district_data['Total Male'].sum())
    total_female_population = str(district_data['Total Female'].sum())

    return total_population, total_male_population, total_female_population


district_list = dataset['District'].unique().tolist()
selected_district = district_list[0]


total_population, total_male_population, total_female_population = getDistrictStats(
    selected_district)

bargraph_data, bargraph_layout = bar_graph(selected_district)
overlay_data, y_labels, options = overlayed_chart(selected_district)
radar_data, radar_options, radar_layout = radar_chart(selected_district)
pie_chart_data = pie_chart(selected_district)


district_md = Markdown("pages/district/district.md")
