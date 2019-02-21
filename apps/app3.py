from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

df_sample = pd.DataFrame({
    chem_name: ['B4C', 'SiC'],
    weight_name: ['50', '50'],
    atomic_name: ['', ''],
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
        Input('app3_button_del', 'n_clicks')
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
        # State('app3_sample_table', 'rows'),
    ],
)
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
def output(n_clicks, sample_tb_rows, iso_tb_rows, iso_changed, input_type):
    if n_clicks is not None:
        total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows,
                                                                                          iso_tb_rows,
                                                                                          iso_changed)
        df_input = pd.DataFrame(sample_tb_rows)
        df_input = df_input[df_input[chem_name] != '']
        df_input[input_type] = pd.to_numeric(df_input[input_type])  # , errors='ignore')
        if input_type == weight_name:
            fill_name = atomic_name_p
            update_name = weight_name_p
        else:
            fill_name = weight_name_p
            update_name = atomic_name_p
            df_input.drop(columns=[weight_name], inplace=True)
        _list = []
        _ele_list = []
        _ratio_list = []
        _input_p_list = []
        _input_sum = df_input[input_type].sum()
        for _n, each_chem in enumerate(df_input[chem_name]):
            _molar_mass = o_stack[each_chem]['molar_mass']['value']
            input_num = df_input[input_type][_n]
            _current_ele_list = o_stack[each_chem]['elements']
            _current_ratio_list = o_stack[each_chem]['stoichiometric_ratio']
            _input_percentage = input_num * 100 / _input_sum
            if input_type == weight_name:  # wt.% input (g)
                _result = input_num / _molar_mass
            else:  # at.% input (mol)
                _result = input_num * _molar_mass
            _list.append(_result)
            _input_p_list.append(_input_percentage)
            _ele_list += _current_ele_list
            _ratio_list += _current_ratio_list
        print(_ele_list)
        print(_ratio_list)
        print(_list)
        _array = np.array(_list)
        _input_p_array = np.array(_input_p_list)
        _output_array = _array * 100 / sum(_array)
        df_input[fill_name] = np.round(_output_array, 3)
        df_input[update_name] = np.round(_input_p_array, 3)
        print(df_input)

        return html.Div(
            [
                html.Hr(),
                html.H3('Result'),
                html.P('The effective chemical formula after conversion: {}'.format('aa')),
                dt.DataTable(rows=df_input.to_dict('records'),
                             columns=converter_tb_header_p,
                             editable=False,
                             row_selectable=False,
                             filterable=False,
                             sortable=False,
                             # id='sample_table'
                             ),
                # html.H5('Transmission:'),
                # html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(round(total_trans, 3))),
                # html.H5('Attenuation:'),
                # html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(round(100 - total_trans, 3))),
                html.Div([html.H5('Sample stack:'), html.Div(div_list)])
            ]
        )
