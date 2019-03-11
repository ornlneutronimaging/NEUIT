from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

sample_df_default = pd.DataFrame({
    'column_1': ['H2O'],
    'column_2': [2],
    'column_3': [1],
})

app_name = 'app1'
add_row_id = app_name + '_add_row'
del_row_id = app_name + '_del_row'
sample_table_id = app_name + '_sample_table'
iso_check_id = app_name + '_iso_check'
iso_div_id = app_name + '_iso_input'
iso_table_id = app_name + '_iso_table'
submit_button_id = app_name + '_submit'
result_id = app_name + '_result'

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.Br(),
        dcc.Link('Composition converter', href='/apps/converter'),
        html.H1('Cold neutron transmission'),

        # Sample input
        html.H3('Sample info'),
        html.Div(
            [
                html.Button('+', id=add_row_id, n_clicks_timestamp=0),
                html.Button('-', id=del_row_id, n_clicks_timestamp=0),
                dt.DataTable(
                    data=sample_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=sample_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filtering=False,
                    sorting=False,
                    row_deletable=True,
                    style_cell_conditional=even_3_col,
                    id=sample_table_id
                ),
                markdown_sample,
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

        # Transmission at CG-1D
        html.Div(id=result_id),
    ]
)


@app.callback(
    Output(sample_table_id, 'data'),
    [
        Input(add_row_id, 'n_clicks_timestamp'),
        Input(del_row_id, 'n_clicks_timestamp')
    ],
    [
        State(sample_table_id, 'data'),
        State(sample_table_id, 'columns')
    ])
def update_rows(n_add, n_del, rows, columns):
    if n_add > n_del:
        rows.append({c['id']: '' for c in columns})
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
    Output(result_id, 'children'),
    [
        Input(submit_button_id, 'n_clicks'),
    ],
    [
        State(sample_table_id, 'data'),
        State(iso_table_id, 'data'),
        State(iso_check_id, 'values'),
    ])
def output(n_submit, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_submit is not None:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        if iso_changed:
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=sample_tb_df)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=sample_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation start
        if all(test_passed_list):
            total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(sample_tb_df=sample_tb_df,
                                                                                              iso_tb_df=iso_tb_df,
                                                                                              iso_changed=iso_changed)
            output_div_list = [
                html.Hr(),
                html.H3('Result'),
                html.H5('Transmission:'),
                html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(round(total_trans, 3))),
                html.H5('Attenuation:'),
                html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(round(100 - total_trans, 3))),
                html.Div([html.H5('Sample stack:'), html.Div(div_list)]),
            ]
        return output_div_list
    else:
        return None
