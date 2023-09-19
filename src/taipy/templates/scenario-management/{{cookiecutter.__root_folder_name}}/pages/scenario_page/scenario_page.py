from taipy.gui import Markdown

from .data_node_management import manage_partial


def manage_data_node_partial(state):
    manage_partial(state)

scenario_page = Markdown("pages/scenario_page/scenario_page.md")
