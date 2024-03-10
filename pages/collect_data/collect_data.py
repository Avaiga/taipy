from data.data import data as dataset
from taipy.gui import Markdown


district_list = dataset['District'].unique().tolist()
selected_district = district_list[0]

local_level_name_list = dataset[
    dataset['District'] == selected_district]['Local Level Name'].to_list()
selected_local_level = local_level_name_list[0]

male_population = 0
female_population = 0
household_member = 0
family_member = 0


def on_change_district(state):
    state.local_level_name_list = dataset[
        dataset['District']
        == state.selected_district
    ]["Local Level Name"].to_list()
    state.selected_local_level = state.local_level_name_list[0]

    state.male_population = 0
    state.female_population = 0
    state.household_member = 0
    state.family_member = 0


collect_data_md = Markdown("pages/collect_data/collect_data.md")
