from utils.graphs import bubble_chart_whole, treemap_whole, bar_graph_whole, overlayed_chart_whole

from data.data import data as dataset

from taipy.gui import Markdown


def getNepalStats():
    total_population = str(dataset['Total population'].sum())
    total_male_population = str(dataset['Total Male'].sum())
    total_female_population = str(dataset['Total Female'].sum())

    return total_population, total_male_population, total_female_population


total_population, total_male_population, total_female_population = getNepalStats()

bubble_chart_whole_data, bubble_chart_whole_marker, bubble_chart_whole_layout = bubble_chart_whole()
bargraph_data_whole, bargraph_layout_whole = bar_graph_whole()
overlay_data_whole, overlay_y_labels_whole, overlay_options_whole = overlayed_chart_whole()
treemaps_data = treemap_whole()

nepal_md = Markdown("pages/nepal/nepal.md")
