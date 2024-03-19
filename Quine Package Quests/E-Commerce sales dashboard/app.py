from taipy.gui import Gui, navigate
import pandas as pd
import numpy as np
from collections import OrderedDict

root_md="<|menu|label=Dashboard|lov={[('Products', 'Products'), ('Orders','Orders'), ('Sales', 'Sales'), ('Reports','Reports')]}|on_action=on_menu|>"
products="""
<|Products|>

<|{data}|table|> 
<|{data2}|chart|type=pie|x[1]=0/values|x[2]=1/values|options={options1}|layout={layout}|>
<|{data1}|chart|type=pie|x[1]=0/values|x[2]=1/values|options={options2}|layout={layout}|>
"""

orders="""
<|Orders|>

<|{time_sales}|chart|type=bar|x=Time (nth Hour)|y=No. of Units|layout={layout_bar}|>
<|{data_device}|chart|type=pie|x[1]=0/values|x[2]=1/values|options={options3}|layout={layout1}|>
"""

sales="""
<|Sales|>


"""

reports="""
<|Reports|>


"""
###################################################################

df = pd.read_csv('E-commerce Dataset.csv')
data = pd.DataFrame()
d=[]
for i in df['Product_Category'].unique():
    g3 = np.where(df['Product_Category']==i)
    h3 = pd.DataFrame(data = df.iloc[g3[0],:])
    b3 = pd.DataFrame(data = h3['Product'].unique(), columns=[f"{i}"])
    c3 = pd.DataFrame(data=np.array(h3['Product'].value_counts()),columns=[f"Units Sold for {i}"])
    data = pd.concat([data,b3,c3],axis=1)
    data_pie_1 = {
    "Products": h3['Product'].unique(),
    "Units": np.array(h3['Product'].value_counts())
    }
    d.append(data_pie_1)
    
#######################################################

# List of countries, used as labels in the pie charts

data2 = [
    {
        #Auto & Accessories
        "values": d[0]['Units'],
        "labels": d[0]['Products']
    },
    {
        #Fashion
        "values": d[1]['Units'],
        "labels": d[1]['Products']
    },
]

data1=[
    {
        #Electronics
        "values": d[2]['Units'],
        "labels": d[2]['Products']
    },
    {
        #Home & Furniture
        "values": d[3]['Units'],
        "labels": d[3]['Products']
    },
]

options1 = [
    # First pie chart
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Auto & Accessories",
        "hole": 0.4,
        # Place the trace on the left side
        "domain": {"column": 0}
    },
    # Second pie chart
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Fashion",
        "hole": 0.2,
        # Place the trace on the right side
        "domain": {"column": 1}
    },]

options2=[
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Electronic",
        "hole": 0.3,
        # Place the trace on the right side
        "domain": {"column": 0}
    },
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Home & Furniture",
        "hole": 0.4,
        # Place the trace on the right side
        "domain": {"column": 1}
    }
]

layout = {
    # Show traces in a 1x2 grid
    "title":"Products per category distribution",
    "grid": {
        "rows": 1,
        "columns": 2
    },
    "showlegend": False
}

########### ORDERS ####################################

df['Hour'] = pd.to_datetime(df['Time']).dt.hour

key = df['Hour'].value_counts().keys()
values = df['Hour'].value_counts()
time = {}

for i in range(0,len(values)):
    d = {key[i] : values[i]}
    time.update(d)

time_sorted = OrderedDict(sorted(time.items()))

time_sales = pd.DataFrame(list(time_sorted.items()), columns=['Time (nth Hour)', 'No. of Units'])

layout_bar={
   "title": "Units sold per hour the day"
}

###### ORDER PIE CHART ################################

data_device = [
    {
    "values": df['Payment_method'].value_counts(),
    "labels": df['Payment_method'].unique()
    },
    {
    "values": df['Gender'].value_counts(),
    "labels": df['Gender'].unique()
    },
]

layout1 = {
    # Show traces in a 1x2 grid
    "title":"Summary of Orders",
    "grid": {
        "rows": 1,
        "columns": 2
    },
    "showlegend": False
}

options3 = [
    # First pie chart
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Payment method",
        "hole": 0.4,
        # Place the trace on the left side
        "domain": {"column": 0}
    },
    {
        # Show label value on hover
        "hoverinfo": "label",
        "title": "Gender",
        "hole": 0.4,
        # Place the trace on the left side
        "domain": {"column": 1}
    },
]

#######################################################
def on_menu(state, action, info):
    page = info["args"][0]
    navigate(state, to=page)


pages = {
    "/": root_md,
    "Products": products,
    "Orders": orders,
    "Sales": sales,
    "Reports": reports
}

if __name__ == "__main__":
    app = Gui(pages=pages,css_file="test.css")
    app.run(use_reloader=True)    