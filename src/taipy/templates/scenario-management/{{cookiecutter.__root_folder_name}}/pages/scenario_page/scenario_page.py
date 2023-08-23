from taipy.gui import Markdown

from .data_node_management import (
    custom_write_data_nodes,
    manage_inputs_partial,
    manage_outputs_partial,
    write_data_nodes,
)


def manage_data_node_partials(state):
    manage_inputs_partial(state)
    manage_outputs_partial(state)


def on_change(state, var, val):
    write_data_nodes(state, var, val)
    custom_write_data_nodes(state, var, val)


scenario_page = Markdown("pages/scenario_page/scenario_page.md")
