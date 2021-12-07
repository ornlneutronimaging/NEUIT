# from dash import html
# from dash import dcc
# from dash import dash_table as dt
# from config import app
# from _utilities import *
# from dash.dependencies import Input, Output, State
#
# from app import app
import dash_bootstrap_components as dbc
from callbacks.transmission import *

sample_df_default = pd.DataFrame({
    chem_name: ['H2O'],
    thick_name: [2],
    density_name: [1],
})

app_name = 'app1'
app_id_dict = init_app_ids(app_name=app_name)

layout = html.Div(
        [
            dbc.Row([html.H2("Neutron Transmission",
                             style=({'color': 'blue'}),
                             ),
                     ],
                    class_name='title_tools',
            ),
            html.Hr(style={'borderTop': '3px solid blue'}),
            # Beamline selection
            html.Div(
                    [
                        html.Div(
                                [
                                    html.H6('Beam spectrum from:'),
                                    html.Div(
                                            [
                                                dcc.Dropdown(
                                                        id=app_id_dict['beamline_id'],
                                                        options=[
                                                            {'label': 'IMAGING (CG-1D), HFIR', 'value': 'imaging'},
                                                            {'label': u'IMAGING (CG-1D) \u2264 5.35 \u212B, HFIR',
                                                             'value': 'imaging_crop'},
                                                            {'label': 'SNAP (BL-3), SNS', 'value': 'snap'},
                                                            # {'label': 'SNS, VENUS (BL-10)', 'value': 'venus'},
                                                        ],
                                                        value='imaging',
                                                        searchable=False,
                                                        clearable=False,
                                                ),
                                            ]
                                    ),
                                ], className='five columns', style={'verticalAlign': 'middle'},
                        ),
                        html.Div(
                                [
                                    html.Div(
                                            [
                                                html.H6('Band width:',
                                                        className='four columns'
                                                        ),
                                                dcc.RadioItems(id=app_id_dict['band_type_id'],
                                                               options=[
                                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                                   {'label': 'Wavelength (\u212B)',
                                                                    'value': 'lambda'},
                                                               ],
                                                               value='lambda',
                                                               className='four columns',
                                                               labelStyle={'display': 'inline-block'},
                                                               ),
                                            ], className='row'
                                    ),
                                    html.Div(
                                            [
                                                dcc.Input(id=app_id_dict['band_min_id'], type='number',
                                                          inputMode='numeric',
                                                          placeholder='Min.',
                                                          step=0.001,
                                                          className='four columns',
                                                          ),
                                                dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                                          inputMode='numeric',
                                                          placeholder='Max.',
                                                          step=0.001,
                                                          className='four columns',
                                                          ),
                                                html.P('\u212B',
                                                       id=app_id_dict['band_unit_id'],
                                                       style={'marginBottom': 10, 'marginTop': 5},
                                                       className='one column',
                                                       ),
                                            ], className='row', style={'verticalAlign': 'middle'},
                                    ),
                                ], className=col_width_6, style={'display': 'none'}, id=app_id_dict['band_div_id'],
                        ),
                    ], className='row',
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
                                    init_iso_table(id_str=app_id_dict['iso_table_id'])
                                ],
                                id=app_id_dict['iso_div_id'],
                                style={'display': 'none'},
                        ),
                        html.Button('Submit', id=app_id_dict['submit_button_id']),
                    ]
            ),

            # Error message div
            html.Div(id=app_id_dict['error_id'], children=None),

            # Output div
            html.Div(
                    [
                        # Transmission at CG-1D and stack info
                        html.Div(id=app_id_dict['result_id']),
                    ],
                    id=app_id_dict['output_id'],
                    style={'display': 'none'},
            ),
        ],
        style={'margin': '25px'}
)

