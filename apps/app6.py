import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from _app import app
from apps.utilities.file import make_ascii_file
from _utilities import *

app_name = 'app6'
app_id_dict = init_app_ids(app_name=app_name)


layout = html.Div([
    init_app_links(current_app=app_name, app_dict_all=app_dict),
    init_app_about(current_app=app_name, app_id_dict=app_id_dict),
    html.Div(
            [
                html.Br(),
                dbc.Row([
                    dbc.Col(lg=1),
                    dbc.Label("Max angle value: "),
                    dcc.RadioItems(
                            id='max_angle',
                            options=[
                                {'label': u"180\u00b0", 'value': 180},
                                {'label': u"360\u00b0", 'value': 360}
                            ],
                            value=180,
                            labelStyle={'display': 'inline-block'},
                            style={"padding"    : "0px",
                                   "margin-left": "10px"
                                   },
                    ),
                ]),
                dbc.Row([
                    dbc.Col(lg=1),
                    dbc.Label("Number of angles:"),
                    dcc.Input(id="number_of_angles",
                              type="number",
                              min=1,
                              value=50),
                ]),
                html.Br(),
                dbc.Tabs([
                    dbc.Tab([
                        html.Div(id='table')
                    ], label='Data'),
                    dbc.Tab([
                        dcc.Graph(id='plot')

                    ], label='Plot')
                ]),
                html.Br(),
                dbc.Button("Download ASCII File",
                           id="download",
                           # href="",
                           # download="",
                           style={"width": "100%"},
                           external_link=True,
                           color="primary")
            ])
])


def calculate_golden_ratio(angle_index, max_angle=180):
    phi = 0.5 * (1 + np.sqrt(5))
    return np.fmod(int(angle_index) * phi * 180, int(max_angle))


def retrieve_list_of_golden_angles(total_number_of_angles, max_angle=180):
    list_angles = [calculate_golden_ratio(angle_index, max_angle=max_angle) for angle_index in np.arange(
            total_number_of_angles)]
    return list_angles


@app.callback(Output('plot', 'figure'),
              Output('table', 'children'),
              Input('max_angle', 'value'),
              Input('number_of_angles', 'value'))
def update_golden_angles(max_angle_value, total_number_of_angles):
    fig = go.Figure()

    list_angles = retrieve_list_of_golden_angles(total_number_of_angles, max_angle=max_angle_value)
    data = pd.DataFrame(list_angles, columns=['angles'])

    fig.add_trace(go.Scatterpolar(theta=data['angles'],
                                  mode='markers+lines'))
    fig.layout.xaxis.title = "Iteration number"
    fig.layout.paper_bgcolor = '#E5ECF6'

    table = dbc.Table.from_dataframe(data)

    return fig, table


@app.callback(Output('messages', 'children'),
              Input('download', 'value'))
def download_file(value):
    return "button clicked!"
