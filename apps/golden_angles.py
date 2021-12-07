import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dash_table as dt
from app import app

from _utilities import *

app_name = 'app6'
app_id_dict = init_app_ids(app_name=app_name)


layout = html.Div([
    dbc.Row([html.H2("Golden Angles",
                     style=({'color': 'blue'}),
                     ),
             ],
            class_name='title_tools',
            ),
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
                        dcc.Graph(id='plot',
                                  config={'displaylogo': False,
                                          })

                    ], label='Plot')
                ]),
            ])
    ],
    style={'margin': '25px'}

)


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


    table = dt.DataTable(columns=([{'id': 'angles', 'name': 'Angles (degrees)', 'type': 'numeric', 'editable':
        False}]),
                         data=data.to_dict('records'),
                         export_format='csv',
                         style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                       'color': 'white'},
                         style_cell={'textAlign': 'left'},
                         style_table={'maxWidth': '30%'},
                         )

    return fig, table
