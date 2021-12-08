from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc
from dash import dash_table as dt
import pandas as pd

from app import app
from callbacks.utilities.initialization import init_app_ids
import callbacks.utilities.constants as constants
from callbacks.utilities.validator import validate_sample_input, validate_iso_input
from callbacks.utilities.all_apps import (update_iso_table_callback, force_dict_to_numeric, form_iso_table,
                                          create_sample_df_from_compos_df, form_transmission_result_div,
                                          form_sample_stack_table_div, update_rows_util,
                                          iso_dict_schema)
from callbacks.utilities.converter import (compos_header_percent_df, convert_input_to_composition,
                                           convert_to_effective_formula, compos_dict_schema)

app_name = 'converter'
app_id_dict = init_app_ids(app_name=app_name)


@app.callback(
    Output(app_id_dict['app_info_id'], 'style'),
    [
        Input(app_id_dict['more_about_app_id'], 'value'),
    ],
    [
        State(app_id_dict['app_info_id'], 'style'),
    ])
def show_hide_band_input(more_info, style):
    if more_info != ['more']:
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style


@app.callback(
    Output(app_id_dict['sample_table_id'], 'columns'),
    [
        Input(app_id_dict['compos_type_id'], 'value'),
    ],
    [
        State(app_id_dict['sample_table_id'], 'columns'),
    ])
def update_input_columns(compos_type, columns):
    if compos_type == constants.weight_name:
        columns[1]['name'] = constants.weight_name
    else:
        columns[1]['name'] = constants.atomic_name
    return columns


@app.callback(
    [
        Output(app_id_dict['sample_table_id'], 'data'),
        Output(app_id_dict['error_upload_id'], 'children'),
        Output(app_id_dict['hidden_upload_time_id'], 'children'),
    ],
    [
        Input(app_id_dict['add_row_id'], 'n_clicks_timestamp'),
        Input(app_id_dict['del_row_id'], 'n_clicks_timestamp'),
        Input(app_id_dict['sample_upload_id'], 'contents'),
        Input(app_id_dict['sample_upload_id'], 'last_modified'),
    ],
    [
        State(app_id_dict['hidden_upload_time_id'], 'children'),
        State(app_id_dict['sample_upload_id'], 'filename'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['sample_table_id'], 'columns')
    ])
def update_rows(n_add, n_del, list_of_contents, upload_time, prev_upload_time, list_of_names, rows, columns):
    rows, error_message, upload_t = update_rows_util(n_add=n_add,
                                                     n_del=n_del,
                                                     list_of_contents=list_of_contents,
                                                     upload_time=upload_time,
                                                     prev_upload_time=prev_upload_time,
                                                     list_of_names=list_of_names,
                                                     rows=rows,
                                                     columns=columns)
    return rows, error_message, upload_t


@app.callback(
    Output(app_id_dict['iso_table_id'], 'data'),
    [
        Input(app_id_dict['database_id'], 'value'),
        Input(app_id_dict['sample_table_id'], 'data'),
    ],
    [
        State(app_id_dict['iso_table_id'], 'data'),
    ])
def update_iso_table(database, sample_tb_rows, prev_iso_tb_rows):
    return_dict = update_iso_table_callback(sample_tb_rows=sample_tb_rows,
                                            prev_iso_tb_rows=prev_iso_tb_rows,
                                            database=database)
    return return_dict


@app.callback(
    Output(app_id_dict['iso_div_id'], 'style'),
    [
        Input(app_id_dict['iso_check_id'], 'value'),
    ],
    [
        State(app_id_dict['iso_div_id'], 'style'),
    ])
def show_hide_iso_table(iso_changed, style):
    if len(iso_changed) == 1:
        style['display'] = 'block'
    else:
        style['display'] = 'none'
    return style


@app.callback(
    Output(app_id_dict['output_id'], 'style'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
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
    Output(app_id_dict['error_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
    ],
    [
        State(app_id_dict['database_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
    ])
def error(n_submit, database, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_submit is not None:
        # Convert all number str to numeric and keep rest invalid input
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)

        # Test sample input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  sample_schema=compos_dict_schema,
                                                                  database=database)  # different schema)

        # Test iso input format and sum
        if all(test_passed_list):
            if len(iso_changed) == 1:
                iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
                iso_tb_df = pd.DataFrame(iso_tb_dict)
            else:
                iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)

            test_passed_list, output_div_list = validate_iso_input(iso_df=iso_tb_df,
                                                                   iso_schema=iso_dict_schema,
                                                                   test_passed_list=test_passed_list,
                                                                   output_div_list=output_div_list,
                                                                   database=database)

        # Return result
        if all(test_passed_list):
            return True
        else:
            return output_div_list
    else:
        return None


@app.callback(
    Output(app_id_dict['result_id'], 'children'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
    ],
    [
        State(app_id_dict['database_id'], 'value'),
        State(app_id_dict['sample_table_id'], 'data'),
        State(app_id_dict['iso_table_id'], 'data'),
        State(app_id_dict['iso_check_id'], 'value'),
        State(app_id_dict['compos_type_id'], 'value'),
    ])
def output(n_submit, test_passed, database, compos_tb_rows, iso_tb_rows, iso_changed, compos_type):
    if test_passed is True:
        # Modify input for testing
        compos_tb_dict = force_dict_to_numeric(input_dict_list=compos_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        compos_tb_df = pd.DataFrame(compos_tb_dict)
        if len(iso_changed) == 1:
            iso_tb_df = pd.DataFrame(iso_tb_dict)
        else:
            iso_tb_df = form_iso_table(sample_df=compos_tb_df, database=database)

        # Calculation start

        # Remove rows contains no chemical input
        _compos_df = compos_tb_df[:]
        _compos_df = _compos_df[_compos_df[_compos_df.columns[0]] != '']

        _sample_df = create_sample_df_from_compos_df(compos_tb_df=_compos_df)
        _iso_tb_df = iso_tb_df[:]

        # Calculation starts
        transmission_div_list, o_stack = form_transmission_result_div(sample_tb_rows=_sample_df.to_dict('records'),
                                                                      iso_tb_rows=_iso_tb_df.to_dict('records'),
                                                                      iso_changed=iso_changed,
                                                                      beamline='imaging_crop',
                                                                      band_min=None,
                                                                      band_max=None,
                                                                      band_type='energy',
                                                                      database=database)
        sample_stack_div_list = form_sample_stack_table_div(o_stack=o_stack, full_stack=False)

        compos_output_df, ele_list, mol_list = convert_input_to_composition(compos_df=_compos_df,
                                                                            compos_type=compos_type,
                                                                            o_stack=o_stack)

        effective_formula = convert_to_effective_formula(ele_list=ele_list, mol_list=mol_list)

        output_div_list = [
            html.Hr(),
            html.H3('Result'),
            html.P('Effective chemical formula: {}'.format(effective_formula)),
            dcc.Markdown('''Above '**effective chemical formula**' can be used as '**Chemical formula**' 
            in other apps)'''),
            dt.DataTable(data=compos_output_df.to_dict('records'),
                         columns=compos_header_percent_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filter_action='none',
                         sort_action='none',
                         row_deletable=False,
                         style_cell_conditional=[
                             {'if': {'column_id': constants.chem_name},
                              'width': '33%'},
                             {'if': {'column_id': constants.weight_name_p},
                              'width': '33%'},
                             {'if': {'column_id': constants.atomic_name_p},
                              'width': '33%'},
                         ],
                         ),
            html.Div(sample_stack_div_list)
        ]
        return output_div_list
    else:
        return None
