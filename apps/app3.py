from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

df_sample = pd.DataFrame({
    chem_name: ['B4C', 'SiC'],
    weight_name: ['50', '50'],
    # atomic_name: ['', ''],
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
                dcc.RadioItems(id='composition_input_type',
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
                html.Div(
                    [
                        html.Button('+', id='app3_button_add', n_clicks=0),
                        html.Button('-', id='app3_button_del', n_clicks=0),
                        # html.Button('+', id='app3_button_add', n_clicks_timestamp=0),
                        # html.Button('-', id='app3_button_del', n_clicks_timestamp=0),
                    ], className='row'
                ),

                dt.DataTable(
                    rows=df_sample.to_dict('records'),
                    # optional - sets the order of columns
                    columns=[chem_name, weight_name],
                    # columns=converter_tb_header.remove(atomic_name),
                    editable=True,
                    row_selectable=False,
                    filterable=False,
                    sortable=False,
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
                        dt.DataTable(rows=iso_tb_df_default.to_dict('records'),
                                     columns=iso_table_header,
                                     editable=True,
                                     # editable={layer_name: False,
                                     #           ele_name: False,
                                     #           iso_name: True,
                                     #           },
                                     # row_selectable=True,
                                     filterable=True,
                                     sortable=True,
                                     id='app3_iso_table'),
                    ],
                    id='app3_iso_input',
                    style={'visibility': 'hidden'},
                    # style={'display': 'none'},
                ),
                html.Button('Submit', id='app3_button_submit'),
            ]
        ),
        # # Transmission at CG-1D
        # html.Div(id='app3_error'),
        # Transmission at CG-1D
        html.Div(id='app3_result'),
        # Hidden Div to handle button action
        html.Div([
            html.Div(id='app3_clicked_button', children='del:0 add:0 tog:0 last:nan', style={'display': 'none'})
        ]),
        html.Div(id='app3_display_clicked', children=""),
    ]
)


@app.callback(
    Output('app3_clicked_button', 'children'),
    [
        Input('app3_button_add', 'n_clicks'),
        Input('app3_button_del', 'n_clicks'),
    ],
    [
        State('app3_clicked_button', 'children')
    ])
def updated_clicked(add_clicks, del_clicks, prev_clicks):
    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'
    if del_clicks > int(prev_clicks['del']):
        last_clicked = 'del'
    elif add_clicks > int(prev_clicks['add']):
        last_clicked = 'add'
    cur_clicks = 'add:{} del:{} last:{}'.format(add_clicks, del_clicks, last_clicked)
    print(cur_clicks)
    return cur_clicks


@app.callback(
    Output('app3_sample_table', 'rows'),
    [
        Input('app3_clicked_button', 'children'),
    ],
    [
        State('app3_sample_table', 'rows'),
        State('composition_input_type', 'value'),
        State('app3_sample_table', 'columns'),
    ])
def add_del_row(clicked, sample_tb_rows, input_type, converter_tb_header_new):
    last_clicked = clicked[-3:]
    _df_sample = add_del_tb_rows_converter(add_or_del=last_clicked,
                                           sample_tb_rows=sample_tb_rows,
                                           input_type=input_type,
                                           header=converter_tb_header_new)
    return _df_sample.to_dict('records')


@app.callback(
    Output('app3_sample_table', 'columns'),
    [
        Input('composition_input_type', 'value'),
    ])
def update_input_columns(input_type):
    converter_tb_header_new = converter_tb_header[:]
    if input_type == weight_name:
        converter_tb_header_new.remove(atomic_name)
    else:
        converter_tb_header_new.remove(weight_name)
    return converter_tb_header_new


@app.callback(
    Output('app3_iso_table', 'rows'),
    [
        Input('app3_sample_table', 'rows'),
    ])
def update_iso_table(sample_tb_rows):
    _df = form_iso_table(sample_tb_rows)
    return _df.to_dict('records')


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
        State('app3_sample_table', 'rows'),
        State('app3_iso_table', 'rows'),
        State('app3_iso_check', 'values'),
        State('composition_input_type', 'value'),
    ])
def output(n_clicks, sample_tb_rows, iso_tb_rows, iso_changed, compos_type):
    if n_clicks is not None:
        # Test input
        df_sample_tb, df_iso_tb, test_passed_list, output_div_list = validate_composition_input(
            sample_tb_rows=sample_tb_rows,
            iso_tb_rows=iso_tb_rows,
            compos_type=compos_type)

        # Calculation starts
        if all(test_passed_list):
            total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(df_sample_tb=df_sample_tb,
                                                                                              df_iso_tb=df_iso_tb,
                                                                                              iso_changed=iso_changed)
            df_input, ele_list, mol_list = convert_input_to_composition(df_input=df_sample_tb,
                                                                        compos_type=compos_type,
                                                                        o_stack=o_stack)

            effective_formula = convert_to_effective_formula(ele_list=ele_list, mol_list=mol_list)

            output_div_list = [
                html.Hr(),
                html.H3('Result'),
                html.P('The effective chemical formula after conversion: {}'.format(effective_formula)),
                html.P("(This can be passed as 'Chemical formula' for other apps)"),
                dt.DataTable(rows=df_input.to_dict('records'),
                             columns=converter_tb_header_p,
                             editable=False,
                             row_selectable=False,
                             filterable=False,
                             sortable=False,
                             # id='sample_table'
                             ),
                html.Div([html.H5('Sample stack:'), html.Div(div_list)])
            ]
            return output_div_list
        else:
            return output_div_list
    else:
        return empty_div
