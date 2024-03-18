# Import required functions from utils.graphs module
from utils.graphs import bubble_chart_whole, treemap_whole, bar_graph_whole, overlayed_chart_whole

# Import the dataset
from data.data import data as dataset

# Import Markdown component from Taipy GUI
from taipy.gui import Markdown

# Function to get overall Nepal statistics
def getNepalStats():
   # Calculate total population, male population, and female population for the entire dataset
   total_population = str(dataset['Total population'].sum())
   total_male_population = str(dataset['Total Male'].sum())
   total_female_population = str(dataset['Total Female'].sum())

   return total_population, total_male_population, total_female_population

# Get overall Nepal statistics
total_population, total_male_population, total_female_population = getNepalStats()

# Get data and layout for various charts and graphs for the entire Nepal
bubble_chart_whole_data, bubble_chart_whole_marker, bubble_chart_whole_layout = bubble_chart_whole()
bargraph_data_whole, bargraph_layout_whole = bar_graph_whole()
overlay_data_whole, overlay_y_labels_whole, overlay_options_whole = overlayed_chart_whole()
treemaps_data = treemap_whole()

# Create a Markdown component for the Nepal page
nepal_md = Markdown("pages/nepal/nepal.md")