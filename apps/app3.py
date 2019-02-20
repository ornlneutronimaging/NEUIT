from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

df_sample = pd.DataFrame({
    chem_name: ['SiC', 'Si'],
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
                    columns=converter_tb_header,
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
    ])
def add_del_row(clicked, sample_tb_rows):
    last_clicked = clicked[-3:]
    _df_sample = add_del_tb_rows_converter(add_or_del=last_clicked, sample_tb_rows=sample_tb_rows)
    return _df_sample.to_dict('records')


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
    ])
def output(n_clicks, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_clicks is not None:
        total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows,
                                                                                          iso_tb_rows,
                                                                                          iso_changed)
        df_input = pd.DataFrame(sample_tb_rows)
        atomic_bool = all(np.array(df_input[atomic_name] != '')) is True
        weight_bool = all(np.array(df_input[weight_name] != '')) is True
        print(df_input)
        print(sample_tb_rows)
        if weight_bool:
            _name = weight_name
            fill_name = atomic_name
        else:
            _name = atomic_name
            fill_name = weight_name
        _list = []
        for _n, each_phase in enumerate(sample_tb_rows):
            _molar_mass = o_stack[each_phase[chem_name]]['molar_mass']['value']
            _num = float(each_phase[_name])
            if weight_bool:  # wt.% input (g)
                _result = _num / _molar_mass
            else:  # at.% input (mol)
                _result = _num * _molar_mass
            _list.append(_result)
        _array = np.array(_list)
        _output_array = _array * 100 / sum(_array)
        df_input[fill_name] = np.round(_output_array, 3)
        print(df_input)

        print(atomic_bool, weight_bool)
        return html.Div(
            [
                html.Hr(),
                html.H3('Result'),
                html.H5('Transmission:'),
                html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(round(total_trans, 3))),
                html.H5('Attenuation:'),
                html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(round(100 - total_trans, 3))),
                html.Div([html.H5('Sample stack:'), html.Div(div_list)])
            ]
        )
