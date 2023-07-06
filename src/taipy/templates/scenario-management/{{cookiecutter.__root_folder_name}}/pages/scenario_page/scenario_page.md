<|part|render={selected_scenario}|

<| Selected scenario |expandable|

<|layout|columns=1 1|
<|{selected_scenario}|scenario|not expandable|expanded|>

<|{selected_scenario}|scenario_dag|>
|>

|>


<|layout|columns=1 1|

<input|card|
## Input
<|part|partial={inputs_partial}|>
|input>

<output|card|
## Output
<|part|partial={outputs_partial}|>
|output>

|>

|>
