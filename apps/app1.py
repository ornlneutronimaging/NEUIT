from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

sample_df_default = pd.DataFrame({
    chem_name: ['H2O'],
    thick_name: [2],
    density_name: [1],
})

app_id_dict = init_app_ids(app_name='app1')

# Create app layout
layout = html.Div(
    [
        html.A('Home', href='/', target="_blank"),
        html.Br(),
        html.A(app_dict['app2']['name'], href=app_dict['app2']['url'], target="_blank"),
        html.Br(),
        html.A(app_dict['app3']['name'], href=app_dict['app3']['url'], target="_blank"),
        html.H1(app_dict['app1']['name']),

        # Beamline selection
        html.Div(
            [
                html.Div(
                    [
                        html.H3('Beamline'),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=app_id_dict['beamline_id'],
                                    options=[
                                        {'label': 'IMAGING (CG-1D), HFIR', 'value': 'imaging'},
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
                                html.H3('Band width',
                                        className='four columns'
                                        ),
                                dcc.RadioItems(id=app_id_dict['band_type_id'],
                                               options=[
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
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
                                          step=0.01,
                                          className='four columns',
                                          ),
                                dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.01,
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
        html.H3('Sample info'),
        html.Div(
            [
                init_upload_field(id_str=app_id_dict['sample_upload_id'],
                                  div_str=app_id_dict['error_upload_id'],
                                  hidden_div_str=app_id_dict['hidden_upload_time_id'],
                                  add_row_id=app_id_dict['add_row_id'],
                                  del_row_id=app_id_dict['del_row_id'],
                                  database_id=app_id_dict['database_id'],
                                  ),
                dt.DataTable(
                    data=sample_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=sample_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filter_action='none',
                    sort_action='none',
                    row_deletable=False,
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
    ]
)


@app.callback(
    Output(app_id_dict['band_div_id'], 'style'),
    [
        Input(app_id_dict['beamline_id'], 'value'),
    ],
    [
        State(app_id_dict['band_div_id'], 'style'),
    ])
def show_hide_band_input(beamline, style):
    if beamline == 'imaging':
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style


@app.callback(
    Output(app_id_dict['band_unit_id'], 'children'),
    [
        Input(app_id_dict['band_type_id'], 'value'),
    ])
def show_band_units(band_type):
    if band_type == 'lambda':
        return '\u212B'
    else:
        return 'eV'


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
        Input(app_id_dict['sample_table_id'], 'data'),
    ],
    [
        State(app_id_dict['iso_table_id'], 'data'),
    ])
def update_iso_table(sample_tb_rows, prev_iso_tb_rows):
    compos_tb_df = pd.DataFrame(sample_tb_rows)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_rows)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    new_iso_df = form_iso_table(sample_df=sample_df)
    new_iso_df = update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
    return new_iso_df.to_dict('records')


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
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['beamline_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_type_id'], 'value'),
    ])
def error(n_submit, database, sample_tb_rows, iso_tb_rows, iso_changed, beamline, band_min, band_max, band_type):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        # Test sample input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  sample_schema=sample_dict_schema,)
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
                iso_tb_df = form_iso_table(sample_df=sample_tb_df)

            test_passed_list, output_div_list = validate_iso_input(iso_df=iso_tb_df,
                                                                   iso_schema=iso_dict_schema,
                                                                   test_passed_list=test_passed_list,
                                                                   output_div_list=output_div_list)
        # Test band width input
        if all(test_passed_list):
            test_passed_list, output_div_list = validate_band_width_input(beamline=beamline,
                                                                          band_width=(band_min, band_max),
                                                                          band_type=band_type,
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
    Output(app_id_dict['result_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
    ],
    [
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['beamline_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_type_id'], 'value'),
    ])
def output_transmission_and_stack(n_submit, test_passed, sample_tb_rows, iso_tb_rows, iso_changed,
                                  beamline, band_min, band_max, band_type):
    if test_passed is True:
        output_div_list, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                iso_tb_rows=iso_tb_rows,
                                                                iso_changed=iso_changed,
                                                                beamline=beamline,
                                                                band_min=band_min,
                                                                band_max=band_max,
                                                                band_type=band_type)
        if beamline != 'imaging':  # add CG-1D anyway if not selected
            trans_div_list_tof, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                       iso_tb_rows=iso_tb_rows,
                                                                       iso_changed=iso_changed,
                                                                       beamline='imaging',
                                                                       band_min=band_min,
                                                                       band_max=band_max,
                                                                       band_type=band_type)
            output_div_list.extend(trans_div_list_tof)

        # Sample stack table div
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack)
        output_div_list.extend(sample_stack_div_list)

        return output_div_list
    else:
        return None
