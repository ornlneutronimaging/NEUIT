import dash_bootstrap_components as dbc
from callbacks.resonance import *

# Neutron resonance tool

energy_range_df_default = pd.DataFrame({
    energy_name: [1, 100],
    wave_name: [0.28598, 0.0286],
    speed_name: [13832.93, 138329.29],
    tof_name: [1189.1914, 118.9191],
    class_name: ['Epithermal', 'Epithermal'],
})

sample_df_default = pd.DataFrame({
    chem_name: ['Ag'],
    thick_name: ['1'],
    density_name: [''],
})

app_name = 'app2'
app_id_dict = init_app_ids(app_name=app_name)

plot_data_filename = "plot_data.csv"

# Create app2 layout
layout = html.Div(
    [

        dbc.Row([html.H2("Neutron Resonance",
                         style=({'color': 'blue'}),
                         ),
                 ],
                class_name='title_tools',
                ),
        html.Hr(style={'borderTop': '3px solid blue'}),

        # Global parameters
        html.Div(
            [
                # Range input
                html.H6('Energy range:'),
                html.Div([
                    dt.DataTable(
                        data=energy_range_df_default.to_dict('records'),
                        # optional - sets the order of columns
                        columns=energy_range_header_df.to_dict('records'),
                        editable=True,
                        row_selectable=False,
                        filter_action='none',
                        sort_action='none',
                        row_deletable=False,
                        style_cell_conditional=range_tb_even_5_col,
                        style_data_conditional=range_tb_gray_cols,
                        id=app_id_dict['range_table_id']
                    ),
                ]),
                dcc.Markdown('''NOTE: **Energy (eV)** and **Wavelength (\u212B)** columns are editable.'''),

                # Hidden div to store prev_distance
                html.Div(id=app_id_dict['hidden_prev_distance_id'], children=distance_default,
                         style={'display': 'none'}),

                # Hidden div to store range input type
                html.Div(id=app_id_dict['hidden_range_input_coord_id'], children=[0, 0], style={'display': 'none'}),

                # Step/distance input
                html.Div(
                    [
                        html.Div(
                            [
                                html.H6('Energy step:'),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id=app_id_dict['e_step_id'],
                                            options=[
                                                {'label': '0.001 (eV)  (NOT recommended if energy range > 10 eV)',
                                                 'value': 0.001},
                                                {'label': '0.01 (eV)', 'value': 0.01},
                                                {'label': '0.1 (eV)', 'value': 0.1},
                                                {'label': '1 (eV)', 'value': 1},
                                                {'label': '10 (eV)', 'value': 10},
                                                {'label': '100 (eV)', 'value': 100},
                                            ],
                                            value=0.1,
                                            searchable=False,
                                            clearable=False,
                                        ),
                                    ]
                                ),
                                dcc.Markdown(
                                    '''NOTE: Pick a suitable energy step base on the energy range selected.'''),
                            ], className='five columns', style={'verticalAlign': 'middle'},
                        ),
                        html.Div(
                            [
                                html.H6('Source-to-detector (optional):'),
                                html.Div(
                                    [
                                        dcc.Input(id=app_id_dict['distance_id'], type='number', value=distance_default,
                                                  min=1,
                                                  inputMode='numeric',
                                                  step=0.01,
                                                  className='nine columns'),
                                        html.P('(m)', className='one column',
                                               style={'marginBottom': 10, 'marginTop': 5},
                                               # style={'verticalAlign': 'middle'},
                                               ),
                                    ], className='row', style={'verticalAlign': 'middle'},
                                ),
                                dcc.Markdown(
                                    '''NOTE: Please ignore the above input field if you are **NOT** 
                                    interested in displaying results in time-of-flight (TOF).'''),
                            ], className=col_width_6,
                        ),
                    ], className='row',
                ),
            ]
        ),

        # Sample input
        html.Div(
            [
                init_upload_field(id_str=app_id_dict['sample_upload_id'],
                                  div_str=app_id_dict['error_upload_id'],
                                  hidden_div_str=app_id_dict['hidden_upload_time_id'],
                                  add_row_id=app_id_dict['add_row_id'],
                                  del_row_id=app_id_dict['del_row_id'],
                                  database_id=app_id_dict['database_id'],
                                  app_id=app_name,
                                  ),
                dt.DataTable(
                    data=sample_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=sample_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filter_action='none',
                    sort_action='none',
                    row_deletable=True,
                    export_format='csv',
                    style_cell_conditional=sample_tb_even_3_col,
                    style_data_conditional=[striped_rows],
                    id=app_id_dict['sample_table_id']
                ),
                markdown_sample,
                label_sample,

                # Input table for isotopic ratios
                dcc.Checklist(id=app_id_dict['iso_check_id'],
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': 'yes'},
                              ], value=[],
                              ),
                html.Div(
                    [
                        markdown_iso,
                        # init_upload_field(id_str=iso_upload_id),
                        init_iso_table(id_str=app_id_dict['iso_table_id'])
                    ],
                    id=app_id_dict['iso_div_id'],
                    style={'display': 'none'},
                ),
                html.Button('Submit', id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),
            ]
        ),

        # Error message div
        html.Div(id=app_id_dict['error_id'], children=None),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

        # Hidden div to store df_export json
        html.Div(id=app_id_dict['hidden_df_export_json_id'], style={'display': 'none'}),

        # Hidden div to store x_type
        html.Div(id=app_id_dict['prev_x_type_id'], children='energy', style={'display': 'none'}),

        # Output div
        html.Div(
            [
                # Plot options
                html.Div(id=app_id_dict['plot_options_div_id'], children=plot_option_div),

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

                # Transmission at CG-1D and sample stack
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
