<|part|render={selected_scenario}|

<| Selected scenario |expandable|

<|layout|columns=1 1|

<|{selected_scenario}|scenario|not expandable|expanded|>

<|{selected_scenario}|scenario_dag|>

|>

|>


<|layout|columns=1 1|

<|card|
<|part|partial={inputs_section_partial}|>
|>

<|card|
<|part|partial={outputs_section_partial}|>
|>

|>

|>
