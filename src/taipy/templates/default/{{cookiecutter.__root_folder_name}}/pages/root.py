"""
The rootpage of the application.
Page content is imported from the root.md file.

Please refer to https://docs.taipy.io/en/latest/manuals/gui/pages for more details.
"""

from taipy.gui import Markdown

root_page = Markdown("pages/root.md")
