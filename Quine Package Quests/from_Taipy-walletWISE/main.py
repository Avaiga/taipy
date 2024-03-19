from taipy import Gui
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

import os
import google.generativeai as genai
import subprocess
import json

from income_pi_data import income_pi_data
from expenses_pi_data import expenses_pi_data

# Configuration for GenAI
genai.configure(api_key=os.getenv("API_KEY"))

title = "walletWISE 🤑"

hover_text = """🚀 Track, Thrive, Triumph. #MoneyMastery"""

income = ""
expenses = ""

income_sector = ""
expenses_sector = ""
message = ""

path = "wallet_calc.gif"

source_of_income = ["salary", "dividend", "business_revenue", "tax_rebate", "others"]
source_of_expenses = [
    "Fooding",
    "Clothing",
    "Education",
    "Health",
    "Misc",
]


# loading Gemini Pro model
model = genai.GenerativeModel("gemini-pro")


# Getting Sum of Data under different heading
def get_sum(data_string):
    try:
        entries = data_string.split(",")
        total_sum = sum(
            int(entry.split(":")[1]) for entry in entries if len(entry.split(":")) == 2
        )
        return total_sum
    except (ValueError, IndexError):
        print("Error: Unable to calculate sum.")
        return None


# Net amount
def net_amount(income_sum, expense_sum):
    if income_sum < expense_sum:
        result = "loss"
        net_amount = expense_sum - income_sum
    else:
        result = "profit"
        net_amount = income_sum - expense_sum

    return result, net_amount


# Generating content using the model
def generate(state):
    state.message = "Please wait while we analyze your INCOME AND EXPENSES..."

    # Read data from income.txt
    with open("income.txt", "r") as income_file:
        income_data = income_file.read().strip()

    # Read data from expenses.txt
    with open("expenses.txt", "r") as expenses_file:
        expenses_data = expenses_file.read().strip()

    print(f"Income_data: {income_data}\nExpenses_data: {expenses_data}")

    print(
        f"Sum of Income=>{get_sum(income_data)}\n Sum of Expenses=>{get_sum(expenses_data)}"
    )

    status = net_amount(get_sum(income_data), get_sum(expenses_data))

    # Combine the data into a prompt for generating response
    prompt = f"""Create a financial Saving plan while analyzing 
    Income_Data:\n{income_data}\n
    Expenses:\n{expenses_data}\n
    The person is in {status[0]} and the total {status[0]} amount is: {status[1]}\n
    While giving tips please use the data provided to you as reference and give tips based on that!
    Remember the goal is to maximize saving, maximize investment while minimizing useless expenses
    \nPlease provide only 7 tips for the person by analyzing the Income, Expense and total {status[0]}!\n
    """

    # Generate content using the model
    result = model.generate_content([prompt])

    # Access the parts of the response
    response_text = result.candidates[0].content.parts[0].text

    # Run pi_data.py using subprocess
    subprocess.run(["python3", "pi_data.py"])
    # income_data is a string (business_revenue:750,dividend:300,others:500)
    # parse income_data into a dictionary
    income_data_dict = {}
    for entry in income_data.split(","):
        if ":" in entry:
            key, value = entry.split(":")
            if key in income_data_dict:
                income_data_dict[key] += int(value)
            else:
                income_data_dict[key] = int(value)

    income_data_df = pd.DataFrame(
        {
            "Income_Source": list(income_data_dict.keys()),
            "Amount": list(income_data_dict.values()),
        }
    )
    state.income_pi_data = pd.DataFrame(income_data_df)

    expenses_data_dict = {}
    for entry in expenses_data.split(","):
        if ":" in entry:
            key, value = entry.split(":")
            if key in expenses_data_dict:
                expenses_data_dict[key] += int(value)
            else:
                expenses_data_dict[key] = int(value)

    expenses_data_df = pd.DataFrame(
        {
            "Expenses_Source": list(expenses_data_dict.keys()),
            "Amount": list(expenses_data_dict.values()),
        }
    )
    state.expenses_pi_data = pd.DataFrame(expenses_data_df)

    res = response_text
    user_friendly_message = parse_and_format_tips(res)
    print(response_text)
    state.message = f"""
    Income:\n{income_data}\n
    Expenses:\n{expenses_data}\n
    The person is in {status[0]} and the total {status[0]} amount is: {status[1]}\n\n
    You should try to follow this: \n\n\n{user_friendly_message}
    """


