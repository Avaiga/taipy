from taipy.gui import Gui


def test_invalid_control_name(gui: Gui, helpers):
    md_string = "<|invalid|invalid|>"
    expected_list = ["<Field", 'value="invalid"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_value_to_negated_property(gui: Gui, helpers):
    # Catch warning?
    md_string = "<|button|not active=true|>"
    expected_list = ["<Button", "active={false}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_invalid_property_value(gui: Gui, helpers):
    # Catch warning?
    md_string = "<|button|let's try that!|>"
    expected_list = ["<Button", 'label="&lt;Empty&gt;"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_unclosed_block(gui: Gui, helpers):
    # Catch warning?
    md_string = "<|"
    expected_list = ["<Part", "</Part>"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_opening_unknown_block(gui: Gui, helpers):
    # Catch warning?
    md_string = "<|unknown"
    expected_list = ["<div", "&lt;|unknown"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_closing_unknown_block(gui: Gui, helpers):
    # Catch warning?
    md_string = "|>"
    expected_list = ["<div>", "No matching opened tag", "</div>"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_md_link(gui: Gui, helpers):
    # Catch warning?
    md_string = "[content](link)"
    expected_list = ["<a", 'href="link"', "content</a>"]
    helpers.test_control_md(gui, md_string, expected_list)