# @app.callback(
#     Output(app_id_dict['app_info_id'], 'style'),
#     [
#         Input(app_id_dict['more_about_app_id'], 'value'),
#     ],
#     [
#         State(app_id_dict['app_info_id'], 'style'),
#     ])
# def show_hide_band_input(more_info, style):
#     if more_info != ['more']:
#         style['display'] = 'none'
#     else:
#         style['display'] = 'block'
#     return style
#
#
# @app.callback(
#     Output(app_id_dict['band_div_id'], 'style'),
#     [
#         Input(app_id_dict['beamline_id'], 'value'),
#     ],
#     [
#         State(app_id_dict['band_div_id'], 'style'),
#     ])
# def show_hide_band_input(beamline, style):
#     if beamline in ['imaging', 'imaging_crop']:
#         style['display'] = 'none'
#     else:
#         style['display'] = 'block'
#     return style
#
#
# @app.callback(
#     Output(app_id_dict['band_unit_id'], 'children'),
#     [
#         Input(app_id_dict['band_type_id'], 'value'),
#     ])
# def show_band_units(band_type):
#     if band_type == 'lambda':
#         return '\u212B'
#     else:
#         return 'eV'
#
#
# @app.callback(
#     [
#         Output(app_id_dict['sample_table_id'], 'data'),
#         Output(app_id_dict['error_upload_id'], 'children'),
#         Output(app_id_dict['hidden_upload_time_id'], 'children'),
#     ],
#     [
#         Input(app_id_dict['add_row_id'], 'n_clicks_timestamp'),
#         Input(app_id_dict['del_row_id'], 'n_clicks_timestamp'),
#         Input(app_id_dict['sample_upload_id'], 'contents'),
#         Input(app_id_dict['sample_upload_id'], 'last_modified'),
#     ],
#     [
#         State(app_id_dict['hidden_upload_time_id'], 'children'),
#         State(app_id_dict['sample_upload_id'], 'filename'),
#         State(app_id_dict['sample_table_id'], 'data'),
#         State(app_id_dict['sample_table_id'], 'columns')
#     ])
# def update_rows(n_add, n_del, list_of_contents, upload_time, prev_upload_time, list_of_names, rows, columns):
#     rows, error_message, upload_t = update_rows_util(n_add=n_add,
#                                                      n_del=n_del,
#                                                      list_of_contents=list_of_contents,
#                                                      upload_time=upload_time,
#                                                      prev_upload_time=prev_upload_time,
#                                                      list_of_names=list_of_names,
#                                                      rows=rows,
#                                                      columns=columns)
#     return rows, error_message, upload_t
#
#
# @app.callback(
#     Output(app_id_dict['iso_table_id'], 'data'),
#     [
#         Input(app_id_dict['database_id'], 'value'),
#         Input(app_id_dict['sample_table_id'], 'data'),
#
#     ],
#     [
#         State(app_id_dict['iso_table_id'], 'data'),
#     ])
# def update_iso_table(database, sample_tb_rows, prev_iso_tb_rows):
#     return_dict = update_iso_table_callback(sample_tb_rows=sample_tb_rows,
#                                             prev_iso_tb_rows=prev_iso_tb_rows,
#                                             database=database)
#     return return_dict
#
#
# @app.callback(
#     Output(app_id_dict['iso_div_id'], 'style'),
#     [
#         Input(app_id_dict['iso_check_id'], 'value'),
#     ],
#     [
#         State(app_id_dict['iso_div_id'], 'style'),
#     ])
# def show_hide_iso_table(iso_changed, style):
#     if len(iso_changed) == 1:
#         style['display'] = 'block'
#     else:
#         style['display'] = 'none'
#     return style
#
#
# @app.callback(
#     Output(app_id_dict['output_id'], 'style'),
#     [
#         Input(app_id_dict['submit_button_id'], 'n_clicks'),
#         Input(app_id_dict['error_id'], 'children'),
#     ])
# def show_output_div(n_submit, test_passed):
#     if n_submit is not None:
#         if test_passed is True:
#             return {'display': 'block'}
#         else:
#             return {'display': 'none'}
#     else:
#         return {'display': 'none'}
#
#
# @app.callback(
#     Output(app_id_dict['error_id'], 'children'),
#     [
#         Input(app_id_dict['submit_button_id'], 'n_clicks'),
#     ],
#     [
#         State(app_id_dict['database_id'], 'value'),
#         State(app_id_dict['sample_table_id'], 'data'),
#         State(app_id_dict['iso_table_id'], 'data'),
#         State(app_id_dict['iso_check_id'], 'value'),
#         State(app_id_dict['beamline_id'], 'value'),
#         State(app_id_dict['band_min_id'], 'value'),
#         State(app_id_dict['band_max_id'], 'value'),
#         State(app_id_dict['band_type_id'], 'value'),
#     ])
#
#
# def error(n_submit, database, sample_tb_rows, iso_tb_rows, iso_changed, beamline, band_min, band_max, band_type):
#     if n_submit is not None:
#         # Convert all number str to numeric and keep rest invalid input
#         sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
#         sample_tb_df = pd.DataFrame(sample_tb_dict)
#
#         # Test sample input format
#         test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
#                                                                   sample_schema=sample_dict_schema,
#                                                                   database=database)
#         # Test density required or not
#         if all(test_passed_list):
#             test_passed_list, output_div_list = validate_density_input(sample_tb_df=sample_tb_df,
#                                                                        test_passed_list=test_passed_list,
#                                                                        output_div_list=output_div_list)
#         # Test iso input format and sum
#         if all(test_passed_list):
#             if len(iso_changed) == 1:
#                 iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
#                 iso_tb_df = pd.DataFrame(iso_tb_dict)
#             else:
#                 iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)
#
#             test_passed_list, output_div_list = validate_iso_input(iso_df=iso_tb_df,
#                                                                    iso_schema=iso_dict_schema,
#                                                                    test_passed_list=test_passed_list,
#                                                                    output_div_list=output_div_list,
#                                                                    database=database)
#         # Test band width input
#         if all(test_passed_list):
#             test_passed_list, output_div_list = validate_band_width_input(beamline=beamline,
#                                                                           band_width=(band_min, band_max),
#                                                                           band_type=band_type,
#                                                                           test_passed_list=test_passed_list,
#                                                                           output_div_list=output_div_list)
#
#         # Test energy range for bonded H cross-sections
#         if all(test_passed_list):
#             for each_chem in sample_tb_dict[chem_name]:
#                 if each_chem in ir_util.h_bond_list:
#                     if beamline == 'imaging':
#                         test_passed_list.append(False)
#                         output_div_list.append(
#                             html.P(
#                                 u"SPECTRUM ERROR: ['Only wavelengths <= 5.35 \u212B are currently supported for bonded H cross-sections in '{}'']".format(
#                                     each_chem)))
#                         output_div_list.append(
#                             html.P(u"Please use spectrum: ['IMAGING (CG-1D) \u2264 5.35 \u212B, HFIR']"))
#                     elif beamline == 'imaging_crop':
#                         test_passed_list.append(True)
#                     else:
#                         if band_type == 'lambda':
#                             if band_max > 5.35:
#                                 test_passed_list.append(False)
#                                 output_div_list.append(
#                                     html.P(
#                                         u"BAND WIDTH ERROR: ['Only wavelengths <= 5.35 \u212B are currently supported supported for bonded H cross-sections in '{}'']".format(
#                                             each_chem)
#                                     ))
#                         if band_type == 'energy':
#                             wave_max = ir_util.ev_to_angstroms(band_min)
#                             energy_min = ir_util.angstroms_to_ev(5.35)
#                             if wave_max > 5.35:
#                                 test_passed_list.append(False)
#                                 output_div_list.append(
#                                     html.P(
#                                         u"BAND WIDTH ERROR: ['Only energies >= {} eV are currently supported supported for bonded H cross-sections in '{}'']".format(
#                                             energy_min, each_chem)))
#
#         # Return result
#         if all(test_passed_list):
#             return True
#         else:
#             return output_div_list
#     else:
#         return None
#
#
# @app.callback(
#     Output(app_id_dict['result_id'], 'children'),
#     [
#         Input(app_id_dict['submit_button_id'], 'n_clicks'),
#         Input(app_id_dict['error_id'], 'children'),
#     ],
#     [
#         State(app_id_dict['database_id'], 'value'),
#         State(app_id_dict['sample_table_id'], 'data'),
#         State(app_id_dict['iso_table_id'], 'data'),
#         State(app_id_dict['iso_check_id'], 'value'),
#         State(app_id_dict['beamline_id'], 'value'),
#         State(app_id_dict['band_min_id'], 'value'),
#         State(app_id_dict['band_max_id'], 'value'),
#         State(app_id_dict['band_type_id'], 'value'),
#     ])
# def output_transmission_and_stack(n_submit, test_passed, database, sample_tb_rows, iso_tb_rows, iso_changed,
#                                   beamline, band_min, band_max, band_type):
#     if test_passed is True:
#         output_div_list, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
#                                                                 iso_tb_rows=iso_tb_rows,
#                                                                 iso_changed=iso_changed,
#                                                                 beamline=beamline,
#                                                                 band_min=band_min,
#                                                                 band_max=band_max,
#                                                                 band_type=band_type,
#                                                                 database=database)
#         if beamline != 'imaging':  # add CG-1D anyway if not selected
#             try:
#                 trans_div_list_tof, o_stack_cg1d = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
#                                                                                 iso_tb_rows=iso_tb_rows,
#                                                                                 iso_changed=iso_changed,
#                                                                                 beamline='imaging',
#                                                                                 band_min=band_min,
#                                                                                 band_max=band_max,
#                                                                                 band_type=band_type,
#                                                                                 database=database)
#                 output_div_list.extend(trans_div_list_tof)
#             except Exception:
#                 pass
#
#         # Sample stack table div
#         sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack)
#         output_div_list.extend(sample_stack_div_list)
#
#         return output_div_list
#     else:
#         return None