def parse_and_format_tips(tips_text):
    # Remove ** signs and split the text into lines
    lines = tips_text.split("\n")

    # Filter out empty lines and lines starting with a number
    tips_lines = [
        line.lstrip("1234567890. ").replace("**", "").strip("* ")
        for line in lines
        if line.strip()
    ]

    # Create a user-friendly message with existing numbering and line breaks
    user_friendly_message = "\n\n".join(
        f"{index}. {tip}" if index > 0 else tip for index, tip in enumerate(tips_lines)
    )

    return user_friendly_message


def generate_income(state):
    print(state.income)
    if state.income != "" and state.income_sector != "":
        with open("income.txt", "a") as f:
            f.write(f"{state.income_sector}:{state.income},")


def generate_expenses(state):
    print(state.expenses)
    if state.expenses != "" and state.expenses_sector != "":
        with open("expenses.txt", "a") as f:
            f.write(f"{state.expenses_sector}:{state.expenses},")


def clear_income(state):
    state.income_sector = ""
    state.income = ""


def clear_expenses(state):
    state.expenses_sector = ""
    state.expenses = ""


page = """

<style>

.greenButton:hover{
    text-decoration: none;
    background-color: rgba(255, 96, 255, 0.08);
    border: 1px solid rgb(150, 255, 0);
}

.greenButton{
    border: 1px solid rgba(150, 255, 0, 0.5);
    color:rgb(150, 255, 0);
    margin-bottom:2rem;
}

.pichart{
    display:flex;
}

.chartbox{
    display:flex;
    border: 1px solid white;
}

.button_row{
    display: flex;
}

.fullwidth{
width:100% !important;
}

.form{
 display:flex;
 flex-direction:column;
 justify-content:space-evenly;
 padding:2rem;
 margin-top:2rem;
}

.middleSection{
 display:flex;
 flex-wrap: wrap;
 justify-content:center;
 gap:2rem;
 padding:"2rem"
 
}

.fullCenter{
 display:flex;
 justify-content:center;
 align-items:center;
  flex-direction:column;
}
</style>

<|text-right|toggle|theme|>\n<center>\n<|navbar|>\n</center>
<|text-center |
<|{title}|hover_text="{hover_text}"|text|>
|>
<|middleSection| 
<|fullCenter|  
 <|{path}|image|>
 |>
<||

<|form| 

<|1 1|layout|
### Income **Amount & Sector**{: .color-primary}!    
TOTAL INCOME: <|{income}|input|>
<|{income_sector}|selector|lov={source_of_income}|dropdown|label=sources of income|> 
|>
<|class_name = button_row|
<|Add to Income!|button|on_action=generate_income|>
<|Clear|button|class_name=blueButton|on_action=clear_income|>
|>
<|1 1|layout|
### Expenses **Amount & Sector**{: .color-primary}!    
EXPENDITURE: <|{expenses}|input|>
<|{expenses_sector}|selector|lov={source_of_expenses}|dropdown|label=sources of expense|> 
|>
<|class_name=button_row|
<|Add to Expense|button|on_action=generate_expenses|>
<|Clear|button|class_name=blueButton|on_action=clear_expenses|>
|>
|>

<|text-center|
<|Get Insights|button|class_name=greenButton|on_action=generate|>
|>
|>
|>
<|part|class_name=card|
<|{message}|input|multiline|not active|label= Your Insights will be appear here!|class_name=fullwidth|>
|>

<|1 1|layout|
<part|class_name=card mt1|
## Income **Chart**{:.color-primary}
<|{income_pi_data}|chart|rebuild|type=pie|values=Amount|labels=Income_Source|>
|>
<part|class_name=card mt1|
## Expense **Chart**{:.color-primary}
<|{expenses_pi_data}|chart|rebuild|type=pie|values=Amount|labels=Expenses_Source|>
|>
"""

if __name__ == "__main__":
    app = Gui(page)
    app.run(
        title="walletWISE",
        watermark="""Balance your revenue and expenses! Copyright @Ujj1225""",
        favicon="wallet_wise.gif",
        use_reloader=True,
    )
