# Data

Choose the CSV file: <|{input_csv_file}|file_selector|active={scenario}|label=Upload CSV|on_action=drop_csv|extensions=.csv|>

<|{inputs}|table|rebuild|>

Replacement value: <|{replacement_type}|input|active={scenario}|>

<|Clean data|button|active={input_csv_file}|on_action=on_clean_data|>

<|{results}|table|rebuild|>
