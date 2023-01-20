import dash_bootstrap_components as dbc

from callbacks.bragg import *
from callbacks.utilities.constants import *
from callbacks.utilities.initialization import (init_app_ids, temperature_default, distance_default, delay_default,
                                                init_app_about, init_display_plot_data_check, sample_tb_even_10_col)
from callbacks.utilities.plot import bragg_plot_option_div
from callbacks.utilities.all_apps import bragg_sample_header_df

# Bragg-edge tool

app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)

bragg_sample_df_default = pd.DataFrame({
    chem_name: ['Ni'],
    index_number_h: [0.0],
    index_number_k: [0.0],
    index_number_l: [0.0],
    axial_length_a: [3.5238],
    axial_length_b: [3.5238],
    axial_length_c: [3.5238],
    interaxial_angle_alpha: [90],
    interaxial_angle_beta: [90],
    interaxial_angle_gamma: [90]
})

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

                        dbc.Col(
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
                                ]
                            ), width=2
                        ),
                    ]
                ),
            ]
        ),

        html.Div(
            [
                html.H1(''),
                html.H3('Wavelength band:'),
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
        html.H2('Input elements'),
        html.Div(),

        html.Div(
            [
                html.H4('Upload .cif file(s) and/or edit table:'),
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
                html.Hr(style={'color': 'red'}),

                # dropdown
                dbc.Row(
                        [
                            html.Label("List of user defined or .cif file(s) loaded:"),
                            dcc.Dropdown(['blank'], 'blank',
                                         id=app_id_dict['cif_dropdown'],
                                         searchable=False,
                                         )
                        ]
                ),

                html.Div(html.P([html.Br()]),
                         id=app_id_dict['cif_dropdown_div']),

                html.Button('Add row', id=app_id_dict['add_row_id'], n_clicks_timestamp=0),

                dt.DataTable(
                    data=bragg_sample_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=bragg_sample_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filter_action='none',
                    sort_action='none',
                    row_deletable=True,
                    export_format='csv',
                    css=[{'selector': '.export', 'rule': 'position:absolute; left:0px; bottom:-35px'}],
                    style_cell_conditional=sample_tb_even_10_col,
                    style_data_conditional=[striped_rows],
                    id=app_id_dict['manual_input_of_elements']
                ),
                html.Div(html.P([html.Br(), html.Br()])),
                html.Hr(style={'color': 'red'}),
                html.Button('Submit',
                            style={
                                'width': '100%',
                            },
                            id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),
                html.Div(id=app_id_dict['hidden_upload_time_id'], style={'display': 'none'}, children=0),
            ],
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
                bragg_plot_option_div,
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),
                init_display_plot_data_check(app_id_dict),

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
