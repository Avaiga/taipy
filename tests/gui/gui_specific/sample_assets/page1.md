# Taipy Demo Page 1

x = <|{x}|>

<|x = {x}|>

y = <|{y}|>

<|y = {y}|>

<|x + y = {x+y}|>

Editing for x: <|{x}|number|>

Editing for y: <|{y}|number|>

2*x+3*y = <|{2*x+3*y}|>

Input for 2*x+3*y: <|{2*x+3*y}|number|>

<|Hello to {name.lower()}|>

<|{my_date}|>

<|{my_date}|date_selector|>

<|{my_date}|date_selector|with_time=True|>

<|{parameter.date}|>

<|{parameter.date}|date_selector|>

<|{parameter.date}|date_selector|with_time=True|>

<|{parameter.name}|>

<|{parameter.name}|input|>

<|button|label={name}|>

<|Hello {name}|button|on_action=do_something_fn|id={btn_id}|>

## These won't work (with_time)

<|{my_date}|date_selector|with_time|>

<|{csvdata}|table|page_size=10|page_size_options=10;30;1000|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|show_all=False|>