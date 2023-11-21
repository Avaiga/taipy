from taipy.gui import Markdown, notify

from .data_node_management import manage_partial


def notify_on_submission(state, submitable, details):
    if details["submission_status"] == "COMPLETED":
        notify(state, "success", "Submision completed!")
    elif details["submission_status"] == "FAILED":
        notify(state, "error", "Submission failed!")
    else:
        notify(state, "info", "In progress...")


def manage_data_node_partial(state):
    manage_partial(state)


scenario_page = Markdown("pages/scenario_page/scenario_page.md")
