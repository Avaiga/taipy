from taipy import Gui
import requests
import json

project_name="Stock Simulator By Varad Acharya"
image_path="./logo.png"

data=""
with open("stockInfo.json","r") as f:
    data=json.load(f)

company_name="IBM"
# print(company_name)

dates=[]
open_price=[]
close_price=[]
high_price=[]
low_price=[]
volume=[]

for i,j in data["Time Series (5min)"].items():
    dates.append(i)
    open_price.append(float(j['1. open']))
    high_price.append(float(j['2. high']))
    low_price.append(float(j['3. low']))
    close_price.append(float(j['4. close']))
    volume.append(int(j['5. volume']))

dataFrame={
    "DATES":dates,
    "OPEN":open_price,
    "HIGH":high_price,
    "LOW":low_price,
    "CLOSE":close_price,
    "VOLUME":volume
}

page="""
<|text-center|
<|{image_path}|image|>
# <|{project_name}|text|format=%.2f|hover_text="Welcome to our Varad Simulator"|>
>
Enter name of company for which you want to see stocks : <|{company_name}|input|>

<|SUBMIT|button|class_name=secondary|>

Stock Price with respect to Time : 

<|{dataFrame}|chart|x=DATES|y[1]=OPEN|y[2]=LOW|y[3]=HIGH|y[4]=CLOSE|mode[2]=dash|color[3]=red|color[4]=blue|>

Stock Volume Traded with respect to time : 

<|{dataFrame}|chart|x=DATES|y[1]=VOLUME|color[1]=green|>

"""

Gui(page).run(use_reloader=True)