from dash import Dash, html, dash_table, dcc
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import transformations as t

# initialize app
app = Dash(__name__)

def get_data():
    with sqlite3.connect('enviro.db') as conn:
        return pd.read_sql_query("SELECT living_room_temp,bathroom_temp,closet_temp,staircase_temp,humidity,pressure,recordDate FROM weather ORDER BY recordDate DESC;", conn)

    
def get_lastday(df: pd.DataFrame) -> pd.DataFrame:
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    df["last_day"] = pd.to_datetime(df["recordDate"]).dt.date >= yesterday
    return df

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

def serve_layout():
    
    df = get_data()
    temperatures, other = t.breakdown(t.dataframe_pivot(df))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=other["recordDate"], y=other["value"].loc[other["variable"] == "humidity"], name="humidity in %"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=other["recordDate"], y=other["value"].loc[other["variable"] == "pressure"], name="pressure in hPa"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Pressure and Humidity"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date/Time")

    # Set y-axes titles
    fig.update_yaxes(title_text="hPa", secondary_y=True)
    fig.update_yaxes(title_text="humidity %", secondary_y=False)

    fig.update_coloraxes

    current_temp = get_current_temperature(df)
    current_humidity = get_current_humidity(df)

    card_container = html.Div(className='cardContainer', children=[
                     html.Div(className='timer', 
                         children=datetime.datetime.now().strftime("%c")),
                     html.Div(className='temperatureCard',
                         children=get_current_temperature_as_string(current_temp, 1)),
                    html.Div(className='temperatureVarianceCard',
                         children=percentage_difference_as_string(current_temp, get_rolling_record_average(df)["living_room_temp"])),
                     html.Div(className='humidityCard',
                         children=get_current_humidity_as_string(current_humidity, 1)),
                     html.Div(className='humidityVarianceCard',
                         children=percentage_difference_as_string(current_humidity, get_rolling_record_average(df)["humidity"]))])
    
    graph_container = html.Div(className='graphContainer', children=[
                      dcc.Graph(figure=px.line(temperatures, x='recordDate', y='value', title="Temperatures in C", color="variable")),
                      dcc.Graph(figure=fig)])
    
    return html.Div(className='app', children=[card_container, graph_container])
    #dash_table.DataTable(data=df.to_dict('records'), page_size=10)


app.layout = serve_layout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)
