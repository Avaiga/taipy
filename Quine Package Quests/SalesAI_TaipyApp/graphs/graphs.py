import random
import pandas as pd

data = pd.read_csv('DataSet\Diwali Sales Data.csv', encoding= 'latin1')



#Pie chart
def PieChart(states):
   States = data[data['State'] == states]
   Order = States.groupby('Occupation')['Orders'].sum().reset_index()
   pie_data= {"values": Order['Orders'].to_list(),"labels": Order['Occupation'].to_list()}
   return pie_data

# bar graph
def BarGraph():
   grouped_data = data.groupby('Occupation', as_index=False).agg({
       'Orders': 'sum'
   })

   layout = {
       "title": 'Total Orders per Occupation',
       "xaxis": dict(title='Occupation'),
       "yaxis": dict(title='Orders'),
       "barmode": 'group'
   }
   return grouped_data, layout
