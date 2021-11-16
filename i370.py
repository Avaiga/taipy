from taipy.gui import Gui, Markdown
import pandas as pd
from datetime import datetime, timedelta

x1 = 1
x2 = 2
today = datetime.now()
dates_df = pd.Series([today, today + timedelta(days=1), today + timedelta(days=2)], name="Date")
col1_df = pd.Series([0., 1., 2.], name="Input")
col2_df = pd.Series([0., 1., 4.], name="Square")
table_data = pd.concat([dates_df, col1_df, col2_df], axis=1)

gui = Gui(pages={"page1": Markdown('''# Taipy Issue 370
Here is x1: <|{x1}|>. <|{x1}|slider|>

Here are x1 and x2: <|{x1} {x2}|>

Table: <|{table_data}|table|>''')})

# Here is x1: <|{x1}|>. <|{x1}| slider | >
# Here are x1 and x2: < |{x1} {x2} | >


gui.run()
