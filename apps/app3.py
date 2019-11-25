from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

compos_df_default = pd.DataFrame({
    chem_name: ['B4C', 'SiC'],
    compos_2nd_col_id: ['50', '50'],
})

app_name = 'app3'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        html.A('Home', href='/', target="_blank"),
        html.Br(),
        html.A(app_dict['app1']['name'], href=app_dict['app1']['url'], target="_blank"),
        html.Br(),
        html.A(app_dict['app2']['name'], href=app_dict['app2']['url'], target="_blank"),
        html.H1(app_dict['app3']['name']),

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
                    data=compos_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=compos_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filter_action='none',
                    sort_action='none',
                    row_deletable=True,
                    export_format='csv',
                    style_cell_conditional=[
                        {'if': {'column_id': chem_name},
                         'width': '50%'},
                        {'if': {'column_id': compos_2nd_col_id},
                         'width': '50%'},
                    ],
                    style_data_conditional=[striped_rows],
                    id=app_id_dict['sample_table_id']
                ),
                markdown_compos,

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
                # Effective formula and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    Output(app_id_dict['sample_table_id'], 'columns'),
    [
        Input(app_id_dict['compos_type_id'], 'value'),
    ],
    [
        State(app_id_dict['sample_table_id'], 'columns'),
    ])
def update_input_columns(compos_type, columns):
    if compos_type == weight_name:
        columns[1]['name'] = weight_name
    else:
        columns[1]['name'] = atomic_name
    return columns


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
    ])
def error(n_submit, database, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        # Test sample input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  sample_schema=compos_dict_schema,
                                                                  database=database)  # different schema)

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
        State(app_id_dict['database_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['compos_type_id'], 'value'),
    ])
def output(n_submit, test_passed, database, compos_tb_rows, iso_tb_rows, iso_changed, compos_type):
    if test_passed is True:
        # Modify input for testing
        compos_tb_dict = force_dict_to_numeric(input_dict_list=compos_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        compos_tb_df = pd.DataFrame(compos_tb_dict)
        if len(iso_changed) == 1:
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=compos_tb_df, database=database)

        # Calculation start

        # Remove rows contains no chemical input
        _compos_df = compos_tb_df[:]
        _compos_df = _compos_df[_compos_df[_compos_df.columns[0]] != '']

        _sample_df = creat_sample_df_from_compos_df(compos_tb_df=_compos_df)
        _iso_tb_df = iso_tb_df[:]

        # Calculation starts
        transmission_div_list, o_stack = form_transmission_result_div(sample_tb_rows=_sample_df.to_dict('records'),
                                                                      iso_tb_rows=_iso_tb_df.to_dict('records'),
                                                                      iso_changed=iso_changed,
                                                                      beamline='imaging',
                                                                      band_min=None,
                                                                      band_max=None,
                                                                      band_type='energy',
                                                                      database=database)
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack, full_stack=False)

        compos_output_df, ele_list, mol_list = convert_input_to_composition(compos_df=_compos_df,
                                                                            compos_type=compos_type,
                                                                            o_stack=o_stack)

        effective_formula = convert_to_effective_formula(ele_list=ele_list, mol_list=mol_list)

        output_div_list = [
            html.Hr(),
            html.H3('Result'),
            html.P('Effective chemical formula: {}'.format(effective_formula)),
            dcc.Markdown('''Above '**effective chemical formula**' can be used as '**Chemical formula**' 
            in other apps)'''),
            dt.DataTable(data=compos_output_df.to_dict('records'),
                         columns=compos_header_percent_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filter_action='none',
                         sort_action='none',
                         row_deletable=False,
                         style_cell_conditional=[
                             {'if': {'column_id': chem_name},
                              'width': '33%'},
                             {'if': {'column_id': weight_name_p},
                              'width': '33%'},
                             {'if': {'column_id': atomic_name_p},
                              'width': '33%'},
                         ],
                         ),
            html.Div(sample_stack_div_list)
        ]
        return output_div_list
    else:
        return None
