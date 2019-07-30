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
error_id = app_name + '_error'
output_id = app_name + '_output'
beamline_id = app_name + '_beamline'
band_div_id = app_name + '_band_div'
band_min_id = app_name + '_band_min'
band_max_id = app_name + '_band_max'
band_type_id = app_name + '_band_type'
band_unit_id = app_name + '_band_unit'

# Create app layout
layout = html.Div(
    [
        html.A('Home', href='/', target="_blank"),
        html.Br(),
        html.A(app_dict['app2']['name'], href=app_dict['app2']['url'], target="_blank"),
        html.Br(),
        html.A(app_dict['app3']['name'], href=app_dict['app3']['url'], target="_blank"),
        html.H1(app_dict['app1']['name']),

        # Beamline selection
        html.Div(
            [
                html.Div(
                    [
                        html.H3('Beamline'),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=beamline_id,
                                    options=[
                                        {'label': 'IMAGING (CG-1D), HFIR', 'value': 'imaging'},
                                        {'label': 'SNAP (BL-3), SNS', 'value': 'snap'},
                                        # {'label': 'SNS, VENUS (BL-10)', 'value': 'venus'},
                                    ],
                                    value='imaging',
                                    searchable=False,
                                    clearable=False,
                                ),
                            ]
                        ),
                    ], className='five columns', style={'verticalAlign': 'middle'},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3('Band width',
                                        className='four columns'
                                        ),
                                dcc.RadioItems(id=band_type_id,
                                               options=[
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                               ],
                                               value='lambda',
                                               className='four columns',
                                               labelStyle={'display': 'inline-block'},
                                               ),
                            ], className='row'
                        ),
                        html.Div(
                            [
                                dcc.Input(id=band_min_id, type='number',
                                          inputMode='numeric',
                                          placeholder='Min.',
                                          step=0.01,
                                          className='four columns',
                                          ),
                                dcc.Input(id=band_max_id, type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.01,
                                          className='four columns',
                                          ),
                                html.P('\u212B',
                                       id=band_unit_id,
                                       style={'marginBottom': 10, 'marginTop': 5},
                                       className='one column',
                                       ),
                            ], className='row', style={'verticalAlign': 'middle'},
                        ),
                    ], className=col_width_6, style={'display': 'none'}, id=band_div_id,
                ),
            ], className='row',
        ),
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
                    filter_action='none',
                    sort_action='none',
                    row_deletable=True,
                    style_cell_conditional=even_3_col,
                    style_data_conditional=[striped_rows],
                    id=sample_table_id
                ),
                markdown_sample,
                label_sample,

                # Input table for isotopic ratios
                dcc.Checklist(id=iso_check_id,
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': 'yes'},
                              ], value=[],
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
                # Transmission at CG-1D and stack info
                html.Div(id=result_id),
            ],
            id=output_id,
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    Output(band_div_id, 'style'),
    [
        Input(beamline_id, 'value'),
    ],
    [
        State(band_div_id, 'style'),
    ])
def show_hide_band_input(beamline, style):
    if beamline == 'imaging':
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style


@app.callback(
    Output(band_unit_id, 'children'),
    [
        Input(band_type_id, 'value'),
    ])
def show_band_units(band_type):
    if band_type == 'lambda':
        return '\u212B'
    else:
        return 'eV'


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
def update_iso_table(sample_tb_rows, prev_iso_tb_rows):
    compos_tb_df = pd.DataFrame(sample_tb_rows)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_rows)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    try:
        new_iso_df = form_iso_table(sample_df=sample_df)
        new_iso_df = update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
        return new_iso_df.to_dict('records')
    except ValueError:
        return None


@app.callback(
    Output(iso_div_id, 'style'),
    [
        Input(iso_check_id, 'value'),
    ],
    [
        State(iso_div_id, 'style'),
    ])
def show_hide_iso_table(iso_changed, style):
    if len(iso_changed) == 1:
        style['display'] = 'block'
    else:
        style['display'] = 'none'
    return style


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
        State(iso_check_id, 'value'),
        State(beamline_id, 'value'),
        State(band_min_id, 'value'),
        State(band_max_id, 'value'),
        State(band_type_id, 'value'),
    ])
def error(n_submit, sample_tb_rows, iso_tb_rows, iso_changed, beamline, band_min, band_max, band_type):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        # Test sample input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  sample_schema=sample_dict_schema)

        # Test density required or not
        if all(test_passed_list):
            test_passed_list, output_div_list = validate_density_input(sample_tb_df=sample_tb_df,
                                                                       test_passed_list=test_passed_list,
                                                                       output_div_list=output_div_list)

        # Test iso input format and sum
        if all(test_passed_list):
            if len(iso_changed) == 1:
                iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
                iso_tb_df = pd.DataFrame(iso_tb_dict)
            else:
                iso_tb_df = form_iso_table(sample_df=sample_tb_df)

            test_passed_list, output_div_list = validate_iso_input(iso_df=iso_tb_df,
                                                                   iso_schema=iso_dict_schema,
                                                                   test_passed_list=test_passed_list,
                                                                   output_div_list=output_div_list)
        # Test band width input
        if all(test_passed_list):
            test_passed_list, output_div_list = validate_band_width_input(beamline=beamline,
                                                                          band_width=(band_min, band_max),
                                                                          band_type=band_type,
                                                                          test_passed_list=test_passed_list,
                                                                          output_div_list=output_div_list)

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
        State(iso_check_id, 'value'),
        State(beamline_id, 'value'),
        State(band_min_id, 'value'),
        State(band_max_id, 'value'),
        State(band_type_id, 'value'),
    ])
def output_transmission_and_stack(n_submit, test_passed, sample_tb_rows, iso_tb_rows, iso_changed,
                                  beamline, band_min, band_max, band_type):
    if test_passed is True:
        output_div_list, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                iso_tb_rows=iso_tb_rows,
                                                                iso_changed=iso_changed,
                                                                beamline=beamline,
                                                                band_min=band_min,
                                                                band_max=band_max,
                                                                band_type=band_type)
        if beamline != 'imaging':  # add CG-1D anyway if not selected
            trans_div_list_tof, o_stack = form_transmission_result_div(sample_tb_rows=sample_tb_rows,
                                                                       iso_tb_rows=iso_tb_rows,
                                                                       iso_changed=iso_changed,
                                                                       beamline='imaging',
                                                                       band_min=band_min,
                                                                       band_max=band_max,
                                                                       band_type=band_type)
            output_div_list.extend(trans_div_list_tof)

        # Sample stack table div
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack)
        output_div_list.extend(sample_stack_div_list)

        return output_div_list
    else:
        return None
