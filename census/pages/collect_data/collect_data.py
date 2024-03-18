# Import the dataset
from data.data import data as dataset

# Import the Markdown component from Taipy GUI
from taipy.gui import Markdown

# Get a list of unique districts from the dataset
district_list = dataset['District'].unique().tolist()

# Set the initially selected district to the first district in the list
selected_district = district_list[0]

# Get a list of local level names for the initially selected district
local_level_name_list = dataset[dataset['District'] == selected_district]['Local Level Name'].to_list()

# Set the initially selected local level to the first local level in the list
selected_local_level = local_level_name_list[0]

# Initialize variables to store population and family/household data
male_population = 0
female_population = 0
household_member = 0
family_member = 0

# Function to update state when district selection changes
def on_change_district(state):
   # Update the list of local level names based on the selected district
   state.local_level_name_list = dataset[dataset['District'] == state.selected_district]["Local Level Name"].to_list()
   
   # Set the selected local level to the first local level in the updated list
   state.selected_local_level = state.local_level_name_list[0]
   
   # Reset population and family/household data
   state.male_population = 0
   state.female_population = 0
   state.household_member = 0
   state.family_member = 0

# Create a Markdown component for the collect data page
collect_data_md = Markdown("pages/collect_data/collect_data.md")