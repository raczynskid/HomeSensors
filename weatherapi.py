import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

class OpenMeteoApi:
    def __init__(self) -> None:
        self.get_openweather_response()

    def setup_api_client(self) -> openmeteo_requests.Client:
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_openweather_response(self):
        self.setup_api_client()
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 47.1149,
            "longitude": 8.3901,
            "current": ["temperature_2m", "relative_humidity_2m", "rain", "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "daylight_duration", "uv_index_max"],
            "timezone": "auto",
            "past_days": 5
        }
        self.response = self.openmeteo.weather_api(url, params=params)[0]
        self.current = self.response.Current()
        self.daily = self.response.Daily()
    
    def daily_forecast(self) -> pd.DataFrame:
        daily_temperature_2m_max = self.daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = self.daily.Variables(1).ValuesAsNumpy()
        daily_daylight_duration = self.daily.Variables(2).ValuesAsNumpy()
        daily_uv_index_max = self.daily.Variables(3).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(self.daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(self.daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = self.daily.Interval()),
            inclusive = "left"
        )}
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["uv_index_max"] = daily_uv_index_max

        return pd.DataFrame(data = daily_data)

    def refresh(self) -> None:
        self.get_openweather_response()

    @property
    def temperature(self) -> float:
        return self.current.Variables(0).Value()

    @property
    def humidity(self) -> float:
        return self.current.Variables(1).Value()
    
    @property
    def rain(self) -> float:
        return self.current.Variables(2).Value()
    
    @property
    def pressure(self) -> float:
        return self.current.Variables(3).Value()

    @property
    def pressure(self) -> float:
        return self.current.Variables(4).Value()

    @property
    def pressure(self) -> float:
        return self.current.Variables(5).Value()
    