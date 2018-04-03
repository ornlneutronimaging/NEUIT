import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from dash.dependencies import Input, Output, State

from _app import app
from _utilities import add_del_tb_rows, form_iso_table, calculate_transmission_cg1d_and_form_stack_table, \
    iso_table_header

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

col_3 = 'three columns'
col_6 = 'six columns'

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
                        html.Button('+', id='app1_button_add'),
                        html.Button('-', id='app1_button_del'),
                    ], className='row'
                ),

                dt.DataTable(
                    rows=df_sample.to_dict('records'),
                    # optional - sets the order of columns
                    columns=[chem_name, thick_name, density_name],
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
                html.Div(id='app1_iso_input'),
                dcc.Checklist(id='app1_iso_check',
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': True},
                              ], values=[],
                              ),
                html.Button('Submit', id='app1_button_submit'),
            ]
        ),

        # Transmission at CG-1D
        html.Div(id='app1_result'),
    ]
)


@app.callback(
    Output('app1_sample_table', 'rows'),
    [
        Input('app1_button_add', 'n_clicks'),
        Input('app1_button_del', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
    ])
def add_del_row(n_add, n_del, sample_tb_rows):
    _df_sample = add_del_tb_rows(n_add, n_del, sample_tb_rows)
    return _df_sample.to_dict('records')


@app.callback(
    Output('app1_iso_input', 'children'),
    [
        Input('app1_iso_check', 'values'),
        Input('app1_sample_table', 'rows'),
    ])
def show_iso_table(iso_check, sample_tb_rows):
    if not iso_check:
        return html.Div(dt.DataTable(rows=[{}], id='app1_iso_table'), style={'display': 'none'})
    else:
        _df = form_iso_table(sample_tb_rows)
        return dt.DataTable(rows=_df.to_dict('records'),
                            columns=iso_table_header,
                            editable=True,
                            # editable={layer_name: False,
                            #           ele_name: False,
                            #           iso_name: True,
                            #           },
                            # row_selectable=True,
                            filterable=True,
                            sortable=True,
                            id='app1_iso_table'
                            ),
        # dcc.Markdown("""NOTE: please only edit the 'Isotopic ratio' column.""")


@app.callback(
    Output('app1_result', 'children'),
    [
        Input('app1_button_submit', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
        State('app1_iso_table', 'rows'),
    ])
def output(n_clicks, sample_tb_rows, iso_tb_rows):
    if n_clicks is not None:
        total_trans, div_list = calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows, iso_tb_rows)
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
