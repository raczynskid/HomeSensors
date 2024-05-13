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

def serve_humidity_and_pressure_graph(weekly_means: pd.DataFrame):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    weekly_means_humidity = weekly_means.loc[weekly_means["variable"] == "humidity"]
    weekly_means_pressure = weekly_means.loc[weekly_means["variable"] == "pressure"]
    fig.add_trace(
        go.Scatter(x=weekly_means_humidity["recordDate"], y=weekly_means_humidity['value'], name="humidity in %"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=weekly_means_pressure["recordDate"], y=weekly_means_pressure['value'], name="pressure in hPa"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Pressure and Humidity", template='simple_white'
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date/Time")

    # Set y-axes titles
    fig.update_yaxes(title_text="hPa", secondary_y=True)
    fig.update_yaxes(title_text="humidity %", secondary_y=False)

    fig.update_coloraxes
    return fig

def serve_temperature_graph(weekly_means: pd.DataFrame):
    temperature_fig=px.line(data_frame=weekly_means.loc[weekly_means["variable"] == "living_room_temp"], x='recordDate', y='value', title="Temperatures in C", template='simple_white')
    temperature_fig.update_traces(textposition='top center', line_color='#ff9aa2')
    return temperature_fig


def serve_layout():
    
    df = get_data()
    temperatures, other = breakdown(dataframe_pivot(df))
    other = other.loc[other['recordDate'] >= (datetime.date.today()- datetime.timedelta(weeks=4)).strftime("%Y-%m-01") ]
    weekly_means = get_interval_means(df, 'w').reset_index()

    current_temp = get_current_temperature(df)
    current_humidity = get_current_humidity(df)

    timer = html.Div(className='timer', children=datetime.datetime.now().strftime("%x"))
    card_temperature = html.Div(className='temperatureCard', children=get_current_temperature_as_string(current_temp, 1))
    card_temperature_variance = html.Div(className='temperatureVarianceCard', children=percentage_difference_as_string(current_temp, get_rolling_record_average(df)["living_room_temp"]))
    card_humidity = html.Div(className='humidityCard', children=get_current_humidity_as_string(current_humidity, 1))
    card_humidity_variance = html.Div(className='humidityVarianceCard', children=percentage_difference_as_string(current_humidity, get_rolling_record_average(df)["humidity"]))

    graph_temperature = dcc.Graph(figure=serve_temperature_graph(weekly_means))
    graph_humidity_and_pressure = dcc.Graph(figure=serve_humidity_and_pressure_graph(weekly_means))

    card_container = html.Div(className='cardContainer', 
                     children=[
                     timer,
                     card_temperature,
                     card_temperature_variance,
                     card_humidity,
                     card_humidity_variance
                     ])
    
    graph_container = html.Div(className='graphContainer', children=[
                      graph_temperature,
                      graph_humidity_and_pressure
                      ])
    
    return html.Div(className='app', children=[card_container, graph_container])


app.layout = serve_layout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)
