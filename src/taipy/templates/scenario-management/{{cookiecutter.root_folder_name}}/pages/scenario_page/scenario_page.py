from taipy.gui import Markdown, notify


def on_clean_data(state):
    state.scenario.submit(wait=True)
    state.results = state.scenario.cleaned_dataset.read()
    notify(state, message=f"csv file has been cleaned for scenario {state.scenario.get_simple_label()}`")


def drop_csv(state):
    state.scenario.initial_dataset.path = state.input_csv_file
    state.inputs = state.scenario.initial_dataset.read()
    notify(state, message=f"csv file `{state.input_csv_file}` loaded for scenario `{state.scenario.get_simple_label()}`")


scenario_page = Markdown("pages/scenario_page/scenario_page.md")
