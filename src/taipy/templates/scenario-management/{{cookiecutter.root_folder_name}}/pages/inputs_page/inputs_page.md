<|part|

<|part|render={not selected_scenario}|
<center> No scenario selected. </center>
|>

<|part|render={selected_scenario}|

<|part|partial={inputs_partial}|>

<|submit scenario|button|on_action={submit(selected_scenario)}|active={is_ready_to_run(selected_scenario)}|>

|>

|>
