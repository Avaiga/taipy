<|layout|columns=1 1|

<|part|render={selected_scenario}|

<|{selected_scenario}|scenario|not expandable|expanded|on_submission_change=notify_on_submission|>

<|{selected_scenario}|scenario_dag|>
|>

<|part|partial={data_node_partial}|render={selected_data_node}|>

|>
