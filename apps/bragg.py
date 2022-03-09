import dash_bootstrap_components as dbc

from callbacks.bragg import *
from callbacks.utilities.initialization import (init_app_ids, temperature_default, distance_default, init_app_about,
                                                init_display_plot_data_check)
from callbacks.utilities.plot import bragg_plot_option_div

# Bragg-edge tool

app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        dbc.Row([html.H2("Bragg Edge Simulator",
                         style=({'color': 'blue'}),
                         ),
                 ],
                class_name='title_tools',
                ),
        html.Hr(style={'borderTop': '3px solid blue'}),
        init_app_about(current_app=app_name, app_id_dict=app_id_dict),
        # Experiment input
        html.Div(
            [
                html.H3('Global parameters:'),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Temperature (K):'),
                                    dcc.Input(id=app_id_dict['temperature_id'],
                                              type='number',
                                              value=temperature_default,
                                              min=0,
                                              inputMode='numeric',
                                              step=0.1,
                                              ),
                                ]
                            ), width=2
                        ),

                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Source-to-detector (m):'),
                                    dcc.Input(id=app_id_dict['distance_id'],
                                              type='number',
                                              value=distance_default,
                                              min=0,
                                              inputMode='numeric',
                                              step=0.01,
                                              ),
                                ]
                            ), width=2
                        ),
                    ]
                ),
            ]
        ),

        html.Div(
            [
                html.H6('Wavelength band:'),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Min. (\u212B) :'),
                                    dcc.Input(id=app_id_dict['band_min_id'], type='number',
                                              inputMode='numeric',
                                              placeholder='Min.',
                                              step=0.001,
                                              value=0.05,
                                              ),
                                ]
                            ), width=2
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Max. (\u212B):'),
                                    dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                              inputMode='numeric',
                                              placeholder='Max.',
                                              step=0.001,
                                              value=5.5,
                                              ),
                                ]
                            ), width=2
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Step (\u212B):'),
                                    dcc.Input(id=app_id_dict['band_step_id'], type='number',
                                              inputMode='numeric',
                                              placeholder='Max.',
                                              step=0.001,
                                              value=0.005,
                                              ),
                                ]
                            ), width=2
                        ),
                    ],
                ),
            ],
        ),
        html.Hr(),
        html.H3('Upload cif file/files:'),

        html.Div(
            [
                dcc.Upload(id=app_id_dict['cif_upload_id'],
                           children=html.Div([
                               'Drag and Drop or ',
                               html.A('Select Files'),
                           ]),
                           style={
                               'width': '100%',
                               'height': '60px',
                               'lineHeight': '60px',
                               'borderWidth': '1px',
                               'borderStyle': 'dashed',
                               'borderRadius': '5px',
                               'textAlign': 'center',
                               'margin': '10px'
                           },
                           # Allow multiple files to be uploaded
                           multiple=True,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['cif_upload_fb_id']),
                html.Button('Submit', id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),
                html.Div(id=app_id_dict['hidden_upload_time_id'], style={'display': 'none'}, children=0),
            ]
        ),

        # Error message div1
        html.Div(id=app_id_dict['error_id'], children=None),

        # Error message div2
        html.Div(id=app_id_dict['error_id2'], children=True),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

        # Hidden div to store df_export json
        html.Div(id=app_id_dict['hidden_df_export_json_id'], style={'display': 'none'}),

        # Output div
        html.Div(
            [
                # Plot
                html.Div(
                    [
                        bragg_plot_option_div,
                        dcc.Loading(
                            id="loading-2",
                            children=[
                                html.Div(id=app_id_dict['plot_div_id'], className='container'),
                                init_display_plot_data_check(app_id_dict),
                                # Data table for the plotted data
                                html.Div(id=app_id_dict['df_export_tb_div']),
                            ],
                            type="circle",
                        )
                    ]
                ),

                # Transmission at CG-1D and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
