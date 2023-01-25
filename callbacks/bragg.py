from dash.dependencies import Input, Output, State
from dash import dash_table as dt
from dash import dcc
from dash import html
import matplotlib.pyplot as plt
from bem import xscalc, matter
import pandas as pd
import numpy as np
import json
import time


import ImagingReso._utilities as ir_util
from app import app
from callbacks.utilities.initialization import (init_app_ids, striped_rows, plot_loading, resubmit)
import callbacks.utilities.constants as constants
from callbacks.utilities.plot import shape_matplot_to_plotly
from callbacks.utilities.all_apps import y_type_to_y_label, x_type_to_x_tag, load_dfs, update_rows_util
from callbacks.utilities.bragg import parse_cif_upload
from callbacks.utilities.resonance import fill_df_x_types
from callbacks.utilities.constants import *


app_name = 'bragg'
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


# tab 1
@app.callback(
        Output(app_id_dict['data_table_tab1'], 'data'),
    [
        Input(app_id_dict['add_row_tab1'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['data_table_tab1'], 'data'),
        State(app_id_dict['data_table_tab1'], 'columns'),
    ]
)
def update_rows(add_time, data, columns):
    data.append({c['id']: '' for c in columns})
    return data

# tab 2
@app.callback(
    [
        Output(app_id_dict['cif_upload_fb_tab2'], 'children'),
        Output(app_id_dict['no_error_tab2'], 'children'),
        Output(app_id_dict['data_table_tab2'], 'data'),
        Output(app_id_dict['hidden_upload_time_tab2'], 'children'),
        Output(app_id_dict['a_tab2'], 'value'),
        Output(app_id_dict['b_tab2'], 'value'),
        Output(app_id_dict['c_tab2'], 'value'),
        Output(app_id_dict['alpha_tab2'], 'value'),
        Output(app_id_dict['beta_tab2'], 'value'),
        Output(app_id_dict['gamma_tab2'], 'value')
    ],
    [
        Input(app_id_dict['cif_upload_tab2'], 'filename'),
        Input(app_id_dict['add_row_tab2'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['hidden_upload_time_tab2'], 'children'),
        State(app_id_dict['cif_upload_tab2'], 'contents'),
        State(app_id_dict['data_table_tab2'], 'data'),
        State(app_id_dict['data_table_tab2'], 'columns'),
    ],
)
def upload_feedback(cif_names, add_button_timestamp,
                    prev_upload_time, cif_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:

        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if cif_uploads is not None:

        if add_button_timestamp != prev_upload_time:

            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        # for each_index, each_content in enumerate(cif_uploads):
        #     _cif_struc = parse_cif_upload(content=each_content)
        _cif_struc = parse_cif_upload(content=cif_uploads)
        for _row_index, _row in enumerate(_cif_struc):

            if _row_index == 0:
                interaxial_angle_alpha = _row.lattice.alpha
                interaxial_angle_beta = _row.lattice.beta
                interaxial_angle_gamma = _row.lattice.gamma
                axial_length_a = _row.lattice.a
                axial_length_b = _row.lattice.b
                axial_length_c = _row.lattice.c

            chem_name = _row.element
            index_number_h = _row.x
            index_number_k = _row.y
            index_number_l = _row.z

            _new_table_entry = {constants.chem_name: chem_name,
                                constants.index_number_h: index_number_h,
                                constants.index_number_k: index_number_k,
                                constants.index_number_l: index_number_l}

            content_of_table.append(_new_table_entry)

    if '.cif' in cif_names:
        data_fb_list.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(cif_names)]))
    else:
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.cif' is ""supported.".format(cif_names)])
        error_div_list.append(error_div)

    if len(error_div_list) == 0:
        test_passed = True
    else:
        test_passed = error_div_list

    return data_fb_list, test_passed, \
           content_of_table, prev_upload_time, \
           axial_length_a, axial_length_b, \
           axial_length_c, interaxial_angle_alpha, \
           interaxial_angle_beta, interaxial_angle_gamma


