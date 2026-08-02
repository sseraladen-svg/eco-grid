import pandas as pd
from prophet import Prophet


def train_prophet():

    df = pd.read_csv('data/weather_data.csv')

    # Solar radiation forecast
    solar = df[['date','solar_radiation']]
    solar.columns = ['ds','y']

    model = Prophet()
    model.fit(solar)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    result = forecast[['ds','yhat']]
    result.to_csv('data/solar_forecast.csv', index=False)

    # Wind speed forecast
    wind = df[['date','wind_speed']]
    wind.columns = ['ds','y']

    model_wind = Prophet()
    model_wind.fit(wind)

    forecast_wind = model_wind.predict(future)
    result_wind = forecast_wind[['ds','yhat']]
    result_wind.to_csv('data/wind_forecast.csv', index=False)
