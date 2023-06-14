# Page 2

Choose the CSV file of your choice to display it.
<|{path}|file_selector|label=Upload CSV|on_action=drop_csv|extensions=.csv|>

<|part|render={path}|
<|Data|expandable|expanded=False|
<|{data}|table|rebuild|>
|>
|>
