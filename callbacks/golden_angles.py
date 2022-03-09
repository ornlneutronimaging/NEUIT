from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from app import app
import pandas as pd
from dash import dash_table as dt
import numpy as np

from callbacks.utilities.initialization import init_app_ids


app_name = 'golden_angles'
app_id_dict = init_app_ids(app_name=app_name)


def calculate_golden_ratio(angle_index, max_angle=180):
    phi = 0.5 * (1 + np.sqrt(5))
    return np.fmod(int(angle_index) * phi * 180, int(max_angle))


def retrieve_list_of_golden_angles(total_number_of_angles, max_angle=180):
    list_angles = [calculate_golden_ratio(angle_index, max_angle=max_angle) for angle_index in np.arange(
            total_number_of_angles)]
    return list_angles

@app.callback(
    Output(app_id_dict['app_info_id'], 'style'),
    [
        Input(app_id_dict['more_about_app_id'], 'value'),
    ],
    [
        State(app_id_dict['app_info_id'], 'style'),
    ])
def show_hide_band_input(more_info, style):
    if more_info != ['more']:
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style


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

    table = dt.DataTable(columns=([{'id': 'angles',
                                    'name': 'Angles (degrees)',
                                    'type': 'numeric',
                                    'editable': False}]),
                         data=data.to_dict('records'),
                         export_format='csv',
                         style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                       'color': 'white'},
                         style_cell={'textAlign': 'left'},
                         style_table={'maxWidth': '30%'},
                         )

    return fig, table
