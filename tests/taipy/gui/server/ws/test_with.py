from taipy.gui import Gui


def test_sending_messages_in_group(gui: Gui, helpers):
    gui.bind_var_val("name", "World!")
    gui.bind_var_val("btn_id", "button1")
    md_string = "<|Hello {name}|button|id={btn_id}|>"
    with gui as aGui:
        setattr(aGui, "name", "Monde!")
        setattr(aGui, "btn_id", "button2")
    expected_list = ["<Button", 'defaultLabel="Hello Monde!"', 'id="button1"', "label={tp_Hello_name"]
    helpers.test_control_md(gui, md_string, expected_list)
