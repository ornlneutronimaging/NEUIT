from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
tof_name = 'Time-of-flight (\u03BCs)'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ele_name = 'Element'

df_sample = pd.DataFrame({
    chem_name: ['H2O'],
    thick_name: ['2'],
    density_name: ['1'],
})

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.H1('Cold neutron transmission'),
        html.H3('Sample info'),

        # Sample input
        html.Div(
            [
                html.Div(
                    [
                        html.Button('+', id='app1_button_add', n_clicks=0),
                        html.Button('-', id='app1_button_del', n_clicks=0),
                        # html.Button('+', id='app1_button_add', n_clicks_timestamp=0),
                        # html.Button('-', id='app1_button_del', n_clicks_timestamp=0),
                    ], className='row'
                ),

                dt.DataTable(
                    rows=df_sample.to_dict('records'),
                    # optional - sets the order of columns
                    columns=sample_tb_header,
                    editable=True,
                    row_selectable=False,
                    filterable=False,
                    sortable=False,
                    id='app1_sample_table'
                ),
                dcc.Markdown(
                    '''NOTE: density input can be omitted (leave as blank) 
                    only if the input formula is single element, density available
                    [here](http://periodictable.com/Properties/A/Density.al.html) will be used.'''),
                # Input table for isotopic ratios
                dcc.Checklist(id='app1_iso_check',
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': True},
                              ], values=[],
                              ),
                html.Div(
                    [
                        dcc.Markdown("""NOTE: Please edit **ONLY** the 'Isotopic ratio' column.
                        Editing of 'Sample info' will **RESET** contents in isotope table."""),
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
                                     id='app1_iso_table'),
                    ],
                    id='app1_iso_input',
                    style={'visibility': 'hidden'},
                    # style={'display': 'none'},
                ),
                html.Button('Submit', id='app1_button_submit'),
            ]
        ),

        # Transmission at CG-1D
        html.Div(id='app1_result'),
        # Hidden Div to handle button action
        html.Div([
            html.Div(id='app1_clicked_button', children='del:0 add:0 tog:0 last:nan', style={'display': 'none'})
        ]),
        html.Div(id='app1_display_clicked', children=""),
    ]
)


@app.callback(
    Output('app1_clicked_button', 'children'),
    [
        Input('app1_button_add', 'n_clicks'),
        Input('app1_button_del', 'n_clicks')
    ],
    [
        State('app1_clicked_button', 'children')
    ])
def updated_clicked(add_clicks, del_clicks, prev_clicks):
    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'
    if del_clicks > int(prev_clicks['del']):
        last_clicked = 'del'
    elif add_clicks > int(prev_clicks['add']):
        last_clicked = 'add'
    cur_clicks = 'del:{} add:{} last:{}'.format(del_clicks, add_clicks, last_clicked)
    return cur_clicks


@app.callback(
    Output('app1_sample_table', 'rows'),
    [
        Input('app1_clicked_button', 'children'),
    ],
    [
        State('app1_sample_table', 'rows'),
    ])
def add_del_row(clicked, sample_tb_rows):
    last_clicked = clicked[-3:]
    _df_sample = add_del_tb_rows(add_or_del=last_clicked, sample_tb_rows=sample_tb_rows)
    return _df_sample.to_dict('records')


@app.callback(
    Output('app1_iso_table', 'rows'),
    [
        Input('app1_sample_table', 'rows'),
    ])
def update_iso_table(sample_tb_rows):
    _df = form_iso_table(sample_tb_rows)
    return _df.to_dict('records')


@app.callback(
    Output('app1_iso_input', 'style'),
    [
        Input('app1_iso_check', 'values'),
    ])
def show_hide_iso_table(iso_changed):
    if iso_changed:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('app1_result', 'children'),
    [
        Input('app1_button_submit', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
        State('app1_iso_table', 'rows'),
        State('app1_iso_check', 'values'),
    ])
def output(n_clicks, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_clicks is not None:
        total_trans, div_list = calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows,
                                                                                 iso_tb_rows,
                                                                                 iso_changed)
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
