from taipy.gui import Markdown

from .folder1.content1 import a, update_a  # noqa: F401
from .folder1.content2 import *  # noqa: F403

page = Markdown(
"""
<|{a}|id=num_a|>
<|btna|button|on_action=update_a|id=btn_a|>
<|{b}|id=num_b|>
<|btnb|button|on_action=update_b|id=btn_b|>
"""
)