# tab 3
@app.callback(
    [
        Output(app_id_dict['cif_upload_fb_tab3'], 'children'),
        Output(app_id_dict['no_error_tab3'], 'children'),
        Output(app_id_dict['data_table_tab3'], 'data'),
        Output(app_id_dict['hidden_upload_time_tab3'], 'children'),
        Output(app_id_dict['a_tab3'], 'value'),
        Output(app_id_dict['b_tab3'], 'value'),
        Output(app_id_dict['c_tab3'], 'value'),
        Output(app_id_dict['alpha_tab3'], 'value'),
        Output(app_id_dict['beta_tab3'], 'value'),
        Output(app_id_dict['gamma_tab3'], 'value')

    ],
    [
        Input(app_id_dict['cif_upload_tab3'], 'filename'),
        Input(app_id_dict['add_row_tab3'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['hidden_upload_time_tab3'], 'children'),
        State(app_id_dict['cif_upload_tab3'], 'contents'),
        State(app_id_dict['data_table_tab3'], 'data'),
        State(app_id_dict['data_table_tab3'], 'columns'),
    ],
)
def upload_feedback(cif_names, add_button_timestamp,
                    prev_upload_time, cif_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:

        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if cif_uploads is not None:

        if add_button_timestamp != prev_upload_time:

            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        # for each_index, each_content in enumerate(cif_uploads):
        #     _cif_struc = parse_cif_upload(content=each_content)
        _cif_struc = parse_cif_upload(content=cif_uploads)
        for _row_index, _row in enumerate(_cif_struc):

            if _row_index == 0:
                interaxial_angle_alpha = _row.lattice.alpha
                interaxial_angle_beta = _row.lattice.beta
                interaxial_angle_gamma = _row.lattice.gamma
                axial_length_a = _row.lattice.a
                axial_length_b = _row.lattice.b
                axial_length_c = _row.lattice.c

            chem_name = _row.element
            index_number_h = _row.x
            index_number_k = _row.y
            index_number_l = _row.z

            _new_table_entry = {constants.chem_name: chem_name,
                                constants.index_number_h: index_number_h,
                                constants.index_number_k: index_number_k,
                                constants.index_number_l: index_number_l}

            content_of_table.append(_new_table_entry)

    if '.cif' in cif_names:
        data_fb_list.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(cif_names)]))
    else:
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.cif' is ""supported.".format(cif_names)])
        error_div_list.append(error_div)

    if len(error_div_list) == 0:
        test_passed = True
    else:
        test_passed = error_div_list

    return data_fb_list, test_passed, \
           content_of_table, prev_upload_time, \
           axial_length_a, axial_length_b, \
           axial_length_c, interaxial_angle_alpha, \
           interaxial_angle_beta, interaxial_angle_gamma


# tab 4
@app.callback(
    [
        Output(app_id_dict['cif_upload_fb_tab4'], 'children'),
        Output(app_id_dict['no_error_tab4'], 'children'),
        Output(app_id_dict['data_table_tab4'], 'data'),
        Output(app_id_dict['hidden_upload_time_tab4'], 'children'),
        Output(app_id_dict['a_tab4'], 'value'),
        Output(app_id_dict['b_tab4'], 'value'),
        Output(app_id_dict['c_tab4'], 'value'),
        Output(app_id_dict['alpha_tab4'], 'value'),
        Output(app_id_dict['beta_tab4'], 'value'),
        Output(app_id_dict['gamma_tab4'], 'value')
    ],
    [
        Input(app_id_dict['cif_upload_tab4'], 'filename'),
        Input(app_id_dict['add_row_tab4'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['hidden_upload_time_tab4'], 'children'),
        State(app_id_dict['cif_upload_tab4'], 'contents'),
        State(app_id_dict['data_table_tab4'], 'data'),
        State(app_id_dict['data_table_tab4'], 'columns'),
    ],
)
def upload_feedback(cif_names, add_button_timestamp,
                    prev_upload_time, cif_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:

        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if cif_uploads is not None:

        if add_button_timestamp != prev_upload_time:

            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        # for each_index, each_content in enumerate(cif_uploads):
        #     _cif_struc = parse_cif_upload(content=each_content)
        _cif_struc = parse_cif_upload(content=cif_uploads)
        for _row_index, _row in enumerate(_cif_struc):

            if _row_index == 0:
                interaxial_angle_alpha = _row.lattice.alpha
                interaxial_angle_beta = _row.lattice.beta
                interaxial_angle_gamma = _row.lattice.gamma
                axial_length_a = _row.lattice.a
                axial_length_b = _row.lattice.b
                axial_length_c = _row.lattice.c

            chem_name = _row.element
            index_number_h = _row.x
            index_number_k = _row.y
            index_number_l = _row.z

            _new_table_entry = {constants.chem_name: chem_name,
                                constants.index_number_h: index_number_h,
                                constants.index_number_k: index_number_k,
                                constants.index_number_l: index_number_l}

            content_of_table.append(_new_table_entry)

    if '.cif' in cif_names:
        data_fb_list.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(cif_names)]))
    else:
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.cif' is ""supported.".format(cif_names)])
        error_div_list.append(error_div)

    if len(error_div_list) == 0:
        test_passed = True
    else:
        test_passed = error_div_list

    return data_fb_list, test_passed, \
           content_of_table, prev_upload_time, \
           axial_length_a, axial_length_b, \
           axial_length_c, interaxial_angle_alpha, \
           interaxial_angle_beta, interaxial_angle_gamma


