# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_code_block_styling_light_mode(page: "Page", gui: Gui, helpers):
    """Test that code blocks have default styling in light mode"""
    markdown_content = """
<|# Code Block Test

Here is some `inline code` in the text.

And here is a code block:

```python
def hello():
    return "world"
```
|id=text1|mode=md|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page("test_page", markdown_content)
    helpers.run_e2e(gui)
    page.goto("./test_page")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    
    # Wait for code element to be rendered
    page.wait_for_selector("code")
    
    # Check inline code has background color
    inline_code_bg = page.evaluate(
        'window.getComputedStyle(document.querySelector("code"), null).getPropertyValue("background-color")'
    )
    assert inline_code_bg != "rgba(0, 0, 0, 0)", "Inline code should have a background color"
    
    # Check inline code has monospace font
    inline_code_font = page.evaluate(
        'window.getComputedStyle(document.querySelector("code"), null).getPropertyValue("font-family")'
    )
    assert "consolas" in inline_code_font.lower() or "monaco" in inline_code_font.lower() or "courier" in inline_code_font.lower(), \
        "Inline code should use a monospace font"
    
    # Check pre element if it exists (code block)
    pre_elements = page.query_selector_all("pre")
    if len(pre_elements) > 0:
        pre_bg = page.evaluate(
            'window.getComputedStyle(document.querySelector("pre"), null).getPropertyValue("background-color")'
        )
        assert pre_bg != "rgba(0, 0, 0, 0)", "Code block should have a background color"
        
        pre_padding = page.evaluate(
            'window.getComputedStyle(document.querySelector("pre"), null).getPropertyValue("padding")'
        )
        assert pre_padding != "0px", "Code block should have padding"


@pytest.mark.teste2e
def test_code_block_styling_dark_mode(page: "Page", gui: Gui, helpers):
    """Test that code blocks have default styling in dark mode"""
    markdown_content = """
<|# Code Block Test

Here is some `inline code` in the text.

```javascript
console.log("test");
```
|id=text1|mode=md|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page("test_page", markdown_content)
    helpers.run_e2e(gui, dark_mode=True)
    page.goto("./test_page")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    
    # Wait for dark mode to be applied
    page.wait_for_selector(".taipy-dark")
    
    # Wait for code element
    page.wait_for_selector("code")
    
    # Check that code has styling
    inline_code_bg = page.evaluate(
        'window.getComputedStyle(document.querySelector("code"), null).getPropertyValue("background-color")'
    )
    assert inline_code_bg != "rgba(0, 0, 0, 0)", "Inline code should have a background color in dark mode"


@pytest.mark.teste2e  
def test_code_block_in_chat(page: "Page", gui: Gui, helpers):
    """Test that code blocks in chat messages have proper styling"""
    chat_messages = [
        ["1", "Show me a Python example", "user"],
        ["2", "Here's an example:\n\n```python\ndef greet():\n    print('Hello')\n```", "assistant"],
    ]
    
    page_content = '<|{chat_messages}|chat|id=chat1|>'
    
    gui._set_frame(inspect.currentframe())
    gui.add_page("test_page", page_content)
    helpers.run_e2e(gui)
    page.goto("./test_page")
    page.expect_websocket()
    page.wait_for_selector("#chat1")
    
    # Wait for markdown to render in chat
    page.wait_for_selector("code", timeout=5000)
    
    # Verify code block has styling
    code_font = page.evaluate(
        'window.getComputedStyle(document.querySelector("code"), null).getPropertyValue("font-family")'
    )
    assert "consolas" in code_font.lower() or "monaco" in code_font.lower() or "courier" in code_font.lower(), \
        "Code in chat should use monospace font"


@pytest.mark.teste2e
def test_pre_mode_styling(page: "Page", gui: Gui, helpers):
    """Test that pre mode text component has proper styling"""
    pre_content = """def example():
    x = 42
    return x"""
    
    page_content = '<|{pre_content}|id=pre1|mode=pre|>'
    
    gui._set_frame(inspect.currentframe())
    gui.add_page("test_page", page_content)
    helpers.run_e2e(gui)
    page.goto("./test_page")
    page.expect_websocket()
    page.wait_for_selector("#pre1")
    
    # Check pre element has background
    pre_bg = page.evaluate(
        'window.getComputedStyle(document.querySelector("#pre1"), null).getPropertyValue("background-color")'
    )
    assert pre_bg != "rgba(0, 0, 0, 0)", "Pre mode should have background color"
    
    # Check pre element has monospace font
    pre_font = page.evaluate(
        'window.getComputedStyle(document.querySelector("#pre1"), null).getPropertyValue("font-family")'
    )
    assert "consolas" in pre_font.lower() or "monaco" in pre_font.lower() or "courier" in pre_font.lower(), \
        "Pre mode should use monospace font"


@pytest.mark.teste2e
def test_code_styling_can_be_overridden(page: "Page", gui: Gui, helpers):
    """Test that default code block styling can be overridden with custom CSS"""
    markdown_content = '<|`custom code`|id=text1|mode=md|>'
    custom_style = """
code {
    background-color: rgb(255, 0, 0) !important;
}
"""
    
    gui._set_frame(inspect.currentframe())
    gui.add_page("test_page", markdown_content, style=custom_style)
    helpers.run_e2e(gui)
    page.goto("./test_page")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    page.wait_for_selector("code")
    
    # Check that custom style is applied
    code_bg = page.evaluate(
        'window.getComputedStyle(document.querySelector("code"), null).getPropertyValue("background-color")'
    )
    assert code_bg == "rgb(255, 0, 0)", "Custom style should override default code styling"


