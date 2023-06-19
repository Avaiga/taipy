"""
The data management page of the application.
Page content is imported from the data.md file.

Please refer to https://docs.taipy.io/en/latest/manuals/gui/pages for more details.
"""

from taipy.gui import Markdown, notify

input_csv_file = None
replacement_type = "NO VALUE"
results = None
inputs = None


def on_clean_data(state):
    state.scenario.submit(wait=True)
    state.is_scenario_computed = True
    state.results = state.scenario.cleaned_dataset.read()
    notify(state, message=f"csv file has been cleaned for scenario {state.scenario.get_simple_label()}`")


def drop_csv(state):
    state.scenario.initial_dataset.path = state.input_csv_file
    state.inputs = state.scenario.initial_dataset.read()
    notify(
        state, message=f"csv file `{state.input_csv_file}` loaded for scenario `{state.scenario.get_simple_label()}`"
    )


data_page = Markdown("pages/data/data.md")
