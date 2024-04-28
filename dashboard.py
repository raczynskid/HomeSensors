from dash import Dash, html, dash_table, dcc
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
from transformations import *

# initialize app
app = Dash(__name__)

def get_data():
    with sqlite3.connect('enviro.db') as conn:
        return pd.read_sql_query("SELECT living_room_temp,bathroom_temp,closet_temp,staircase_temp,humidity,pressure,recordDate FROM weather ORDER BY recordDate DESC;", conn)

    
def get_lastday(df: pd.DataFrame) -> pd.DataFrame:
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    df["last_day"] = pd.to_datetime(df["recordDate"]).dt.date >= yesterday
    return df

def serve_layout():
    
    df = get_data()
    temperatures, other = breakdown(dataframe_pivot(df))
    weekly_means_temperature = get_interval_means(temperatures, "living_room_temp", "W")
    weekly_means_humidity = get_interval_means(other, "humidity", "W")
    weekly_means_pressure = get_interval_means(other, "pressure", "D")

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
                      dcc.Graph(figure=px.line(weekly_means_temperature, y='value', title="Temperatures in C")),
                      dcc.Graph(figure=fig)])
    
    return html.Div(className='app', children=[card_container, graph_container, dcc.Graph(figure=px.line(weekly_means_humidity, y='value')), dcc.Graph(figure=px.line(weekly_means_pressure, y='value'))])
    #dash_table.DataTable(data=df.to_dict('records'), page_size=10)


app.layout = serve_layout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)
