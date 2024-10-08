from taipy.gui import Gui, State

# Initial values for the AlertComponent
alert_message = "This is an alert message!"
alert_severity = "info"  # Options: "error", "warning", "info", "success"
alert_variant = "filled"  # Options: "filled", "outlined", "standard"

# Markdown definition for the AlertComponent
md = """
# Alert Component Test

## Current Alert:
<|{alert_message}|alert|severity={alert_severity}|variant={alert_variant}|>

### Update Alert Message:
<|{alert_message}|input|label=Alert Message|on_change=on_change|>

### Select Alert Severity:
<|{alert_severity}|selector|lov=error;warning;info;success|label=Select Severity|on_change=on_change|>

### Select Alert Variant:
<|{alert_variant}|selector|lov=filled;outlined;standard|label=Select Variant|on_change=on_change|>
"""

# Callback function to handle dynamic changes to the AlertComponent
def on_change(state: State, var_name: str, value: str):
    print(f"{var_name} changed to: {value}")
    if var_name == "alert_message":
        state.alert_message = value
    elif var_name == "alert_severity":
        state.alert_severity = value
    elif var_name == "alert_variant":
        state.alert_variant = value

# Run the GUI
Gui(md).run()
