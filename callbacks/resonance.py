from dash.dependencies import Input, Output, State
import matplotlib.pyplot as plt

from app import app
from callbacks.utilities._utilities import *
from callbacks.utilities.initialization import init_app_ids
import callbacks.utilities.constants as constants
from callbacks.utilities.validator import validate_sample_input, validate_density_input, validate_iso_input, validate_energy_input

app_name = 'resonance'
app_id_dict = init_app_ids(app_name=app_name)


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
        range_table_rows[0][constants.tof_name] = fill_range_table_by_e(e_ev=range_table_rows[0][constants.energy_name],
                                                              distance_m=distance)[constants.tof_name]
        range_table_rows[1][constants.tof_name] = fill_range_table_by_e(e_ev=range_table_rows[1][constants.energy_name],
                                                              distance_m=distance)[constants.tof_name]
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

        # Test energy range for bonded H cross-sections
        if all(test_passed_list):
            for each_chem in sample_tb_dict[constants.chem_name]:
                if each_chem in ir_util.h_bond_list:
                    for each_row in range_tb_rows:
                        if each_row[constants.wave_name] > 5.35:
                            energy_min = ir_util.angstroms_to_ev(5.35)
                            test_passed_list.append(False)
                            output_div_list.append(
                                html.P(
                                    u"INPUT ERROR: {}: ['Only wavelengths <= 5.35 \u212B are currently supported supported for bonded H cross-sections']".format(
                                        str(constants.wave_name))))
                            output_div_list.append(
                                html.P(
                                    u"INPUT ERROR: {}: ['Only wavelengths >= {} \u212B are currently supported supported for bonded H cross-sections']".format(
                                        str(constants.energy_name), energy_min)))

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
        Input('y_type', 'value'),
        Input(app_id_dict['error_id'], 'children'),
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
                          y_type,
                          test_passed,
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
        df_x[constants.energy_name] = df_y[constants.energy_name][:]
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
    [
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        Input(app_id_dict['error_id'], 'children'),
        Input('show_opt', 'value'),
        Input(app_id_dict['hidden_df_json_id'], 'children'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('plot_scale', 'value'),
    ],
    [
        State('show_opt', 'value'),
    ])
def plot(test_passed, show_opt, jsonified_data, y_type, x_type, plot_scale, prev_show_opt):
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
        jsonized_plot_df = df_to_plot.to_json(orient='split', date_format='iso')

        # Plot in matplotlib
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        try:
            ax1 = df_to_plot.set_index(keys=x_tag).plot(legend=False, ax=ax1)
        except TypeError:
            pass
        ax1.set_ylabel(y_label)

        # Convert to plotly and format layout
        plotly_fig = shape_matplot_to_plotly(fig=fig, y_type=y_type, plot_scale=plot_scale)

        return html.Div([dcc.Graph(figure=plotly_fig, id=app_id_dict['plot_fig_id'])]), [json.dumps(jsonized_plot_df)]
    else:
        return plot_loading, [None]


# @app.callback(
#     Output(app_id_dict['plot_fig_id'], 'figure'),
#     [
#         Input('plot_scale', 'value'),
#         Input('x_type', 'value'),
#     ],
#     [
#         State('y_type', 'value'),
#         State(app_id_dict['prev_x_type_id'], 'children'),
#         State(app_id_dict['plot_fig_id'], 'figure'),
#         State(app_id_dict['hidden_df_json_id'], 'children'),
#     ])
# def set_plot_scale_log_or_linear(plot_scale, x_type, y_type, prev_x_type, plotly_fig, jsonified_data):
#     # Change plot x type
#     if x_type != prev_x_type:
#         df_dict = load_dfs(jsonified_data=jsonified_data)
#         x_tag = x_type_to_x_tag(x_type=x_type)
#         for each_trace in plotly_fig['data']:
#             each_trace['x'] = df_dict['x'][x_tag]
#         plotly_fig['layout']['xaxis']['title']['text'] = x_tag
#
#     if y_type in ['attenuation', 'transmission']:
#         plotly_fig['layout']['yaxis']['autorange'] = False
#         if plot_scale in ['logy', 'loglog']:
#             plot_scale = 'linear'
#     else:
#         plotly_fig['layout']['yaxis']['autorange'] = True
#
#     # Change plot scale between log and linear
#     if plot_scale == 'logx':
#         plotly_fig['layout']['xaxis']['type'] = 'log'
#         plotly_fig['layout']['yaxis']['type'] = 'linear'
#         plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
#     elif plot_scale == 'logy':
#         if y_type not in ['attenuation', 'transmission']:
#             plotly_fig['layout']['xaxis']['type'] = 'linear'
#             plotly_fig['layout']['yaxis']['type'] = 'log'
#     elif plot_scale == 'loglog':
#         if y_type not in ['attenuation', 'transmission']:
#             plotly_fig['layout']['xaxis']['type'] = 'log'
#             plotly_fig['layout']['yaxis']['type'] = 'log'
#     else:
#         plotly_fig['layout']['xaxis']['type'] = 'linear'
#         plotly_fig['layout']['yaxis']['type'] = 'linear'
#         plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
#
#     return plotly_fig

@app.callback(
    [
        Output(app_id_dict['df_export_tb_div'], 'children'),
    ],
    [
        Input(app_id_dict['display_plot_data_id'], 'value'),
        Input(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        State(app_id_dict['error_id'], 'children'),
    ])
def display_plot_data_tb(display_check, jsonized_df_export, test_passed):
    if display_check == ['display']:
        if test_passed is True:
            dataset = json.loads(jsonized_df_export[0])
            df_to_export = pd.read_json(dataset, orient='split')
            df_tb_div_list = [
                html.Hr(),
                dt.DataTable(
                    id=app_id_dict['df_export_tb'],
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
            return [df_tb_div_list]
        else:
            return [None]
    else:
        return [None]


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
        if range_table_rows[0][constants.energy_name] < range_table_rows[1][constants.energy_name]:
            e_min = range_table_rows[0][constants.energy_name]
            e_max = range_table_rows[1][constants.energy_name]
        else:
            e_min = range_table_rows[1][constants.energy_name]
            e_max = range_table_rows[0][constants.energy_name]
        output_div_list, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                iso_tb_rows=iso_tb_rows,
                                                                iso_changed=iso_changed,
                                                                beamline='snap',
                                                                band_min=e_min,
                                                                band_max=e_max,
                                                                band_type='energy',
                                                                database=database)
        # trans_div_list_tof, o_stack_cg1d = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
        #                                                                 iso_tb_rows=iso_tb_rows,
        #                                                                 iso_changed=iso_changed,
        #                                                                 beamline='imaging',
        #                                                                 band_min=None,
        #                                                                 band_max=None,
        #                                                                 band_type=None,
        #                                                                 database=database)
        # output_div_list.extend(trans_div_list_tof)

        # Sample stack table div
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack)
        output_div_list.extend(sample_stack_div_list)
        return output_div_list
    else:
        return None
