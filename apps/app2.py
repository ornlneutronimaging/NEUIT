from dash.dependencies import Input, Output, State
from _app import app
import plotly.tools as tls
import matplotlib.pyplot as plt
from _utilities import *

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
distance_default = 16.45
plot_loading = html.H2('Plot loading...')

# Create app2 layout
layout = html.Div(
    [
        html.A('Home', href='/', target="_blank"),
        html.Br(),
        # dcc.Link(app_dict['app1']['name'], href=app_dict['app1']['url']),
        html.A(app_dict['app1']['name'], href=app_dict['app1']['url'], target="_blank"),
        html.Br(),
        html.A(app_dict['app3']['name'], href=app_dict['app3']['url'], target="_blank"),
        html.H1(app_dict['app2']['name']),
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

        # Hidden div to store json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

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
                        html.Button(
                            'Display data table',
                            id=app_id_dict['export_plot_data_button_id'],
                            style={'display': 'inline-block'},
                            n_clicks_timestamp=0
                        ),
                        html.Div(
                            id=app_id_dict['export_plot_data_notice_id'],
                            style={'display': 'inline-block'},
                        ),
                    ], className='row'
                ),
                # Data table for the plotted data
                html.Div(id=app_id_dict['hidden_df_tb_div']),

                # Transmission at CG-1D and sample stack
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    Output(app_id_dict['hidden_range_input_coord_id'], 'children'),
    [
        Input(app_id_dict['range_table_id'], 'data_timestamp'),
    ],
    [
        State(app_id_dict['range_table_id'], 'data'),
        State(app_id_dict['range_table_id'], 'data_previous'),
    ])
def update_range_input_type(timestamp, new_range_tb_rows, old_range_tb_rows):
    old_range_tb_df = pd.DataFrame(old_range_tb_rows)
    new_range_tb_df = pd.DataFrame(new_range_tb_rows)
    diff_indices = new_range_tb_df.round(5) == old_range_tb_df.round(5)
    _coord = np.where(diff_indices == False)
    if len(_coord[0]) != 1 or len(_coord[1]) != 1:
        print('Old:\n{}'.format(old_range_tb_df))
        print('New:\n{}'.format(new_range_tb_df))
        print(diff_indices)
        print(_coord)
        raise ValueError('Multiple input fields have been modified in the range table')
    modified_coord = (_coord[0][0], _coord[1][0])
    return modified_coord


@app.callback(
    [
        Output(app_id_dict['range_table_id'], 'data'),
        Output(app_id_dict['hidden_prev_distance_id'], 'children'),
    ],
    [
        Input(app_id_dict['range_table_id'], 'data_timestamp'),
        Input(app_id_dict['hidden_range_input_coord_id'], 'children'),
        Input(app_id_dict['distance_id'], 'value'),
    ],
    [
        State(app_id_dict['hidden_prev_distance_id'], 'children'),
        State(app_id_dict['range_table_id'], 'data'),
    ])
def form_range_table(timestamp, modified_coord, distance, prev_distance, range_table_rows):
    if distance == prev_distance:
        range_table_rows = update_range_tb_by_coordinate(range_table_rows=range_table_rows,
                                                         distance=distance,
                                                         modified_coord=modified_coord)
    else:
        range_table_rows[0][tof_name] = fill_range_table_by_e(e_ev=range_table_rows[0][energy_name],
                                                              distance_m=distance)[tof_name]
        range_table_rows[1][tof_name] = fill_range_table_by_e(e_ev=range_table_rows[1][energy_name],
                                                              distance_m=distance)[tof_name]
    return range_table_rows, distance


@app.callback(
    [
        Output(app_id_dict['sample_table_id'], 'data'),
        Output(app_id_dict['error_upload_id'], 'children'),
        Output(app_id_dict['hidden_upload_time_id'], 'children'),
    ],
    [
        Input(app_id_dict['add_row_id'], 'n_clicks_timestamp'),
        Input(app_id_dict['del_row_id'], 'n_clicks_timestamp'),
        Input(app_id_dict['sample_upload_id'], 'contents'),
        Input(app_id_dict['sample_upload_id'], 'last_modified'),
    ],
    [
        State(app_id_dict['hidden_upload_time_id'], 'children'),
        State(app_id_dict['sample_upload_id'], 'filename'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['sample_table_id'], 'columns')
    ])
def update_rows(n_add, n_del, list_of_contents, upload_time, prev_upload_time, list_of_names, rows, columns):
    rows, error_message, upload_t = update_rows_util(n_add=n_add,
                                                     n_del=n_del,
                                                     list_of_contents=list_of_contents,
                                                     upload_time=upload_time,
                                                     prev_upload_time=prev_upload_time,
                                                     list_of_names=list_of_names,
                                                     rows=rows,
                                                     columns=columns)
    return rows, error_message, upload_t


