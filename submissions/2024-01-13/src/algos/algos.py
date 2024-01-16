import pandas as pd
from sklearn.linear_model import LinearRegression
import datetime as dt
import numpy as np
from pmdarima import auto_arima



def add_features(data):
    dates = pd.to_datetime(data["Date"])
    data["Months"] = dates.dt.month
    data["Days"] = dates.dt.isocalendar().day
    data["Week"] = dates.dt.isocalendar().week
    data["Day of week"] = dates.dt.dayofweek
    return data

def create_train_data(final_data, date:dt.datetime):
    date = date.date() if type(date) == dt.datetime else date
    bool_index = pd.to_datetime(final_data['Date']).dt.date <= date
    train_data = final_data[bool_index]
    return train_data

def preprocess(initial_data, country, date):
    data = initial_data.groupby(["Country/Region",'Date'])\
                       .sum()\
                       .dropna()\
                       .reset_index()

    final_data = data.loc[data['Country/Region']==country].reset_index(drop=True)
    final_data = final_data[['Date','Deaths']]
    final_data = add_features(final_data)
    
    train_data = create_train_data(final_data, date)
    return final_data, train_data


def train_arima(train_data):
    model = auto_arima(train_data['Deaths'],
                       start_p=1, start_q=1,
                       max_p=5, max_q=5,
                       start_P=0, seasonal=False,
                       d=1, D=1, trace=True,
                       error_action='ignore',  
                       suppress_warnings=True)
    model.fit(train_data['Deaths'])
    return model


def forecast(model):
    predictions = model.predict(n_periods=60)
    return np.array(predictions)


def concat(final_data, predictions_arima, predictions_linear_regression, date):
    def  _convert_predictions(final_data, predictions, date, label='Predictions'):
        dates = pd.to_datetime([date + dt.timedelta(days=i)
                                for i in range(len(predictions))])
        final_data['Date'] = pd.to_datetime(final_data['Date'])
        final_data = final_data[['Date','Deaths']]
        predictions = pd.concat([pd.Series(dates, name="Date"),
                                 pd.Series(predictions, name=label)], axis=1)
        return final_data.merge(predictions, on="Date", how="outer")


    result_arima = _convert_predictions(final_data, predictions_arima, date, label='ARIMA')
    result_linear_regression = _convert_predictions(final_data, predictions_linear_regression, date, label='Linear Regression')

    return result_arima.merge(result_linear_regression, on=["Date", 'Deaths'], how="outer").sort_values(by='Date')


def train_linear_regression(train_data):    
    y = train_data['Deaths']
    X = train_data.drop(['Deaths','Date'], axis=1)
    
    model = LinearRegression()
    model.fit(X,y)
    return model

def forecast_linear_regression(model, date):
    dates = pd.to_datetime([date + dt.timedelta(days=i)
                            for i in range(60)])
    X = add_features(pd.DataFrame({"Date":dates}))
    X.drop('Date', axis=1, inplace=True)
    predictions = model.predict(X)
    return predictions