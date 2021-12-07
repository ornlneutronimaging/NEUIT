import dash_bootstrap_components as dbc

from callbacks.tof_plotter import *


# Time-of-flight plotter

app_name = 'tof_plotter'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout

layout = html.Div(
    [
        dbc.Row([html.H2("TOF plotter",
                         style=({'color': 'blue'}),
                         ),
                 ],
                class_name='title_tools',
                ),
        html.Hr(style={'borderTop': '3px solid blue'}),

        # Experiment input
        html.Div(
            [
                html.H3('Instrument Parameters:'),
                html.Div(
                    [
                        # html.Div(
                        #     [
                        #         html.H6('Temperature (K):'),
                        #         dcc.Input(id=app_id_dict['temperature_id'],
                        #                   type='number',
                        #                   value=temperature_default,
                        #                   min=0,
                        #                   inputMode='numeric',
                        #                   step=0.1,
                        #                   ),
                        #     ], className=col_width_3,
                        # ),

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
                            ], className=col_width_3,
                        ),

                        html.Div(
                            [
                                html.H6('Delay (\u03BCs):'),
                                dcc.Input(id=app_id_dict['delay_id'],
                                          type='number',
                                          value=delay_default,
                                          min=0,
                                          inputMode='numeric',
                                          step=0.01,
                                          ),
                            ], className=col_width_3,
                        ),
                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ], className='row', style={'verticalAlign': 'middle'},
        ),

        html.H3('Upload files:'),

        html.Div(
            [
                html.H6('Spectrum:'),
                dcc.Upload(id=app_id_dict['spectra_upload_id'],
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
                           multiple=False,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['spectra_upload_fb_id']),

                html.H6('Data:'),
                dcc.Upload(id=app_id_dict['data_upload_id'],
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
                html.Div(id=app_id_dict['data_upload_fb_id']),

                html.H6('Background (optional):'),
                dcc.Checklist(
                    id=app_id_dict['background_check_id'],
                    options=[
                        {'label': 'Ignore loaded background', 'value': 'ignore'},
                    ],
                    value=[],
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Upload(id=app_id_dict['background_upload_id'],
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
                           multiple=False,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['background_upload_fb_id']),

                html.Div(id=app_id_dict['hidden_upload_time_id'], style={'display': 'none'}, children=0),
            ]
        ),

        # Error message div
        html.Div(id=app_id_dict['error_id'], children=None),

        # Output div
        html.Div(
            [
                # Plot options
                html.H3('Plot:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('X options: '),
                                dcc.RadioItems(id='x_type',
                                               options=[
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                                   {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
                                                   {'label': 'Image index (#)', 'value': 'number'},
                                               ],
                                               value='number',
                                               # n_clicks_timestamp=0,
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Y options: '),
                                dcc.RadioItems(id='y_type',
                                               options=[
                                                   {'label': 'Transmission', 'value': 'transmission'},
                                                   {'label': 'Attenuation', 'value': 'attenuation'},
                                               ],
                                               value='transmission',
                                               # n_clicks_timestamp=0,
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Scale options: '),
                                dcc.RadioItems(id='plot_scale',
                                               options=[
                                                   {'label': 'Linear', 'value': 'linear'},
                                                   {'label': 'Log x', 'value': 'logx'},
                                                   {'label': 'Log y', 'value': 'logy'},
                                                   {'label': 'Loglog', 'value': 'loglog'},
                                               ],
                                               value='linear',
                                               # n_clicks_timestamp=0,
                                               )
                            ], className=col_width_3
                        ),
                    ], className='row'
                ),

                # Plot
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),

                # # Transmission at CG-1D and stack info
                # html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
