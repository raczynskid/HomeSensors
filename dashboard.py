from dash import Dash, html, dash_table, dcc
import datetime
import plotly.express as px
import pandas as pd
import sqlite3

# initialize app
app = Dash(__name__)

def get_data():
    with sqlite3.connect('enviro.db') as conn:
        return pd.read_sql_query("SELECT * FROM weather;", conn)

    
def get_lastday(df: pd.DataFrame) -> pd.DataFrame:
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    df["last_day"] = pd.to_datetime(df["recordDate"]).dt.date >= yesterday
    return df


def serve_layout():
    
    df = get_data()
    ytd = get_lastday(df)
    
    return html.Div([
    html.Div(children='Weather station operation'),
    dcc.Graph(figure=px.line(ytd, x='recordDate', y='living_room_temp', title="Living Room temp in C")),
    dcc.Graph(figure=px.line(ytd, x='recordDate', y='humidity', title="Humidity %")),
    dcc.Graph(figure=px.line(ytd, x='recordDate', y='pressure', title="Pressure in hPa")),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])


app.layout = serve_layout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
