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
from datetime import datetime
from urllib.parse import quote as urlquote

import ImagingReso._utilities as ir_util
from app import app
from callbacks.utilities.initialization import (init_app_ids, striped_rows, plot_loading, resubmit)
import callbacks.utilities.constants as constants
from callbacks.utilities.plot import shape_matplot_to_plotly
from callbacks.utilities.all_apps import y_type_to_y_label, x_type_to_x_tag, load_dfs, update_rows_util
from callbacks.utilities.bragg import parse_cif_file, parse_txt_file
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
    [
        Output(app_id_dict['cif_upload_fb_tab1'], 'children'),
        Output(app_id_dict['no_error_tab1'], 'children'),
        Output(app_id_dict['data_table_tab1'], 'data'),
        Output(app_id_dict['hidden_upload_time_tab1'], 'children'),
        Output(app_id_dict['a_tab1'], 'value'),
        Output(app_id_dict['b_tab1'], 'value'),
        Output(app_id_dict['c_tab1'], 'value'),
        Output(app_id_dict['alpha_tab1'], 'value'),
        Output(app_id_dict['beta_tab1'], 'value'),
        Output(app_id_dict['gamma_tab1'], 'value'),
        Output(app_id_dict['hidden_texture_add_row_time_tab1'], 'children'),
        Output(app_id_dict['texture_table_tab1'], 'data')
    ],
    [
        Input(app_id_dict['cif_upload_tab1'], 'filename'),
        Input(app_id_dict['add_row_tab1'], 'n_clicks_timestamp'),
        Input(app_id_dict['texture_add_row_tab1'], 'n_clicks_timestamp'),
    ],
    [
        State(app_id_dict['hidden_upload_time_tab1'], 'children'),
        State(app_id_dict['cif_upload_tab1'], 'contents'),
        State(app_id_dict['data_table_tab1'], 'data'),
        State(app_id_dict['data_table_tab1'], 'columns'),
        State(app_id_dict['hidden_texture_add_row_time_tab1'], 'children'),
        State(app_id_dict['texture_table_tab1'], 'data'),
        State(app_id_dict['texture_table_tab1'], 'columns')
    ],
)
def upload_feedback(cif_names, add_button_timestamp, texture_add_button_timestamp,
                    prev_upload_time, file_uploads, content_of_table, names_of_columns, prev_texture_add_row_time,
                    texture_content_of_table, names_of_texture_columns):

    data_fb_list = []
    error_div_list = []

    print(f"before: {texture_content_of_table =}")

    # print(f"{prev_texture_add_row_time =}")
    # print(f"{texture_add_button_timestamp =}")
    #
    # print(f"")
    # print(f"{add_button_timestamp =}")
    # print(f"{prev_upload_time =}")
    #
    # print(f"{cif_names =}")
    # print(f"{names_of_texture_columns =}")

    # we did not import a cif name, we need to add a row
    if cif_names is None:

        if add_button_timestamp != prev_upload_time:
            # we need to add a row in the top table
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90, \
                   texture_add_button_timestamp, texture_content_of_table

        else:
            print("we clicked add texture row")
            # we need to add a row in the texture table
            texture_content_of_table.append({c['id']: '' for c in names_of_texture_columns})
            print(f"after: {texture_content_of_table =}")
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90, \
                   texture_add_button_timestamp, texture_content_of_table

    # we are importing a file
    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            # we really clicked the add a row button
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90, \
                   texture_add_button_timestamp, texture_content_of_table

        elif texture_add_button_timestamp != prev_texture_add_row_time:
            print("we clicked add texture row!")

        else:
            # we did not click add a row button
            content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc = parse_txt_file(content=file_uploads)

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

    if ('.cif' in cif_names) or ('.txt' in cif_names):
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
           interaxial_angle_beta, interaxial_angle_gamma, \
           prev_texture_add_row_time, texture_content_of_table


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
                    prev_upload_time, file_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:
        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc = parse_txt_file(content=file_uploads)

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

    if ('.cif' in cif_names) or ('.txt' in cif_names):
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
                    prev_upload_time, file_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:
        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc = parse_txt_file(content=file_uploads)

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

    if ('.cif' in cif_names) or ('.txt' in cif_names):
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
                    prev_upload_time, file_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:
        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc = parse_txt_file(content=file_uploads)

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

    if ('.cif' in cif_names) or ('.txt' in cif_names):
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
                    prev_upload_time, file_uploads,
                    content_of_table, names_of_columns):

    data_fb_list = []
    error_div_list = []

    if cif_names is None:
        content_of_table.append({c['id']: '' for c in names_of_columns})
        return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, 3.5238, 3.5238, 3.5238, 90, 90, 90

        else:
            content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc = parse_txt_file(content=file_uploads)

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

    if ('.cif' in cif_names) or ('.txt' in cif_names):
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


