import dash_bootstrap_components as dbc

from callbacks.bragg import *
from callbacks.utilities.initialization import init_app_ids

# Bragg-edge tool

app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        # Experiment input
        html.Div(
            [
                dbc.Row([html.H2("Bragg Edge Simulator",
                                 style=({'color': 'blue'}),
                                 ),
                         ],
                        class_name='title_tools',
                        ),
                html.Hr(style={'borderTop': '3px solid blue'}),

                html.H3('Global parameters:'),
                html.Div(
                    [

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
                            ], className=col_width_3,
                        ),

                        # html.Div(
                        #     [
                        #         html.H6('Source-to-detector (m):'),
                        #         dcc.Input(id=app_id_dict['distance_id'],
                        #                   type='number',
                        #                   value=distance_default,
                        #                   min=0,
                        #                   inputMode='numeric',
                        #                   step=0.01,
                        #                   ),
                        #     ], className=col_width_3,
                        # ),

                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ], className='row', style={'verticalAlign': 'middle'},
        ),

        html.Div(
            [
                html.H6('Wavelength band:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('Min. (\u212B) :'),
                                dcc.Input(id=app_id_dict['band_min_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Min.',
                                          step=0.001,
                                          value=0.05,
                                          ),
                            ], className=col_width_3,
                        ),
                        html.Div(
                            [
                                html.P('Max. (\u212B):'),
                                dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.001,
                                          value=5.5,
                                          ),
                            ], className=col_width_3,
                        ),
                        html.Div(
                            [
                                html.P('Step (\u212B):'),
                                dcc.Input(id=app_id_dict['band_step_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.001,
                                          value=0.005,
                                          ),
                            ], className=col_width_3,
                        ),
                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ],
            className='row',
            style={'verticalAlign': 'middle'},
        ),

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
                # Plot options
                html.H3('Plot:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('X options: '),
                                dcc.RadioItems(id='x_type',
                                               options=[
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                               ],
                                               value='lambda',
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Y options: '),
                                dcc.RadioItems(id='y_type',
                                               options=[
                                                   # {'label': 'Transmission', 'value': 'transmission'},
                                                   # {'label': 'Attenuation', 'value': 'attenuation'},
                                                   # {'label': 'Attenuation coefficient', 'value': 'mu_per_cm'},
                                                   # {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                                   {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                               ],
                                               value='sigma_raw',
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
                        html.Div(
                            [
                                html.P('Interactions: '),
                                dcc.Checklist(id='xs_type',
                                              options=[
                                                  {'label': 'Total', 'value': 'total'},
                                                  {'label': 'Absorption', 'value': 'abs'},
                                                  {'label': 'Coherent elastic scattering', 'value': 'coh_el'},
                                                  {'label': 'Coherent inelastic scattering', 'value': 'coh_inel'},
                                                  {'label': 'Incoherent elastic scattering', 'value': 'inc_el'},
                                                  {'label': 'Incoherent inelastic scattering', 'value': 'inc_inel'},
                                              ],
                                              value=['total'],
                                              # n_clicks_timestamp=0,
                                              )
                            ], className=col_width_3
                        ),
                    ], className='row'
                ),

                # Plot
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),

                # Export plot data button
                html.Div(
                    [
                        dcc.Checklist(
                            id=app_id_dict['display_plot_data_id'],
                            options=[
                                {'label': 'Display plotted data', 'value': 'display'},
                            ],
                            value=[],
                            labelStyle={'display': 'inline-block'}
                        ),
                    ], className='row'
                ),

                # Data table for the plotted data
                html.Div(id=app_id_dict['df_export_tb_div']),

                # Transmission at CG-1D and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
