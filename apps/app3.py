from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

compos_df_default = pd.DataFrame({
    'column_1': ['B4C', 'SiC'],
    'column_2': ['50', '50'],
    'column_3': ['1', '1'],
})

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Cold neutron transmission', href='/apps/cg1d'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.H1('Composition converter'),
        html.H3('Sample composition'),

        html.Div(
            [
                dcc.RadioItems(id='app3_compos_input_type',
                               options=[
                                   {'label': weight_name, 'value': weight_name},
                                   {'label': atomic_name, 'value': atomic_name},
                               ],
                               value=weight_name,
                               )
            ]
        ),

        # Sample input
        html.Div(
            [
                html.Button('Add Row', id='app3_add_row', n_clicks=0),
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
                    id='app3_sample_table'
                ),
                markdown_sample,
                # Input table for isotopic ratios
                dcc.Checklist(id='app3_iso_check',
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': True},
                              ], values=[],
                              ),
                html.Div(
                    [
                        markdown_iso,
                        dt.DataTable(
                            data=iso_tb_df_default.to_dict('records'),
                            columns=iso_tb_header_df.to_dict('records'),
                            editable=True,
                            row_selectable=False,
                            filtering=False,
                            sorting=False,
                            row_deletable=False,
                            style_cell_conditional=[
                                {'if': {'column_id': column_1},
                                 'width': '25%'},
                                {'if': {'column_id': column_2},
                                 'width': '25%'},
                                {'if': {'column_id': column_3},
                                 'width': '25%'},
                                {'if': {'column_id': column_4},
                                 'width': '25%'},
                            ],
                            style_table={
                                'maxHeight': '300',
                                'overflowY': 'scroll'
                            },
                            id='app3_iso_table'
                        ),
                    ],
                    id='app3_iso_input',
                    style={'display': 'none'},
                ),
                html.Button('Submit', id='app3_button_submit'),
            ]
        ),
        # Transmission at CG-1D or error messages
        html.Div(id='app3_result'),
    ]
)


@app.callback(
    Output('app3_sample_table', 'columns'),
    [
        Input('app3_compos_input_type', 'value'),
    ])
def update_input_columns(compos_type):
    if compos_type == weight_name:
        compos_drop = atomic_name
    else:
        compos_drop = weight_name
    compos_header_df_new = compos_header_df[compos_header_df.name != compos_drop]
    return compos_header_df_new.to_dict('records')


@app.callback(
    Output('app3_sample_table', 'data'),
    [
        Input('app3_add_row', 'n_clicks')
    ],
    [
        State('app3_sample_table', 'data'),
        State('app3_sample_table', 'columns')
    ])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('app3_iso_table', 'data'),
    [
        Input('app3_sample_table', 'data'),
    ])
def update_iso_table(compos_tb_row):
    compos_tb_df = pd.DataFrame(compos_tb_row)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    iso_df = form_iso_table(sample_df=sample_df)
    return iso_df.to_dict('records')


@app.callback(
    Output('app3_iso_input', 'style'),
    [
        Input('app3_iso_check', 'values'),
    ])
def show_hide_iso_table(iso_changed):
    if iso_changed:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('app3_result', 'children'),
    [
        Input('app3_button_submit', 'n_clicks'),
    ],
    [
        State('app3_sample_table', 'data'),
        State('app3_iso_table', 'data'),
        State('app3_iso_check', 'values'),
        State('app3_compos_input_type', 'value'),
    ])
def output(n_clicks, compos_tb_rows, iso_tb_rows, iso_changed, compos_type):
    if n_clicks is not None:
        # Modify input for testing
        compos_tb_dict = force_dict_to_numeric(input_dict_list=compos_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        compos_tb_df = pd.DataFrame(compos_tb_dict)
        iso_tb_df = pd.DataFrame(iso_tb_dict)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=compos_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=compos_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation start
        if all(test_passed_list):
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
                             ),
                html.Div([html.H5('Sample stack:'), html.Div(div_list)])
            ]
        return output_div_list
    else:
        return None