# tab 5
@app.callback(
    [
        Output(app_id_dict['cif_upload_fb_tab5'], 'children'),
        Output(app_id_dict['no_error_tab5'], 'children'),
        Output(app_id_dict['data_table_tab5'], 'data'),
        Output(app_id_dict['hidden_upload_time_tab5'], 'children'),
        Output(app_id_dict['a_tab5'], 'value'),
        Output(app_id_dict['b_tab5'], 'value'),
        Output(app_id_dict['c_tab5'], 'value'),
        Output(app_id_dict['alpha_tab5'], 'value'),
        Output(app_id_dict['beta_tab5'], 'value'),
        Output(app_id_dict['gamma_tab5'], 'value')
    ],
    [
        Input(app_id_dict['cif_upload_tab5'], 'filename'),
        Input(app_id_dict['add_row_tab5'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['hidden_upload_time_tab5'], 'children'),
        State(app_id_dict['cif_upload_tab5'], 'contents'),
        State(app_id_dict['data_table_tab5'], 'data'),
        State(app_id_dict['data_table_tab5'], 'columns'),
    ],
)
def upload_feedback(cif_names, add_button_timestamp,
                    prev_upload_time, cif_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:

        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if cif_uploads is not None:

        if add_button_timestamp != prev_upload_time:

            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        # for each_index, each_content in enumerate(cif_uploads):
        #     _cif_struc = parse_cif_upload(content=each_content)
        _cif_struc = parse_cif_upload(content=cif_uploads)
        for _row_index, _row in enumerate(_cif_struc):

            if _row_index == 0:
                interaxial_angle_alpha = _row.lattice.alpha
                interaxial_angle_beta = _row.lattice.beta
                interaxial_angle_gamma = _row.lattice.gamma
                axial_length_a = _row.lattice.a
                axial_length_b = _row.lattice.b
                axial_length_c = _row.lattice.c

            chem_name = _row.element
            index_number_h = _row.x
            index_number_k = _row.y
            index_number_l = _row.z

            _new_table_entry = {constants.chem_name: chem_name,
                                constants.index_number_h: index_number_h,
                                constants.index_number_k: index_number_k,
                                constants.index_number_l: index_number_l}

            content_of_table.append(_new_table_entry)

    if '.cif' in cif_names:
        data_fb_list.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(cif_names)]))
    else:
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.cif' is ""supported.".format(cif_names)])
        error_div_list.append(error_div)

    if len(error_div_list) == 0:
        test_passed = True
    else:
        test_passed = error_div_list

    return data_fb_list, test_passed, \
           content_of_table, prev_upload_time, \
           axial_length_a, axial_length_b, \
           axial_length_c, interaxial_angle_alpha, \
           interaxial_angle_beta, interaxial_angle_gamma


def clean_data_tab(data_tab2=None):
    '''
    remove all the rows with no chemical formula defined
    '''
    data_tab2_cleaned = []
    for _entry in data_tab2:
        if _entry[chem_name] == '':
            continue
        else:
            data_tab2_cleaned.append(_entry)
    return data_tab2_cleaned


