  
  
<|layout|columns=2 9|gap=50px|
<sidebar|sidebar|
**Scenario** Creation

<|{selected_scenario}|scenario_selector|>
|sidebar>

<scenario|part|render={selected_scenario}|
# **Prediction**{: .color-primary} page

<|1 1|layout|
<date|
#### First **day**{: .color-primary} of prediction

<|{selected_date}|date|on_change=on_change_params|>
|date>

<country|
#### **Country**{: .color-primary} of prediction

<|{selected_country}|selector|lov={selector_country}|dropdown|on_change=on_change_params|label=Country|>
|country>
|>

<|{selected_scenario}|scenario|on_submission_change=on_submission_change|not expanded|>

---------------------------------------

## **Predictions**{: .color-primary} and explorer of data nodes

<|{selected_scenario.result.read() if selected_scenario and selected_scenario.result.read() is not None else default_result}|chart|x=Date|y[1]=Deaths|y[2]=Linear Regression|y[3]=ARIMA|type[1]=bar|title=Predictions|>


<|Data Nodes|expandable|
<|1 5|layout|
<|{selected_data_node}|data_node_selector|> 

<|{selected_data_node}|data_node|>
|>
|>

|scenario>
|>
