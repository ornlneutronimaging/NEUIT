from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

compos_df_default = pd.DataFrame({
    'column_1': ['B4C', 'SiC'],
    'column_2': ['50', '50'],
    'column_3': ['1', '1'],
})

app_name = 'app3'
compos_type_id = app_name + 'compos_input_type'
add_row_id = app_name + '_add_row'
del_row_id = app_name + '_del_row'
sample_table_id = app_name + '_sample_table'
iso_check_id = app_name + '_iso_check'
iso_div_id = app_name + '_iso_input'
iso_table_id = app_name + '_iso_table'
submit_button_id = app_name + '_submit'
result_id = app_name + '_result'
error_id = app_name + '_error'
output_id = app_name + '_output'

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Cold neutron transmission', href='/apps/cg1d'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.H1('Composition converter'),

        # Sample input
        html.H3('Sample composition'),
        html.Div(
            [
                dcc.RadioItems(id=compos_type_id,
                               options=[
                                   {'label': weight_name, 'value': weight_name},
                                   {'label': atomic_name, 'value': atomic_name},
                               ],
                               value=weight_name,
                               ),
                html.Button('+', id=add_row_id, n_clicks_timestamp=0),
                html.Button('-', id=del_row_id, n_clicks_timestamp=0),
                dt.DataTable(
                    data=compos_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=compos_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filtering=False,
                    sorting=False,
                    row_deletable=True,
                    style_cell_conditional=[
                        {'if': {'column_id': column_1},
                         'width': '50%'},
                        {'if': {'column_id': column_2},
                         'width': '50%'},
                        {'if': {'column_id': column_3},
                         'width': '50%'},
                    ],
                    id=sample_table_id
                ),
                markdown_compos,
                # Input table for isotopic ratios
                dcc.Checklist(id=iso_check_id,
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': True},
                              ], values=[],
                              ),
                html.Div(
                    [
                        markdown_iso,
                        init_iso_table(id_str=iso_table_id)
                    ],
                    id=iso_div_id,
                    style={'display': 'none'},
                ),
                html.Button('Submit', id=submit_button_id),
            ]
        ),

        # Error message div
        html.Div(id=error_id, children=None),

        # Output div
        html.Div(
            [
                # Effective formula and stack info
                html.Div(id=result_id),
            ],
            id=output_id,
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    Output(sample_table_id, 'columns'),
    [
        Input(compos_type_id, 'value'),
    ])
def update_input_columns(compos_type):
    if compos_type == weight_name:
        compos_drop = atomic_name
    else:
        compos_drop = weight_name
    compos_header_df_new = compos_header_df[compos_header_df.name != compos_drop]
    return compos_header_df_new.to_dict('records')


@app.callback(
    Output(sample_table_id, 'data'),
    [
        Input(add_row_id, 'n_clicks_timestamp'),
        Input(del_row_id, 'n_clicks_timestamp')
    ],
    [
        State(sample_table_id, 'data'),
        # State('app3_sample_table', 'columns'),
        State(compos_type_id, 'value'),
    ])
def update_rows(n_add, n_del, rows, input_type):
    if n_add > n_del:
        if input_type == weight_name:
            empty_col_id = column_2
            fake_col_id = column_3
        else:
            empty_col_id = column_3
            fake_col_id = column_2
        # rows.append({c['id']: '' for c in columns})
        rows.append({'column_1': '', empty_col_id: '', fake_col_id: '1'})
    elif n_add < n_del:
        rows = rows[:-1]
    else:
        rows = rows
    return rows


@app.callback(
    Output(iso_table_id, 'data'),
    [
        Input(sample_table_id, 'data'),
    ],
    [
        State(iso_table_id, 'data'),
    ])
def update_iso_table(compos_tb_dict, prev_iso_tb_dict):
    compos_tb_df = pd.DataFrame(compos_tb_dict)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_dict)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    new_iso_df = form_iso_table(sample_df=sample_df)

    new_iso_df = update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
    return new_iso_df.to_dict('records')


@app.callback(
    Output(iso_div_id, 'style'),
    [
        Input(iso_check_id, 'values'),
    ])
def show_hide_iso_table(iso_changed):
    if iso_changed:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output(output_id, 'style'),
    [
        Input(submit_button_id, 'n_clicks'),
        Input(error_id, 'children'),
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
    Output(error_id, 'children'),
    [
        Input(submit_button_id, 'n_clicks'),
    ],
    [
        State(sample_table_id, 'data'),
        State(iso_table_id, 'data'),
        State(iso_check_id, 'values'),
    ])
def error(n_submit, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        if iso_changed:
            iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=sample_tb_df)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=compos_dict_schema,  # different schema
                                                                  iso_schema=iso_dict_schema)
        # Return result
        if all(test_passed_list):
            return True
        else:
            return output_div_list
    else:
        return None


@app.callback(
    Output(result_id, 'children'),
    [
        Input(submit_button_id, 'n_clicks'),
        Input(error_id, 'children'),
    ],
    [
        State(sample_table_id, 'data'),
        State(iso_table_id, 'data'),
        State(iso_check_id, 'values'),
        State(compos_type_id, 'value'),
    ])
def output(n_submit, test_passed, compos_tb_rows, iso_tb_rows, iso_changed, compos_type):
    if test_passed is True:
        # Modify input for testing
        compos_tb_dict = force_dict_to_numeric(input_dict_list=compos_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        compos_tb_df = pd.DataFrame(compos_tb_dict)
        if iso_changed:
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=compos_tb_df)

        # Calculation start
        if compos_type == weight_name:
            _col_name = column_2
            _rm_name = column_3
        else:
            _col_name = column_3
            _rm_name = column_2

        # Remove rows contains no chemical input
        _compos_df = compos_tb_df[:]
        _compos_df = _compos_df[_compos_df.column_1 != '']
        _compos_df = drop_df_column_not_needed(input_df=_compos_df, column_name=_rm_name)
        _sample_df = creat_sample_df_from_compos_df(compos_tb_df=_compos_df)
        _iso_tb_df = iso_tb_df[:]

        # Calculation starts
        total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(sample_tb_df=_sample_df,
                                                                                          iso_tb_df=_iso_tb_df,
                                                                                          iso_changed=iso_changed)
        compos_output_df, ele_list, mol_list = convert_input_to_composition(compos_df=_compos_df,
                                                                            compos_type=compos_type,
                                                                            o_stack=o_stack)

        effective_formula = convert_to_effective_formula(ele_list=ele_list, mol_list=mol_list)

        output_div_list = [
            html.Hr(),
            html.H3('Result'),
            html.P('The effective chemical formula after conversion: {}'.format(effective_formula)),
            html.P("(This can be passed as 'Chemical formula' for other apps)"),
            dt.DataTable(data=compos_output_df.to_dict('records'),
                         columns=compos_header_p_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filtering=False,
                         sorting=False,
                         row_deletable=False,
                         style_cell_conditional=[
                             {'if': {'column_id': column_1},
                              'width': '33%'},
                             {'if': {'column_id': column_2},
                              'width': '33%'},
                             {'if': {'column_id': column_3},
                              'width': '33%'},
                         ],
                         ),
            html.Div([html.H5('Sample stack:'), html.Div(div_list)])
        ]
        return output_div_list
    else:
        return None