def update_xs_dict(xs_dict=None,
                   data_tab=None,
                   a=None, b=None, c=None,
                   alpha=None, beta=None, gamma=None,
                   temperature=None,
                   log_label='tab2',
                   wavelengths_A=None):
    '''
    calculating the structure for the given data_tab
    '''
    print(f"No errors found in {log_label}, working with {log_label}:")

    # data_tab
    atoms = []
    _name_only = log_label
    data_tab = clean_data_tab(data_tab)
    for entry in data_tab:

        # if no element, continue
        if not entry[chem_name]:
            continue
        _chem_name = entry[chem_name]

        _h = entry[index_number_h]
        _k = entry[index_number_k]
        _l = entry[index_number_l]

        atoms.append(matter.Atom(_chem_name, (_h, _k, _l)))

    print(f"- calculating lattice")
    _lattice = matter.Lattice(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)

    print(f"- calculating structure")
    _structure = matter.Structure(atoms, _lattice, sgid=225)

    print(f"- calculating cross-section")
    _xscalculator = xscalc.XSCalculator(_structure, temperature, max_diffraction_index=4)

    xs_dict[_name_only + ' (total)'] = _xscalculator.xs(wavelengths_A)
    xs_dict[_name_only + ' (abs)'] = _xscalculator.xs_abs(wavelengths_A)
    xs_dict[_name_only + ' (coh el)'] = _xscalculator.xs_coh_el(wavelengths_A)
    xs_dict[_name_only + ' (inc el)'] = _xscalculator.xs_inc_el(wavelengths_A)
    xs_dict[_name_only + ' (coh inel)'] = _xscalculator.xs_coh_inel(wavelengths_A)
    xs_dict[_name_only + ' (inc inel)'] = _xscalculator.xs_inc_inel(wavelengths_A)
    print("- Calculation done!")