@app.callback(
    Output(app_id_dict['iso_table_id'], 'data'),
    [
        Input(app_id_dict['database_id'], 'value'),
        Input(app_id_dict['sample_table_id'], 'data'),
    ],
    [
        State(app_id_dict['iso_table_id'], 'data'),
    ])
def update_iso_table(database, sample_tb_rows, prev_iso_tb_rows):
    return_dict = update_iso_table_callback(sample_tb_rows=sample_tb_rows,
                                            prev_iso_tb_rows=prev_iso_tb_rows,
                                            database=database)
    return return_dict


@app.callback(
    Output(app_id_dict['iso_div_id'], 'style'),
    [
        Input(app_id_dict['iso_check_id'], 'value'),
    ],
    [
        State(app_id_dict['iso_div_id'], 'style'),
    ])
def show_hide_iso_table(iso_changed, style):
    if len(iso_changed) == 1:
        style['display'] = 'block'
    else:
        style['display'] = 'none'
    return style


@app.callback(
    Output('show_opt', 'options'),
    [
        Input('y_type', 'value'),
    ])
def disable_show_options(y_type):
    if y_type in ['attenuation', 'transmission']:
        options = [
            {'label': 'Total', 'value': 'total'},
            {'label': 'Layer', 'value': 'layer'},
            {'label': 'Element', 'value': 'ele'},
            {'label': 'Isotope', 'value': 'iso'},
        ]
    elif y_type == 'mu_per_cm':
        options = [
            {'label': 'Layer', 'value': 'layer'},
            {'label': 'Element', 'value': 'ele'},
            {'label': 'Isotope', 'value': 'iso'},
        ]
    elif y_type[-3:] == 'raw':
        options = [
            {'label': 'Isotope', 'value': 'iso'},
        ]
    else:
        options = [
            {'label': 'Element', 'value': 'ele'},
            {'label': 'Isotope', 'value': 'iso'},
        ]
    return options


@app.callback(
    Output('plot_scale', 'options'),
    [
        Input('y_type', 'value'),
    ])
def disable_plot_scale_options(y_type):
    if y_type in ['attenuation', 'transmission']:
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
        ]
    else:
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
            {'label': 'Log y', 'value': 'logy'},
            {'label': 'Loglog', 'value': 'loglog'},
        ]
    return options


@app.callback(
    Output(app_id_dict['output_id'], 'style'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
    ])
