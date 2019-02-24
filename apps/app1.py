from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *

sample_df_default = pd.DataFrame({
    'column_1': ['H2O'],
    'column_2': ['2'],
    'column_3': ['1'],
})

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.Br(),
        dcc.Link('Composition converter', href='/apps/converter'),
        html.H1('Cold neutron transmission'),
        html.H3('Sample info'),

        # Sample input
        html.Div(
            [
                html.Button('Add Row', id='app1_add_row', n_clicks=0),
                dt.DataTable(
                    data=sample_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=sample_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filtering=False,
                    sorting=False,
                    row_deletable=True,
                    id='app1_sample_table'
                ),
                markdown_sample,

                # Input table for isotopic ratios
                dcc.Checklist(id='app1_iso_check',
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
                            id='app1_iso_table'
                        ),
                    ],
                    id='app1_iso_input',
                    style={'display': 'none'},
                ),
                html.Button('Submit', id='app1_button_submit'),
            ]
        ),

        # Transmission at CG-1D
        html.Div(id='app1_result'),
    ]
)


@app.callback(
    Output('app1_sample_table', 'data'),
    [Input('app1_add_row', 'n_clicks')],
    [State('app1_sample_table', 'data'),
     State('app1_sample_table', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('app1_iso_table', 'data'),
    [
        Input('app1_sample_table', 'data'),
    ])
def update_iso_table(compos_tb_dict):
    compos_tb_df = pd.DataFrame(compos_tb_dict)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    iso_df = form_iso_table(sample_df=sample_df)
    return iso_df.to_dict('records')


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
        State('app1_sample_table', 'data'),
        State('app1_iso_table', 'data'),
        State('app1_iso_check', 'values'),
    ])
def output(n_clicks, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_clicks is not None:
        # Test input
        sample_tb_df = pd.DataFrame(sample_tb_rows)
        iso_tb_df = pd.DataFrame(iso_tb_rows)
        sample_tb_df, iso_tb_df, test_passed_list, output_div_list = validate_sample_input(sample_tb_df=sample_tb_df,
                                                                                           iso_tb_df=iso_tb_df)
        # Calculation starts
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
            return output_div_list
    else:
        return None
