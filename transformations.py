import pandas as pd
pd.options.mode.chained_assignment = None

def dataframe_pivot(df : pd.DataFrame) -> tuple:
    # flattens the data into a timeseries
    return df.melt(id_vars=["recordDate"], value_vars=["living_room_temp", "bathroom_temp", "closet_temp", "humidity", "pressure"])

def breakdown(df: pd.DataFrame) -> tuple:
    # break the flattened dataframe based on variable type
    temperatures = df[["recordDate","variable","value"]].loc[df["variable"].isin(["living_room_temp", "bathroom_temp", "closet_temp"])]
    other = df[["recordDate","variable","value"]].loc[df["variable"].isin(["recordDate","pressure","humidity"])]
    return temperatures, other

def get_interval_means(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    # location var is items after melt, rooms, temp/humidity etc
    temp = dataframe_pivot(df)
    temp.dropna(inplace=True)
    temp["recordDate"] = pd.to_datetime(temp["recordDate"])
    temp.set_index("recordDate", inplace=True)
    return temp.groupby(['variable', pd.Grouper(freq=freq)]).mean()

def get_current_temperature(df: pd.DataFrame) -> float:
    return df['living_room_temp'][0]

def get_current_humidity(df: pd.DataFrame) -> float:
    return df['humidity'][0]

def get_current_temperature_as_string(temp: float, rounding: int) -> str:
    return str(round(temp, rounding)) + '°C'

def get_current_humidity_as_string(humidity: float, rounding: int) -> str:
    return str(round(humidity, rounding)) + '%'

def get_rolling_record_average(df: pd.DataFrame) -> pd.Series:
    # change to date type
    df.recordDate = pd.to_datetime(df.recordDate)
    # sort by date
    df_time = df.set_index('recordDate').sort_index(ascending=True)
    # return rolling window average
    return df_time.rolling(window='30d').mean().loc[df_time.index.max()]

def compare_temp_to_average(df) -> float:
    return round(get_current_temperature(df) - get_rolling_record_average(df)["living_room_temp"], 2)

def compare_humidity_to_average(df) -> float:
    return round(get_current_humidity(df) - get_rolling_record_average(df)["humidity"], 2)

def percentage_difference_as_string(current: float, average: float) -> str:
    figure = (((current - average) / average) * 100)
    descriptor = (" below " if figure <= 0 else " above ") + "30 day average"
    return str(round(figure, 1)) + '%' + descriptor

def average_at_day_intervals(df):
    df["recordDate"] = pd.to_datetime(df["recordDate"]).dt.date
    return df.groupby(df["recordDate"]).mean()