def show_output_div(n_submit, test_passed):
    if n_submit is not None:
        if test_passed is True:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@app.callback(
    Output(app_id_dict['error_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
    ],
    [
        State(app_id_dict['database_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['range_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
    ])
def error(n_submit, database, sample_tb_rows, iso_tb_rows, range_tb_rows, iso_changed):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        # Test sample input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  sample_schema=sample_dict_schema,
                                                                  database=database)
        # Test density required or not
        if all(test_passed_list):
            test_passed_list, output_div_list = validate_density_input(sample_tb_df=sample_tb_df,
                                                                       test_passed_list=test_passed_list,
                                                                       output_div_list=output_div_list)
        # Test iso input format and sum
        if all(test_passed_list):
            if len(iso_changed) == 1:
                iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
                iso_tb_df = pd.DataFrame(iso_tb_dict)
            else:
                iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)

            test_passed_list, output_div_list = validate_iso_input(iso_df=iso_tb_df,
                                                                   iso_schema=iso_dict_schema,
                                                                   test_passed_list=test_passed_list,
                                                                   output_div_list=output_div_list,
                                                                   database=database)
        # Test range table
        if all(test_passed_list):
            range_tb_dict = force_dict_to_numeric(input_dict_list=range_tb_rows)
            range_tb_df = pd.DataFrame(range_tb_dict)

            test_passed_list, output_div_list = validate_energy_input(range_tb_df=range_tb_df,
                                                                      test_passed_list=test_passed_list,
                                                                      output_div_list=output_div_list)

        # Return result
        if all(test_passed_list):
            return True
        else:
            return output_div_list
    else:
        return None


@app.callback(
    Output(app_id_dict['prev_x_type_id'], 'children'),
    [
        Input('x_type', 'value'),
    ])
def store_x_type(x_type):
    return x_type


@app.callback(
    Output(app_id_dict['hidden_df_json_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
        Input('y_type', 'value'),
    ],
    [
        State(app_id_dict['range_table_id'], 'data'),
        State(app_id_dict['e_step_id'], 'value'),
        State(app_id_dict['distance_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['database_id'], 'value'),
    ])
def store_reso_df_in_json(n_submit,
                          test_passed,
                          y_type,
                          range_tb_rows, e_step, distance_m,
                          sample_tb_rows, iso_tb_rows,
                          iso_changed, database):
    if test_passed is True:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        if len(iso_changed) == 1:
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)

        # Calculation starts
        range_tb_df = pd.DataFrame(range_tb_rows)
        o_reso = init_reso_from_tb(range_tb_df=range_tb_df, e_step=e_step, database=database)
        o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=sample_tb_df)
        o_reso = unpack_iso_tb_df_and_update(o_reso=o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)

        # Get dfs from o_reso stacks
        df_y = o_reso.export(y_axis=y_type,
                             x_axis='energy',
                             time_unit='us',
                             mixed=True,
                             all_layers=True,
                             all_elements=True,
                             all_isotopes=True,
                             source_to_detector_m=distance_m,
                             output_type='df')

        df_x = pd.DataFrame()
        df_x[energy_name] = df_y[energy_name][:]
        df_x = fill_df_x_types(df=df_x, distance_m=distance_m)

        df_y.drop(columns=[df_y.columns[0]], inplace=True)  # Drop x-axis row

        datasets = {
            'x': df_x.to_json(orient='split', date_format='iso'),
            'y': df_y.to_json(orient='split', date_format='iso'),
        }
        return json.dumps(datasets)
    else:
        return None


@app.callback(
    Output(app_id_dict['plot_div_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
        Input('show_opt', 'value'),
        Input(app_id_dict['hidden_df_json_id'], 'children'),
        Input('y_type', 'value'),
    ],
    [
        State('x_type', 'value'),
        State('show_opt', 'value'),
        State('plot_scale', 'value'),
    ])
def plot(n_submit, test_passed, show_opt, jsonified_data, y_type, x_type, prev_show_opt, plot_scale):
    if test_passed is True:
        # Load and shape the data
        df_x, df_y, to_plot_list, x_tag, y_label = shape_reso_df_to_output(x_type=x_type,
                                                                           y_type=y_type,
                                                                           show_opt=show_opt,
                                                                           jsonified_data=jsonified_data,
                                                                           prev_show_opt=prev_show_opt,
                                                                           to_csv=False)
        df_to_plot = df_y[to_plot_list]
        df_to_plot.insert(loc=0, column=x_tag, value=df_x[x_tag])

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        # Plot
        try:
            ax1 = df_to_plot.set_index(keys=x_tag).plot(legend=False, ax=ax1)
        except TypeError:
            pass
        ax1.set_ylabel(y_label)

        plotly_fig = tls.mpl_to_plotly(fig)

        # Layout
        plotly_fig.layout.showlegend = True
        plotly_fig.layout.autosize = True
        plotly_fig.layout.height = 600
        plotly_fig.layout.width = 900
        plotly_fig.layout.margin = {'b': 52, 'l': 80, 'pad': 0, 'r': 15, 't': 15}
        plotly_fig.layout.xaxis1.tickfont.size = 15
        plotly_fig.layout.xaxis1.titlefont.size = 18
        plotly_fig.layout.yaxis1.tickfont.size = 15
        plotly_fig.layout.yaxis1.titlefont.size = 18
        plotly_fig.layout.xaxis.autorange = True
        if y_type in ['attenuation', 'transmission']:
            plotly_fig['layout']['yaxis']['autorange'] = False
            if plot_scale in ['logy', 'loglog']:
                plot_scale = 'linear'
        else:
            plotly_fig['layout']['yaxis']['autorange'] = True

        if plot_scale == 'logx':
            plotly_fig['layout']['xaxis']['type'] = 'log'
            plotly_fig['layout']['yaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
        elif plot_scale == 'logy':
            if y_type not in ['attenuation', 'transmission']:
                plotly_fig['layout']['xaxis']['type'] = 'linear'
                plotly_fig['layout']['yaxis']['type'] = 'log'
        elif plot_scale == 'loglog':
            if y_type not in ['attenuation', 'transmission']:
                plotly_fig['layout']['xaxis']['type'] = 'log'
                plotly_fig['layout']['yaxis']['type'] = 'log'
        else:
            plotly_fig['layout']['xaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]

        return html.Div([dcc.Graph(figure=plotly_fig, id=app_id_dict['plot_fig_id'])])
    else:
        return plot_loading


@app.callback(
    Output(app_id_dict['plot_fig_id'], 'figure'),
    [
        Input('plot_scale', 'value'),
        Input('x_type', 'value'),
    ],
    [
        State('y_type', 'value'),
        State(app_id_dict['prev_x_type_id'], 'children'),
        State(app_id_dict['plot_fig_id'], 'figure'),
        State(app_id_dict['hidden_df_json_id'], 'children'),
    ])
def set_plot_scale_log_or_linear(plot_scale, x_type, y_type, prev_x_type, plotly_fig, jsonified_data):
    # Change plot x type
    if x_type != prev_x_type:
        df_dict = load_dfs(jsonified_data=jsonified_data)
        x_tag = x_type_to_x_tag(x_type=x_type)
        for each_trace in plotly_fig['data']:
            each_trace['x'] = df_dict['x'][x_tag]
        plotly_fig['layout']['xaxis']['title']['text'] = x_tag

    if y_type in ['attenuation', 'transmission']:
        plotly_fig['layout']['yaxis']['autorange'] = False
        if plot_scale in ['logy', 'loglog']:
            plot_scale = 'linear'
    else:
        plotly_fig['layout']['yaxis']['autorange'] = True

    # Change plot scale between log and linear
    if plot_scale == 'logx':
        plotly_fig['layout']['xaxis']['type'] = 'log'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
    elif plot_scale == 'logy':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    elif plot_scale == 'loglog':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'log'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    else:
        plotly_fig['layout']['xaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]

    return plotly_fig


@app.callback(
    Output(app_id_dict['result_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
    ],
    [
        State(app_id_dict['database_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['range_table_id'], 'data'),
    ])
def output_transmission_and_stack(n_submit, test_passed, database,
                                  sample_tb_rows, iso_tb_rows, iso_changed, range_table_rows):
    if test_passed is True:
        if range_table_rows[0][energy_name] < range_table_rows[1][energy_name]:
            e_min = range_table_rows[0][energy_name]
            e_max = range_table_rows[1][energy_name]
        else:
            e_min = range_table_rows[1][energy_name]
            e_max = range_table_rows[0][energy_name]
        output_div_list, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                iso_tb_rows=iso_tb_rows,
                                                                iso_changed=iso_changed,
                                                                beamline='snap',
                                                                band_min=e_min,
                                                                band_max=e_max,
                                                                band_type='energy',
                                                                database=database)
        trans_div_list_tof, o_stack_cg1d = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                        iso_tb_rows=iso_tb_rows,
                                                                        iso_changed=iso_changed,
                                                                        beamline='imaging',
                                                                        band_min=None,
                                                                        band_max=None,
                                                                        band_type=None,
                                                                        database=database)
        output_div_list.extend(trans_div_list_tof)

        # Sample stack table div
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack)
        output_div_list.extend(sample_stack_div_list)
        return output_div_list
    else:
        return None


@app.callback(
    [
        Output(app_id_dict['hidden_df_tb_div'], 'children'),
        Output(app_id_dict['export_plot_data_notice_id'], 'children'),
    ],
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks_timestamp'),
        Input(app_id_dict['export_plot_data_button_id'], 'n_clicks_timestamp'),
    ],
    [
        State('x_type', 'value'),
        State('y_type', 'value'),
        State('show_opt', 'value'),
        State(app_id_dict['error_id'], 'children'),
        State(app_id_dict['hidden_df_json_id'], 'children'),
    ])
def export_plot_data(n_submit, n_export, x_type, y_type, show_opt, test_passed, jsonified_data):
    if n_export != 0:
        if n_export > n_submit:
            if test_passed is True:
                # Load and shape the data
                df_x, df_y, to_export_list, x_tag, y_label = shape_reso_df_to_output(x_type=x_type,
                                                                                     y_type=y_type,
                                                                                     show_opt=show_opt,
                                                                                     jsonified_data=jsonified_data,
                                                                                     prev_show_opt=None,
                                                                                     to_csv=True)
                df_to_export = df_y[to_export_list]
                x_tag = x_type_to_x_tag(x_type)
                df_to_export.insert(loc=0, column=x_tag, value=df_x[x_tag])
                # df_to_export.insert(loc=0, column=tof_name, value=df_x[tof_name])
                # df_to_export.insert(loc=0, column=wave_name, value=df_x[wave_name])
                # df_to_export.insert(loc=0, column=energy_name, value=df_x[energy_name])

                # df_to_export.to_clipboard(index=False, excel=True)  # Does not work on the Heroku server
                df_tb_div_list = [
                    html.Hr(),
                    dt.DataTable(
                        id=app_id_dict['hidden_df_tb'],
                        data=df_to_export.to_dict('records'),
                        columns=[{'name': each_col, 'id': each_col} for each_col in df_to_export.columns],
                        export_format='csv',
                        style_data_conditional=[striped_rows],
                        fixed_rows={'headers': True, 'data': 0},
                        style_table={
                            'maxHeight': '300',
                            'overflowY': 'scroll',
                        },
                    )
                ]
                return df_tb_div_list, '\u2705'
            else:
                return None, None
        else:
            return None, None
    else:
        return None, None
