from polygon import RESTClient as rc
import requests
import json

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url='https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=A259DEANU8GNBTMM/v1'
r=requests.get(url)
data=r.json()

with open("stockInfo.json","w") as f:
    json.dump(data,f)