def clean_data_tab(data_tab=None):
    '''
    remove all the rows with no chemical formula defined
    '''
    data_tab_cleaned = []
    for _entry in data_tab:
        if _entry[chem_name] == '':
            continue
        else:
            data_tab_cleaned.append(_entry)
    return data_tab_cleaned


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

    if not data_tab:
        print(f"- data_tab is empty!")
        return

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

        try:
            atoms.append(matter.Atom(_chem_name, (_h, _k, _l)))
        except ValueError as msg:
            return f"error in format of h,k and/or l ({msg})"

    print(f"- calculating lattice")
    _lattice = matter.Lattice(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)

    print(f"- calculating structure")
    _structure = matter.Structure(atoms, _lattice, sgid=225)

    print(f"- calculating cross-section")
    try:
        _xscalculator = xscalc.XSCalculator(_structure, temperature, max_diffraction_index=4)
    except AttributeError as msg:
        return msg

    xs_dict[_name_only + ' (total)'] = _xscalculator.xs(wavelengths_A)
    xs_dict[_name_only + ' (abs)'] = _xscalculator.xs_abs(wavelengths_A)
    xs_dict[_name_only + ' (coh el)'] = _xscalculator.xs_coh_el(wavelengths_A)
    xs_dict[_name_only + ' (inc el)'] = _xscalculator.xs_inc_el(wavelengths_A)
    xs_dict[_name_only + ' (coh inel)'] = _xscalculator.xs_coh_inel(wavelengths_A)
    xs_dict[_name_only + ' (inc inel)'] = _xscalculator.xs_inc_inel(wavelengths_A)
    print("- Calculation done!")

    return None


