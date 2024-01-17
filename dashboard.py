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
        return pd.read_sql_query("SELECT living_room_temp,bathroom_temp,closet_temp,staircase_temp,humidity,pressure,recordDate FROM weather ORDER BY recordDate DESC LIMIT 576 ;", conn)

    
def get_lastday(df: pd.DataFrame) -> pd.DataFrame:
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    df["last_day"] = pd.to_datetime(df["recordDate"]).dt.date >= yesterday
    return df


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

    return html.Div([
    html.Div(children='Weather station operation'),
    dcc.Graph(figure=px.line(temperatures, x='recordDate', y='value', title="Temperatures in C", color="variable")),
    dcc.Graph(figure=fig),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])


app.layout = serve_layout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