# submit button clicked
@app.callback(
    [
        Output(app_id_dict['hidden_df_json_id'], 'children'),
        Output(app_id_dict['no_error_id'], 'children'),
        Output(app_id_dict['output_id'], 'style')
    ],
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
    ],
    [
        State(app_id_dict['data_table_tab1'], 'data'),
        State(app_id_dict['a_tab1'], 'value'),
        State(app_id_dict['b_tab1'], 'value'),
        State(app_id_dict['c_tab1'], 'value'),
        State(app_id_dict['alpha_tab1'], 'value'),
        State(app_id_dict['beta_tab1'], 'value'),
        State(app_id_dict['gamma_tab1'], 'value'),

        State(app_id_dict['data_table_tab2'], 'data'),
        State(app_id_dict['a_tab2'], 'value'),
        State(app_id_dict['b_tab2'], 'value'),
        State(app_id_dict['c_tab2'], 'value'),
        State(app_id_dict['alpha_tab2'], 'value'),
        State(app_id_dict['beta_tab2'], 'value'),
        State(app_id_dict['gamma_tab2'], 'value'),
        State(app_id_dict['no_error_tab2'], 'children'),

        State(app_id_dict['data_table_tab3'], 'data'),
        State(app_id_dict['a_tab3'], 'value'),
        State(app_id_dict['b_tab3'], 'value'),
        State(app_id_dict['c_tab3'], 'value'),
        State(app_id_dict['alpha_tab3'], 'value'),
        State(app_id_dict['beta_tab3'], 'value'),
        State(app_id_dict['gamma_tab3'], 'value'),

        State(app_id_dict['data_table_tab4'], 'data'),
        State(app_id_dict['a_tab4'], 'value'),
        State(app_id_dict['b_tab4'], 'value'),
        State(app_id_dict['c_tab4'], 'value'),
        State(app_id_dict['alpha_tab4'], 'value'),
        State(app_id_dict['beta_tab4'], 'value'),
        State(app_id_dict['gamma_tab4'], 'value'),

        State(app_id_dict['data_table_tab5'], 'data'),
        State(app_id_dict['a_tab5'], 'value'),
        State(app_id_dict['b_tab5'], 'value'),
        State(app_id_dict['c_tab5'], 'value'),
        State(app_id_dict['alpha_tab5'], 'value'),
        State(app_id_dict['beta_tab5'], 'value'),
        State(app_id_dict['gamma_tab5'], 'value'),

        State(app_id_dict['temperature_id'], 'value'),
        State(app_id_dict['distance_id'], 'value'),
        State(app_id_dict['delay_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_step_id'], 'value'),
    ]
)
def show_output_div(n_submit, data_tab1, a_tab1, b_tab1, c_tab1, alpha_tab1, beta_tab1, gamma_tab1,
                    data_tab2, a_tab2, b_tab2, c_tab2, alpha_tab2, beta_tab2, gamma_tab2, no_error_tab2,
                    data_tab3, a_tab3, b_tab3, c_tab3, alpha_tab3, beta_tab3, gamma_tab3,
                    data_tab4, a_tab4, b_tab4, c_tab4, alpha_tab4, beta_tab4, gamma_tab4,
                    data_tab5, a_tab5, b_tab5, c_tab5, alpha_tab5, beta_tab5, gamma_tab5,
                    temperature, distance, delay,
                    band_min, band_max, band_step):

    something_to_plot = False
    if n_submit is not None:

        wavelengths_A = np.arange(band_min, band_max, band_step)
        xs_dict = {}

        data_tab1 = clean_data_tab(data_tab1)
        data_tab2 = clean_data_tab(data_tab2)
        data_tab3 = clean_data_tab(data_tab3)
        data_tab4 = clean_data_tab(data_tab4)
        data_tab5 = clean_data_tab(data_tab5)
        if data_tab2 or data_tab3 or data_tab4 or data_tab5 or data_tab1:
           something_to_plot = True

            # print(f"tab2 is empty! Leaving show_output_div.")
            # return None,  False, {'display': 'none'}

        if no_error_tab2:
            update_xs_dict(xs_dict=xs_dict,
                           data_tab=data_tab2,
                           log_label='tab2',
                           a=a_tab2, b=b_tab2, c=c_tab2,
                           alpha=alpha_tab2, beta=beta_tab2, gamma=gamma_tab2,
                           temperature=temperature,
                           wavelengths_A=wavelengths_A)

        # work with other tabs




        if not something_to_plot:
            return None,  False, {'display': 'none'}

        df_y = pd.DataFrame.from_dict(xs_dict)
        df_x = pd.DataFrame()
        df_x[constants.energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
        df_x = fill_df_x_types(df=df_x, distance_m=distance, delay_us=delay)

        datasets = {
                    'x': df_x.to_json(orient='split', date_format='iso'),
                    'y': df_y.to_json(orient='split', date_format='iso'),
                    }
        return json.dumps(datasets), True, {'display': 'block'}

    else:
        return None,  False, {'display': 'none'}


# @app.callback(
#     Output(app_id_dict['output_id'], 'style'),
#     [
#         Input(app_id_dict['submit_button_id'], 'n_clicks'),
#     ],
#     [
#         State(app_id_dict['no_error_id'], 'children'),
#     ]
# )
# def show_output_div_old(n_submit, test_passed):
#
#     print("in show output div old")
#     if not test_passed:
#         return {'display': 'none'}
#
#     if n_submit is not None:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}


# # Submit button has been clicked
# @app.callback(
#     [
#         Output(app_id_dict['hidden_df_json_id'], 'children'),
#         Output(app_id_dict['error_id2'], 'children'),
#     ],
#     [
#         Input(app_id_dict['submit_button_id'], 'n_clicks'),
#     ],
#     [
#         State(app_id_dict['error_id'], 'children'),
#         # State(app_id_dict['cif_upload_id'], 'contents'),
#         # State(app_id_dict['cif_upload_id'], 'filename'),
#         State(app_id_dict['manual_input_of_elements'], 'data'),
#         State(app_id_dict['temperature_id'], 'value'),
#         State(app_id_dict['distance_id'], 'value'),
#         State(app_id_dict['delay_id'], 'value'),
#         State(app_id_dict['band_min_id'], 'value'),
#         State(app_id_dict['band_max_id'], 'value'),
#         State(app_id_dict['band_step_id'], 'value'),
#     ])
# def store_bragg_df_in_json(n_submit,
#                            test_passed, data_table,
#                            temperature_K, distance_m, delay_us,band_min, band_max, band_step,
#                            ):
#
#     if test_passed:
#         error_div_list = []
#         xs_dict = {}
#         wavelengths_A = np.arange(band_min, band_max, band_step)
#
#         # looking at the table to create the structure
#         print(f"{data_table =}")
#
#
#     return None, False




    #     if cif_uploads is not None:
    #         for each_index, each_content in enumerate(cif_uploads):
    #             try:
    #                 print("'{}:', reading .cif file...".format(cif_names[each_index]))
    #                 _cif_struc = parse_cif_upload(content=each_content)
    #                 _name_only = cif_names[each_index].split('.')[0]
    #                 print("'{}', calculating cross-sections...".format(cif_names[each_index]))
    #                 return
    #                 xscalculator = xscalc.XSCalculator(_cif_struc, temperature_K, max_diffraction_index=4)
    #                 print("Done calculating cross-sections!")
    #                 xs_dict[_name_only + ' (total)'] = xscalculator.xs(wavelengths_A)
    #                 xs_dict[_name_only + ' (abs)'] = xscalculator.xs_abs(wavelengths_A)
    #                 xs_dict[_name_only + ' (coh el)'] = xscalculator.xs_coh_el(wavelengths_A)
    #                 xs_dict[_name_only + ' (inc el)'] = xscalculator.xs_inc_el(wavelengths_A)
    #                 xs_dict[_name_only + ' (coh inel)'] = xscalculator.xs_coh_inel(wavelengths_A)
    #                 xs_dict[_name_only + ' (inc inel)'] = xscalculator.xs_inc_inel(wavelengths_A)
    #                 print("Calculation done.")
    #             except AttributeError as error_msg1:
    #                 print(str(error_msg1))
    #                 error1 = "ERROR: '{}', ".format(cif_names[each_index]) + str(error_msg1).split('.')[0] + '. The .cif format is not compatible, please reformat following ICSD database.'
    #                 error_div_list.append(error1)
    #             except ValueError as error_msg2:
    #                 error2 = "ERROR: '{}', ".format(cif_names[each_index]) + str(error_msg2).split('.')[0] + '.'
    #                 error_div_list.append(error2)
    #         if len(error_div_list) == 0:
    #             df_y = pd.DataFrame.from_dict(xs_dict)
    #             df_x = pd.DataFrame()
    #             df_x[constants.energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
    #             df_x = fill_df_x_types(df=df_x, distance_m=distance_m, delay_us=delay_us)
    #
    #             datasets = {
    #                 'x': df_x.to_json(orient='split', date_format='iso'),
    #                 'y': df_y.to_json(orient='split', date_format='iso'),
    #             }
    #             return json.dumps(datasets), True
    #         else:
    #             return None, error_div_list
    #     else:
    #         return None, False
    # else:
    #     return None, False

@app.callback(
    [
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        Input(app_id_dict['hidden_df_json_id'], 'children'),
        Input(app_id_dict['no_error_id'], 'children'),
        Input('x_type', 'value'),
        Input('y_type', 'value'),
        Input('plot_scale', 'value'),
        Input('xs_type', 'value'),
    ],
    )
def plot(jsonified_data, test_passed, x_type, y_type, plot_scale, xs_type):

    if test_passed:

        if jsonified_data is not None:
            df_dict = load_dfs(jsonified_data=jsonified_data)
            df_x = df_dict['x']
            df_y = df_dict['y']

            # Form selected Y df
            to_plot_list = []

            _name_only = 'tab2'
            if 'total' in xs_type:
                to_plot_list.append(_name_only + ' (total)')
            if 'abs' in xs_type:
                to_plot_list.append(_name_only + ' (abs)')
            if 'coh_el' in xs_type:
                to_plot_list.append(_name_only + ' (coh el)')
            if 'coh_inel' in xs_type:
                to_plot_list.append(_name_only + ' (coh inel)')
            if 'inc_el' in xs_type:
                to_plot_list.append(_name_only + ' (inc el)')
            if 'inc_inel' in xs_type:
                to_plot_list.append(_name_only + ' (inc inel)')
            try:
                df_to_plot = df_y[to_plot_list]
            except KeyError:
                return resubmit, [None]
            if y_type == 'attenuation':
                df_to_plot = 1 - df_y

            # Add X column
            x_tag = x_type_to_x_tag(x_type)
            df_to_plot.insert(loc=0, column=x_tag, value=df_x[x_tag])
            y_label = y_type_to_y_label(y_type)

            jsonized_plot_df = df_to_plot.to_json(orient='split', date_format='iso')

            # Plot in matplotlib
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            try:
                ax1 = df_to_plot.set_index(keys=x_tag).plot(legend=False, ax=ax1)
            except TypeError:
                pass
            ax1.set_ylabel(y_label)

            # Convert to plotly and format layout
            plotly_fig = shape_matplot_to_plotly(fig=fig, y_type=y_type, plot_scale=plot_scale)

            print("about to return html.div")
            return html.Div([dcc.Graph(figure=plotly_fig, id=app_id_dict['plot_fig_id'])]), [json.dumps(jsonized_plot_df)]
        else:
            print("about to return plot_loading")
            return plot_loading, [None]
    else:
        return plot_loading, [None]


# @app.callback(
#     [
#         Output(app_id_dict['plot_div_id'], 'children'),
#         Output(app_id_dict['hidden_df_export_json_id'], 'children'),
#     ],
#     [
#         Input(app_id_dict['hidden_df_json_id'], 'children'),
#         Input(app_id_dict['error_id'], 'children'),
#         Input('x_type', 'value'),
#         Input('y_type', 'value'),
#         Input('plot_scale', 'value'),
#         Input('xs_type', 'value'),
#     ],
#     [
#         State(app_id_dict['cif_upload_id'], 'filename'),
#     ])
# def plot(jsonified_data, test_passed, x_type, y_type, plot_scale, xs_type, fnames):
#     if test_passed:
#         if jsonified_data is not None:
#             df_dict = load_dfs(jsonified_data=jsonified_data)
#             df_x = df_dict['x']
#             df_y = df_dict['y']
#
#             # Form selected Y df
#             to_plot_list = []
#             for each_fname in fnames:
#                 _name_only = each_fname.split('.')[0]
#                 if 'total' in xs_type:
#                     to_plot_list.append(_name_only + ' (total)')
#                 if 'abs' in xs_type:
#                     to_plot_list.append(_name_only + ' (abs)')
#                 if 'coh_el' in xs_type:
#                     to_plot_list.append(_name_only + ' (coh el)')
#                 if 'coh_inel' in xs_type:
#                     to_plot_list.append(_name_only + ' (coh inel)')
#                 if 'inc_el' in xs_type:
#                     to_plot_list.append(_name_only + ' (inc el)')
#                 if 'inc_inel' in xs_type:
#                     to_plot_list.append(_name_only + ' (inc inel)')
#             try:
#                 df_to_plot = df_y[to_plot_list]
#             except KeyError:
#                 return resubmit, [None]
#             if y_type == 'attenuation':
#                 df_to_plot = 1 - df_y
#
#             # Add X column
#             x_tag = x_type_to_x_tag(x_type)
#             df_to_plot.insert(loc=0, column=x_tag, value=df_x[x_tag])
#             y_label = y_type_to_y_label(y_type)
#
#             jsonized_plot_df = df_to_plot.to_json(orient='split', date_format='iso')
#
#             # Plot in matplotlib
#             fig = plt.figure()
#             ax1 = fig.add_subplot(111)
#             try:
#                 ax1 = df_to_plot.set_index(keys=x_tag).plot(legend=False, ax=ax1)
#             except TypeError:
#                 pass
#             ax1.set_ylabel(y_label)
#
#             # Convert to plotly and format layout
#             plotly_fig = shape_matplot_to_plotly(fig=fig, y_type=y_type, plot_scale=plot_scale)
#
#             return html.Div([dcc.Graph(figure=plotly_fig, id=app_id_dict['plot_fig_id'])]), [json.dumps(jsonized_plot_df)]
#         else:
#             return plot_loading, [None]
#     else:
#         return plot_loading, [None]


@app.callback(
    [
        Output(app_id_dict['df_export_tb_div'], 'children'),
    ],
    [
        Input(app_id_dict['display_plot_data_id'], 'value'),
        Input(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        State(app_id_dict['no_error_id'], 'children'),
    ])
def display_plot_data_tb(display_check, jsonized_df_export, test_passed):

    if display_check == ['display']:
        if test_passed is True:
            dataset = json.loads(jsonized_df_export[0])
            df_to_export = pd.read_json(dataset, orient='split')
            df_tb_div_list = [
                html.Hr(),
                dt.DataTable(
                    id=app_id_dict['df_export_tb'],
                    data=df_to_export.to_dict('records'),
                    columns=[{'name': each_col, 'id': each_col} for each_col in df_to_export.columns],
                    export_format='csv',
                    style_data_conditional=[striped_rows],
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={
                        'maxHeight': '300',
                        'overflowY': 'scroll',
                    },
                )
            ]
            return [df_tb_div_list]
        else:
            return [None]
    else:
        return [None]