# submit button clicked
@app.callback(
    [
        Output(app_id_dict['hidden_df_json_id'], 'children'),
        Output(app_id_dict['no_error_id'], 'children'),
        Output(app_id_dict['output_id'], 'style'),
        Output(app_id_dict['general_processing_errors'], 'children')
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
        State(app_id_dict['no_error_tab1'], 'children'),

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
        State(app_id_dict['no_error_tab3'], 'children'),

        State(app_id_dict['data_table_tab4'], 'data'),
        State(app_id_dict['a_tab4'], 'value'),
        State(app_id_dict['b_tab4'], 'value'),
        State(app_id_dict['c_tab4'], 'value'),
        State(app_id_dict['alpha_tab4'], 'value'),
        State(app_id_dict['beta_tab4'], 'value'),
        State(app_id_dict['gamma_tab4'], 'value'),
        State(app_id_dict['no_error_tab4'], 'children'),

        State(app_id_dict['data_table_tab5'], 'data'),
        State(app_id_dict['a_tab5'], 'value'),
        State(app_id_dict['b_tab5'], 'value'),
        State(app_id_dict['c_tab5'], 'value'),
        State(app_id_dict['alpha_tab5'], 'value'),
        State(app_id_dict['beta_tab5'], 'value'),
        State(app_id_dict['gamma_tab5'], 'value'),
        State(app_id_dict['no_error_tab5'], 'children'),

        State(app_id_dict['temperature_id'], 'value'),
        State(app_id_dict['distance_id'], 'value'),
        State(app_id_dict['delay_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_step_id'], 'value'),
    ]
)
def show_output_div(n_submit,
                    data_tab1, a_tab1, b_tab1, c_tab1, alpha_tab1, beta_tab1, gamma_tab1, no_error_tab1,
                    data_tab2, a_tab2, b_tab2, c_tab2, alpha_tab2, beta_tab2, gamma_tab2, no_error_tab2,
                    data_tab3, a_tab3, b_tab3, c_tab3, alpha_tab3, beta_tab3, gamma_tab3, no_error_tab3,
                    data_tab4, a_tab4, b_tab4, c_tab4, alpha_tab4, beta_tab4, gamma_tab4, no_error_tab4,
                    data_tab5, a_tab5, b_tab5, c_tab5, alpha_tab5, beta_tab5, gamma_tab5, no_error_tab5,
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


        if no_error_tab1:
            tab1_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab1,
                                            log_label='tab1',
                                            a=a_tab1, b=b_tab1, c=c_tab1,
                                            alpha=alpha_tab1, beta=beta_tab1, gamma=gamma_tab1,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A)
            if tab1_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab1: {tab1_error_msg}")]

        if no_error_tab2:
            tab2_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab2,
                                            log_label='tab2',
                                            a=a_tab2, b=b_tab2, c=c_tab2,
                                            alpha=alpha_tab2, beta=beta_tab2, gamma=gamma_tab2,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A)
            if tab2_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab2: {tab2_error_msg}")]

        if no_error_tab3:
            tab3_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab3,
                                            log_label='tab3',
                                            a=a_tab3, b=b_tab3, c=c_tab3,
                                            alpha=alpha_tab3, beta=beta_tab3, gamma=gamma_tab3,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A)
            if tab3_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab3: {tab3_error_msg}")]

        if no_error_tab4:
            tab4_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab4,
                                            log_label='tab4',
                                            a=a_tab4, b=b_tab4, c=c_tab4,
                                            alpha=alpha_tab4, beta=beta_tab4, gamma=gamma_tab4,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A)
            if tab4_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab4: {tab4_error_msg}")]

        if no_error_tab5:
            tab5_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab5,
                                            log_label='tab5',
                                            a=a_tab5, b=b_tab5, c=c_tab5,
                                            alpha=alpha_tab5, beta=beta_tab5, gamma=gamma_tab5,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A)
            if tab5_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab5: {tab5_error_msg}")]

        if not something_to_plot:
            return None,  False, {'display': 'none'}, None

        df_y = pd.DataFrame.from_dict(xs_dict)
        df_x = pd.DataFrame()
        df_x[constants.energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
        df_x = fill_df_x_types(df=df_x, distance_m=distance, delay_us=delay)

        datasets = {
                    'x': df_x.to_json(orient='split', date_format='iso'),
                    'y': df_y.to_json(orient='split', date_format='iso'),
                    }
        return json.dumps(datasets), True, {'display': 'block'}, None
    else:
        return None,  False, {'display': 'none'}, None


def update_list_to_plot(name='tab2', df_y=None, to_plot_list=None, xs_type=None):

    if f'{name} (total)' in df_y.columns:

        if 'total' in xs_type:
            to_plot_list.append(name + ' (total)')
        if 'abs' in xs_type:
            to_plot_list.append(name + ' (abs)')
        if 'coh_el' in xs_type:
            to_plot_list.append(name + ' (coh el)')
        if 'coh_inel' in xs_type:
            to_plot_list.append(name + ' (coh inel)')
        if 'inc_el' in xs_type:
            to_plot_list.append(name + ' (inc el)')
        if 'inc_inel' in xs_type:
            to_plot_list.append(name + ' (inc inel)')


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

            update_list_to_plot(name='tab1', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab2', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab3', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab4', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab5', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)

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
            return html.Div([dcc.Graph(figure=plotly_fig,
                                       id=app_id_dict['plot_fig_id'])]), \
                   [json.dumps(jsonized_plot_df)]
        else:
            print("about to return plot_loading")
            return plot_loading, [None]
    else:
        return plot_loading, [None]


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


# hourglass icon
@app.callback(Output("loading-output-2", 'children'),
              Input(app_id_dict['submit_button_id'], "n_clicks"))
def loading_icon(value):
    time.sleep(3)
    return value


def get_current_timestamp():
    """Convert the unix time stamp into a human-readable time format

    Format return will look like  "y2018_m01_d29_h10_mn30"
    """
    now = datetime.now()
    return now.strftime("y%Y_m%m_d%d_h%H_mn%M")


def create_table_output_file_name(table=None):
    '''
    create the name of the file to use to export the data of this tab
    '''
    if table is None:
        return None

    list_atom = []
    for _row in table:
        list_atom.append(_row[chem_name])

    if list_atom == []:
        return None

    file_name = "_".join(list_atom) + f"_{get_current_timestamp()}.txt"
    return file_name


def format_data(dict=None):
    '''
    format the data from a dictionary into a string json
    '''
    if dict is None:
        return ""

    return json.dumps(dict)


# export tab1
@app.callback(Output(app_id_dict["download_tab1"], "data"),
              Input(app_id_dict["download_button_tab1"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab1'], 'data'),
                  State(app_id_dict['a_tab1'], 'value'),
                  State(app_id_dict['b_tab1'], 'value'),
                  State(app_id_dict['c_tab1'], 'value'),
                  State(app_id_dict['alpha_tab1'], 'value'),
                  State(app_id_dict['beta_tab1'], 'value'),
                  State(app_id_dict['gamma_tab1'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# export tab2
@app.callback(Output(app_id_dict["download_tab2"], "data"),
              Input(app_id_dict["download_button_tab2"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab2'], 'data'),
                  State(app_id_dict['a_tab2'], 'value'),
                  State(app_id_dict['b_tab2'], 'value'),
                  State(app_id_dict['c_tab2'], 'value'),
                  State(app_id_dict['alpha_tab2'], 'value'),
                  State(app_id_dict['beta_tab2'], 'value'),
                  State(app_id_dict['gamma_tab2'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# export tab3
@app.callback(Output(app_id_dict["download_tab3"], "data"),
              Input(app_id_dict["download_button_tab3"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab3'], 'data'),
                  State(app_id_dict['a_tab3'], 'value'),
                  State(app_id_dict['b_tab3'], 'value'),
                  State(app_id_dict['c_tab3'], 'value'),
                  State(app_id_dict['alpha_tab3'], 'value'),
                  State(app_id_dict['beta_tab3'], 'value'),
                  State(app_id_dict['gamma_tab3'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# export tab4
@app.callback(Output(app_id_dict["download_tab4"], "data"),
              Input(app_id_dict["download_button_tab4"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab4'], 'data'),
                  State(app_id_dict['a_tab4'], 'value'),
                  State(app_id_dict['b_tab4'], 'value'),
                  State(app_id_dict['c_tab4'], 'value'),
                  State(app_id_dict['alpha_tab4'], 'value'),
                  State(app_id_dict['beta_tab4'], 'value'),
                  State(app_id_dict['gamma_tab4'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# export tab5
@app.callback(Output(app_id_dict["download_tab5"], "data"),
              Input(app_id_dict["download_button_tab5"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab5'], 'data'),
                  State(app_id_dict['a_tab5'], 'value'),
                  State(app_id_dict['b_tab5'], 'value'),
                  State(app_id_dict['c_tab5'], 'value'),
                  State(app_id_dict['alpha_tab5'], 'value'),
                  State(app_id_dict['beta_tab5'], 'value'),
                  State(app_id_dict['gamma_tab5'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# texture checklist tab1
@app.callback([
                Output(app_id_dict['texture_add_row_tab1'], "disabled"),
                Output(app_id_dict['texture_table_tab1'], "editable")
                ],
              Input(app_id_dict['texture_checklist_tab1'], "value"))
def method(checklist_tab1_value):

    # button is unchecked
    if not checklist_tab1_value:
        return True, False

    # button is checked
    if checklist_tab1_value[0].strip() == 'Texture':
        return False, True

# grain size checklist tab1
@app.callback(
    Output(app_id_dict['grain_size_input_tab1'], "disabled"),
    Input(app_id_dict['grain_size_checklist_tab1'], "value"))
def method_grain_size_tab1(checklist_value):

    # button is unchecked
    if not checklist_value:
        return True

    # button is checked
    return False
