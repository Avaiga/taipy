import re


def convert_to_dict(file_path, data_type):
    with open(file_path, "r") as file:
        content = file.read()

    # Extract sources and amounts using regular expression
    matches = re.findall(r"(\w+):(\d+)", content)

    # Create a dictionary with "Income_Source" and "Amount" keys
    data = {f"{data_type.capitalize()}_Source": [], "Amount": []}

    source_dict = {}

    for match in matches:
        source, amount = match
        source_dict.setdefault(source, 0)
        source_dict[source] += float(amount)

    # Adjust the order based on data_type
    data[f"{data_type.capitalize()}_Source"] = list(source_dict.keys())
    data["Amount"] = list(source_dict.values())

    return data


# Example usage for income.txt
income_file_path = "income.txt"
income_data = convert_to_dict(income_file_path, data_type="income")

# Save the result in another Python file
with open("income_pi_data.py", "w") as output_file:
    output_file.write(f"income_pi_data = {income_data}\n")

# Example usage for expenses.txt
expenses_file_path = "expenses.txt"
expenses_data = convert_to_dict(expenses_file_path, data_type="expenses")

# Save the result in another Python file
with open("expenses_pi_data.py", "w") as output_file:
    output_file.write(f"expenses_pi_data = {expenses_data}\n")
