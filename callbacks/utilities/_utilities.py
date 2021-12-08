import os
import sys
from dash import html
from dash import dcc
from dash import dash_table as dt
import pandas as pd
import io
import base64
from scipy.interpolate import interp1d
import numpy as np
import json
import plotly.tools as tls

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser

import ImagingReso._utilities as ir_util
from ImagingReso.resonance import Resonance

from config import app_dict
from callbacks.utilities.validator import MyValidator, is_number, validate_input
# from callbacks.utilities import constants
import callbacks.utilities.constants as constants
from callbacks.utilities.initialization import iso_tb_df_default
from callbacks.utilities.resonance import fill_range_table_by_e



# output_stack_header_short_df = pd.DataFrame({
#     'name': [constants.ratio_name,
#              constants.molar_name],
#     'id': [constants.ratio_name,
#            constants.molar_name],
#     'deletable': [False, False],
#     'editable': [False, False],
# })

col_width_1 = 'one column'
col_width_3 = 'three columns'
col_width_5 = 'five columns'
col_width_6 = 'six columns'
empty_div = html.Div()

distance_default = 16.45  # in meter
delay_default = 0  # in us
temperature_default = 293  # in Kelvin
plot_loading = html.H2('Plot loading...')


compos_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.compos_2nd_col_id: {'type': 'number', 'greater_than_zero': True},
}

iso_dict_schema = {
    # layer_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.layer_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.ele_name: {'type': 'string', 'empty': False, 'required': True, },
    constants.iso_name: {'type': 'string', 'empty': False, 'required': True, },
    constants.iso_ratio_name: {'type': 'number', 'min': 0, 'max': 1, 'required': True, 'between_zero_and_one': True, },
}

sample_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.thick_name: {'type': 'number', 'min': 0, 'required': True, },
    constants.density_name: {'anyof_type': ['string', 'number'], 'min': 0, 'empty_str': True, },
}

#
# def creat_sample_df_from_compos_df(compos_tb_df):
#     _compos_tb_df = compos_tb_df[:]
#     sample_df = pd.DataFrame()
#     sample_df[constants.chem_name] = _compos_tb_df[constants.chem_name]
#     sample_df[constants.thick_name] = 1
#     sample_df[constants.density_name] = ''
#     return sample_df


# def force_dict_to_numeric(input_dict_list: list):
#     input_df = pd.DataFrame(input_dict_list)
#     input_dict = input_df.to_dict('list')
#     keys = input_dict.keys()
#     output_dict = {}
#     for each_key in keys:
#         _current_list = input_dict[each_key]
#         _current_output_list = []
#         for each_item in _current_list:
#             if is_number(each_item):
#                 _current_output_list.append(float(each_item))
#             else:
#                 _current_output_list.append(each_item)
#         output_dict[each_key] = _current_output_list
#     return output_dict


# def load_beam_shape(relative_path_to_beam_shape):
#     # Load beam shape from static
#     df = pd.read_csv(relative_path_to_beam_shape, sep='\t', skiprows=0)
#     df.columns = ['wavelength_A', 'flux']
#     # Get rid of crazy data
#     df.drop(df[df.wavelength_A < 0].index, inplace=True)
#     df.drop(df[df.flux <= 0].index, inplace=True)
#     df.reset_index(drop=True, inplace=True)
#     # Convert wavelength to energy
#     energy_array = ir_util.angstroms_to_ev(df['wavelength_A'])
#     df.insert(1, 'energy_eV', round(energy_array, 6))
#     # df.insert(1, 'energy_eV', energy_array)
#     return df


# def unpack_iso_tb_df_and_update(o_reso, iso_tb_df, iso_changed):
#     if len(iso_changed) == 0:
#         return o_reso
#     else:
#         layer_list = list(o_reso.stack.keys())
#         for each_layer in layer_list:
#             element_list = o_reso.stack[each_layer]['elements']
#             for each_ele in element_list:
#                 _ele_ratio_list = []
#                 for iso_i in range(len(iso_tb_df)):
#                     if each_layer == iso_tb_df[constants.layer_name][iso_i] and each_ele == iso_tb_df[constants.ele_name][iso_i]:
#                         _ele_ratio_list.append(float(iso_tb_df[constants.iso_ratio_name][iso_i]))
#                 o_reso.set_isotopic_ratio(compound=each_layer, element=each_ele, list_ratio=_ele_ratio_list)
#         return o_reso


# def calculate_transmission(sample_tb_df, iso_tb_df, iso_changed, beamline, band_min, band_max, band_type, database):
#     _main_path = os.path.abspath(os.path.dirname(__file__))
#     _path_to_beam_shape = {'imaging': 'static/instrument_file/beam_flux_cg1d.txt',
#                            'imaging_crop': 'static/instrument_file/beam_flux_cg1d_crop.txt',
#                            'snap': 'static/instrument_file/beam_flux_snap.txt',
#                            # 'venus': 'static/instrument_file/beam_flux_venus.txt',
#                            }
#     df_flux_raw = load_beam_shape(_path_to_beam_shape[beamline])
#     if beamline in ['imaging', 'imaging_crop']:
#         e_min = df_flux_raw['energy_eV'].min()
#         e_max = df_flux_raw['energy_eV'].max()
#     else:
#         if band_type == 'lambda':
#             e_min = round(ir_util.angstroms_to_ev(band_max), 6)
#             e_max = round(ir_util.angstroms_to_ev(band_min), 6)
#         else:  # band_type == 'energy'
#             e_min = band_min
#             e_max = band_max
#
#     e_step = (e_max - e_min) / (100 - 1)
#     __o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step, database=database)
#     _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=sample_tb_df)
#     o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)
#     o_stack = o_reso.stack
#
#     # interpolate with the beam shape energy
#     energy = o_reso.total_signal['energy_eV'].round(6)  # !!!need to fix ImagingReso energy_eV columns
#     interp_type = 'cubic'
#     interp_flux_function = interp1d(x=df_flux_raw['energy_eV'], y=df_flux_raw['flux'], kind=interp_type)
#     flux_interp = interp_flux_function(energy)
#     df_flux_interp = pd.DataFrame()
#     df_flux_interp['energy_eV'] = energy
#     df_flux_interp['flux'] = flux_interp
#     df_flux = df_flux_interp[:]
#     trans_tag = 'transmission'
#     mu_tag = 'mu_per_cm'
#     o_signal = o_reso.stack_signal
#
#     _total_trans = _calculate_transmission(flux_df=df_flux, trans_array=o_reso.total_signal[trans_tag])
#
#     for each_layer in o_stack.keys():
#         _current_layer_thickness = o_stack[each_layer]['thickness']['value']
#         if len(o_stack.keys()) == 1:
#             _current_layer_trans = _total_trans
#         else:
#             _current_layer_trans = _calculate_transmission(flux_df=df_flux,
#                                                            trans_array=o_signal[each_layer][trans_tag])
#         o_stack[each_layer][trans_tag] = _current_layer_trans
#         o_stack[each_layer][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_layer_trans,
#                                                                  thickness=_current_layer_thickness)
#         for each_ele in o_stack[each_layer]['elements']:
#             _current_ele_trans = _calculate_transmission(flux_df=df_flux,
#                                                          trans_array=o_signal[each_layer][each_ele][trans_tag])
#             o_stack[each_layer][each_ele][trans_tag] = _current_ele_trans
#             o_stack[each_layer][each_ele][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_ele_trans,
#                                                                                thickness=_current_layer_thickness)
#     return _total_trans, o_stack


# def _calculate_transmission(flux_df: pd.DataFrame, trans_array: np.array):
#     # calculated transmitted flux
#     trans_flux = trans_array * flux_df['flux']
#     integr_total = np.trapz(y=flux_df['flux'] / flux_df['energy_eV'], x=flux_df['energy_eV'], dx=1e-6).round(3)
#     integr_trans = np.trapz(y=trans_flux / flux_df['energy_eV'], x=flux_df['energy_eV'], dx=1e-6).round(3)
#     _trans = integr_trans / integr_total * 100
#     return _trans

#
# def _transmission_to_mu_per_cm(transmission, thickness):
#     mu_per_cm = -np.log(transmission / 100) / (thickness / 10)
#     return mu_per_cm


# def form_transmission_result_div(sample_tb_rows, iso_tb_rows, iso_changed, database,
#                                  beamline, band_min, band_max, band_type):
#     disclaimer = markdown_disclaimer_sns
#     if beamline == 'snap':
#         beamline_name = 'SNAP (BL-3), SNS'
#     elif beamline == 'venus':
#         beamline_name = 'VENUS (BL-10), SNS'
#     elif beamline == 'imaging_crop':
#         beamline_name = u'IMAGING (CG-1D) \u2264 5.35 \u212B, HFIR'
#         disclaimer = markdown_disclaimer_hfir
#     else:  # beamline == 'imaging':
#         beamline_name = 'IMAGING (CG-1D), HFIR'
#         disclaimer = markdown_disclaimer_hfir
#     # Modify input for testing
#     sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
#     sample_tb_df = pd.DataFrame(sample_tb_dict)
#     if len(iso_changed) == 1:
#         iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
#         iso_tb_df = pd.DataFrame(iso_tb_dict)
#     else:
#         iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)
#
#     # Calculation starts
#     total_trans, o_stack = calculate_transmission(sample_tb_df=sample_tb_df,
#                                                   iso_tb_df=iso_tb_df,
#                                                   iso_changed=iso_changed,
#                                                   beamline=beamline,
#                                                   band_min=band_min,
#                                                   band_max=band_max,
#                                                   band_type=band_type,
#                                                   database=database)
#     output_div_list = [
#         html.Hr(),
#         html.H3('Result at ' + beamline_name),
#         html.P('Transmission (total): {} %'.format(round(total_trans, 3))),
#         html.P('Attenuation (total): {} %'.format(round(100 - total_trans, 3))),
#         disclaimer,
#         # html.Div(sample_stack_div_list),
#     ]
#     return output_div_list, o_stack


output_stack_header_df = pd.DataFrame({
    'name': [constants.thick_name,
             constants.density_name,
             constants.ratio_name,
             constants.molar_name,
             constants.number_density_name,
             constants.mu_per_cm_name],
    'id': [constants.thick_name,
           constants.density_name,
           constants.ratio_name,
           constants.molar_name,
           constants.number_density_name,
           constants.mu_per_cm_name],
    'deletable': [False, False, False, False, False, False],
    'editable': [False, False, False, False, False, False],
})


output_stack_header_short_df = pd.DataFrame({
    'name': [constants.ratio_name,
             constants.molar_name],
    'id': [constants.ratio_name,
           constants.molar_name],
    'deletable': [False, False],
    'editable': [False, False],
})


def form_sample_stack_table_div(o_stack, full_stack=True):
    sample_stack_div_list = [html.Hr(), html.H4('Sample stack:')]
    layers = list(o_stack.keys())
    layer_dict = {}

    # For short sample stack output
    if full_stack:
        output_header_df = output_stack_header_df
    else:
        output_header_df = output_stack_header_short_df

    for l, layer in enumerate(layers):
        elements_in_current_layer = o_stack[layer]['elements']
        l_str = str(l + 1)
        current_layer_list = [
            html.H5("Layer {}: {}".format(l_str, layer)),
        ]
        layer_dict[constants.thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[constants.density_name] = round(o_stack[layer]['density']['value'], 3)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[constants.ratio_name] = ":".join(_ratio_str_list)
        layer_dict[constants.molar_name] = round(o_stack[layer]['molar_mass']['value'], 4)
        layer_dict[constants.number_density_name] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'])
        layer_dict[constants.mu_per_cm_name] = '{:0.3e}'.format(o_stack[layer]['mu_per_cm'])

        _df_layer = pd.DataFrame([layer_dict])
        current_layer_list.append(
            dt.DataTable(data=_df_layer.to_dict('records'),
                         columns=output_header_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filter_action='none',
                         sort_action='none',
                         row_deletable=False,
                         style_cell_conditional=output_tb_uneven_6_col,
                         ))

        for e, ele in enumerate(elements_in_current_layer):
            e_str = str(e + 1)
            current_layer_list.append(html.P("Element {}: {}".format(e_str, ele)))
            _iso_list = o_stack[layer][ele]['isotopes']['list']
            _iso_ratios = o_stack[layer][ele]['isotopes']['isotopic_ratio']
            iso_dict = {}
            name_list = []
            id_list = []
            deletable_list = []
            editable_list = []
            for _index, iso in enumerate(_iso_list):
                current_id = 'column_' + str(_index + 1)
                name_list.append(iso)
                id_list.append(current_id)
                deletable_list.append(False)
                editable_list.append(False)
                iso_dict[current_id] = round(_iso_ratios[_index], 4)

            _i = len(id_list)
            name_list.append(constants.molar_name)
            molar_name_id = 'column_' + str(_i + 1)
            id_list.append(molar_name_id)
            deletable_list.append(False)
            editable_list.append(False)
            iso_dict[molar_name_id] = round(o_stack[layer][ele]['molar_mass']['value'], 4)

            # For short sample stack output
            if full_stack:
                name_list.append(constants.number_density_name)
                number_density_name_id = 'column_' + str(_i + 2)
                id_list.append(number_density_name_id)
                deletable_list.append(False)
                editable_list.append(False)
                name_list.append(constants.mu_per_cm_name)
                mu_per_cm_name_id = 'column_' + str(_i + 3)
                id_list.append(mu_per_cm_name_id)
                deletable_list.append(False)
                editable_list.append(False)
                iso_dict[number_density_name_id] = '{:0.3e}'.format(o_stack[layer][ele]['atoms_per_cm3'])
                iso_dict[mu_per_cm_name_id] = '{:0.3e}'.format(o_stack[layer][ele]['mu_per_cm'])
                cell_conditional = [
                    {'if': {'column_id': molar_name_id},
                     'width': '11%'},
                    {'if': {'column_id': number_density_name_id},
                     'width': '11%'},
                    {'if': {'column_id': mu_per_cm_name_id},
                     'width': '11%'},
                ]
            else:
                cell_conditional = []

            _df_iso = pd.DataFrame([iso_dict])
            iso_output_header_df = pd.DataFrame({
                'name': name_list,
                'id': id_list,
                'deletable': deletable_list,
                'editable': editable_list,
            })
            current_layer_list.append(
                dt.DataTable(data=_df_iso.to_dict('records'),
                             columns=iso_output_header_df.to_dict('records'),
                             editable=False,
                             row_selectable=False,
                             filter_action='none',
                             sort_action='none',
                             row_deletable=False,
                             style_cell_conditional=cell_conditional
                             ))
        # Append current layer to the main list
        sample_stack_div_list.append(html.Div(current_layer_list))
        sample_stack_div_list.append(html.Br())
    return sample_stack_div_list


def convert_input_to_composition(compos_df, compos_type, o_stack):
    if compos_type == constants.weight_name:
        fill_name = constants.atomic_name_p
        update_name = constants.weight_name_p
    else:
        fill_name = constants.weight_name_p
        update_name = constants.atomic_name_p
    result_list = []
    _ele_list = []
    _mol_list = []
    _input_converted_p_list = []
    _input_sum = compos_df[constants.compos_2nd_col_id].sum()
    for _n, each_chem in enumerate(compos_df[constants.chem_name]):
        _molar_mass = o_stack[each_chem]['molar_mass']['value']
        input_num = compos_df[constants.compos_2nd_col_id][_n]
        _current_ele_list = o_stack[each_chem]['elements']
        _current_ratio_list = o_stack[each_chem]['stoichiometric_ratio']
        _input_percentage = input_num * 100 / _input_sum
        _ele_list += _current_ele_list
        if compos_type == constants.weight_name:  # wt. input (g)
            _result = input_num / _molar_mass
            _mol_list += list(np.array(_current_ratio_list) * _result)
        else:  # at. input (mol)
            _result = input_num * _molar_mass
            _mol_list += list(np.array(_current_ratio_list) * input_num)
        result_list.append(_result)
        _input_converted_p_list.append(_input_percentage)

    result_array = np.array(result_list)
    _input_converted_p_array = np.array(_input_converted_p_list)
    _output_array = result_array * 100 / sum(result_array)
    compos_df[fill_name] = np.round(_output_array, 3)
    compos_df[update_name] = np.round(_input_converted_p_array, 3)
    return compos_df, _ele_list, _mol_list


def convert_to_effective_formula(ele_list, mol_list):
    ele_array = np.array(ele_list)
    mol_array = np.array(mol_list)
    unique_ele = set(ele_array)
    mol_sum_for_ele_list = []
    for _e in unique_ele:
        indices = ele_array == _e
        mol_for_this_ele = mol_array[indices]
        mol_sum_for_ele_list.append(mol_for_this_ele.sum())
    mol_minimum = min(mol_sum_for_ele_list)
    mol_sum_for_ele_array = np.array(mol_sum_for_ele_list) / mol_minimum
    effective_str = ''
    for index, _e in enumerate(unique_ele):
        effective_str += _e + str(int(round(mol_sum_for_ele_array[index], 3) * 1000))
    return effective_str


def _load_jsonified_data(jsonified_data):
    datasets = json.loads(jsonified_data)
    return datasets


def _extract_df(datasets):
    df_name_list = ['x', 'y']
    df_dict = {}
    for each_name in df_name_list:
        df_dict[each_name] = pd.read_json(datasets[each_name], orient='split')
    return df_dict


def load_dfs(jsonified_data):
    datasets = _load_jsonified_data(jsonified_data=jsonified_data)
    df_dict = _extract_df(datasets=datasets)
    return df_dict


def x_type_to_x_tag(x_type):
    # Determine X names to plot
    if x_type == 'energy':
        x_tag = constants.energy_name
    elif x_type == 'lambda':
        x_tag = constants.wave_name
    else:
        x_tag = constants.tof_name
    return x_tag


def y_type_to_y_label(y_type):
    if y_type == 'transmission':
        y_label = 'Transmission'
    elif y_type == 'attenuation':
        y_label = 'Attenuation'
    elif y_type == 'counts':
        y_label = 'Counts'
    elif y_type == 'sigma':
        y_label = 'Cross-sections (barn)'
    elif y_type == 'sigma_raw':
        y_label = 'Cross-sections (barn)'
    else:  # y_type == 'mu_per_cm':
        y_label = 'Attenuation coefficient \u03BC (cm\u207B\u00B9)'
    return y_label


def x_type_to_x_label(x_type):
    if x_type == 'energy':
        x_label = constants.energy_name
    elif x_type == 'lambda':
        x_label = constants.wave_name
    elif x_type == 'time':
        x_label = constants.tof_name
    else:  # x_type == 'number':
        x_label = constants.number_name
    return x_label


def shape_reso_df_to_output(y_type, x_type, show_opt, jsonified_data, prev_show_opt, to_csv):
    df_dict = load_dfs(jsonified_data=jsonified_data)
    # Determine Y df and y_label to plot

    y_label = y_type_to_y_label(y_type)

    df_x = df_dict['x']
    df_y = df_dict['y']

    # Determine X names to plot
    x_tag = x_type_to_x_tag(x_type)

    # Locate items based on plot level provided
    total_col_name_list = []
    layer_col_name_list = []
    ele_col_name_list = []
    iso_col_name_list = []
    atoms_per_cm3_col_name_list = []
    for col_name in df_y.columns:
        if col_name.count('Total') == 0:
            _num_of_slash = col_name.count('/')
            if _num_of_slash == 0:
                layer_col_name_list.append(col_name)
            elif _num_of_slash == 1:
                ele_col_name_list.append(col_name)
            elif _num_of_slash == 2:
                if col_name.count('atoms_per_cm3') != 0:
                    atoms_per_cm3_col_name_list.append(col_name)
                else:
                    iso_col_name_list.append(col_name)
        else:
            total_col_name_list.append(col_name)

    _to_export_list = []
    if len(show_opt) == 0:
        _to_export_list.append(prev_show_opt)
    if 'total' in show_opt:
        _to_export_list.extend(total_col_name_list)
    if 'layer' in show_opt:
        _to_export_list.extend(layer_col_name_list)
    if 'ele' in show_opt:
        _to_export_list.extend(ele_col_name_list)
    if to_csv:
        _to_export_list.extend(atoms_per_cm3_col_name_list)
    if 'iso' in show_opt:
        _to_export_list.extend(iso_col_name_list)

    return df_x, df_y, _to_export_list, x_tag, y_label


def fill_df_x_types(df: pd.DataFrame, distance_m):
    df.insert(loc=1, column=constants.tof_name, value=ir_util.ev_to_s(array=df[constants.energy_name],
                                                            source_to_detector_m=distance_m,
                                                            offset_us=0))
    df.insert(loc=1, column=constants.wave_name, value=ir_util.ev_to_angstroms(df[constants.energy_name]))
    df[constants.tof_name] = df[constants.tof_name] * 1e6
    return df


def shape_df_to_plot(df, x_type, distance, delay):
    if x_type == 'lambda':
        df['X'] = ir_util.s_to_angstroms(array=df['X'], source_to_detector_m=distance, offset_us=delay)
    if x_type == 'energy':
        df['X'] = ir_util.s_to_ev(array=df['X'], source_to_detector_m=distance, offset_us=delay)
    if x_type == 'number':
        df['X'] = range(1, len(df['X']) + 1)
    if x_type == 'time':
        df['X'] = df['X'] * 1e6 + delay
    return df


# Layout
striped_rows = {'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'}

editable_white = {'if': {'column_editable': False},
                  'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white'}


def add_del_rows(n_add, n_del, rows, columns):
    if n_add > n_del:
        rows.append({c['id']: '' for c in columns})
    elif n_add < n_del:
        if len(rows) > 1:
            rows = rows[:-1]
    else:
        rows = rows[:]
    return rows


def update_rows_util(n_add, n_del, list_of_contents, upload_time, prev_upload_time, list_of_names, rows, columns):
    error_message = None
    if upload_time != prev_upload_time:
        if list_of_contents is not None:
            _rows = []
            for c, n in zip(list_of_contents, list_of_names):
                current_rows, error_message = parse_contents_to_rows(c, n, rows)
                _rows.extend(current_rows)
            rows = _rows
    else:
        rows = add_del_rows(n_add=n_add, n_del=n_del, rows=rows, columns=columns)
    return rows, error_message, upload_time


def parse_contents_to_rows(contents, filename, rows):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    div = None

    if '.csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), na_filter=False)
    elif '.xls' in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded), na_filter=False)
    elif '.txt' in filename:
        # Assume that the user uploaded an txt file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', na_filter=False)
    else:
        df = None
        div = html.Div(["ERROR: '{}', only '.csv', '.xls' and '.txt' are currently supported.".format(filename)])

    if df is not None:
        if len(df) == 0:
            div = html.Div(["ERROR: '{}', contains no data.".format(filename)])
        # if df.columns != list(rows[0].keys()):
        elif list(df.columns) != list(rows[0].keys()):
            div = html.Div(
                ["ERROR: '{}', contains invalid column name. '{}' required.".format(filename, list(rows[0].keys()))])
        else:
            df = df[df[constants.chem_name] != '']
            rows = df.to_dict('records')

    return rows, div


def parse_content(content, name, header):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    error_div = None
    if '.csv' in name:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), na_filter=False, header=header)
    elif '.xls' in name:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded), na_filter=False, header=header)
    elif '.txt' in name:
        # Assume that the user uploaded an txt file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', na_filter=False, header=header)
    else:
        df = None
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.csv', '.xls' and '.txt' are currently supported.".format(
                name)])
    return df, error_div


def parse_cif_upload(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    cif_s = decoded.decode('utf-8')
    p = getParser('cif')
    struc = p.parse(cif_s)
    struc.sg = p.spacegroup
    return struc


app_links_list = []
for i, each_app in enumerate(app_dict.keys()):
    current_number_str = str(i + 1) + '. '
    current_app_name = app_dict[each_app]['name']
    current_url = app_dict[each_app]['url']
    app_links_list.append(current_number_str)
    app_links_list.append(dcc.Link(current_app_name, href=current_url))
    app_links_list.append(html.Br())
app_links_div = html.Div(app_links_list)


output_tb_uneven_6_col = [
    {'if': {'column_id': constants.thick_name},
     'width': '22%'},
    {'if': {'column_id': constants.density_name},
     'width': '22%'},
    {'if': {'column_id': constants.ratio_name},
     'width': '22%'},
    {'if': {'column_id': constants.molar_name},
     'width': '11%'},
    {'if': {'column_id': constants.number_density_name},
     'width': '11%'},
    {'if': {'column_id': constants.mu_per_cm_name},
     'width': '11%'},
]


# markdown_sample = dcc.Markdown('''
# NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**. Density input can **ONLY**
# be **omitted (leave as blank)** if the input formula is a single element.''')
#
# markdown_disclaimer_sns = dcc.Markdown('''
# **Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections
# from **ENDF/B** database and the **simulated** beam spectrum at this beamline.''')
#
# markdown_disclaimer_hfir = dcc.Markdown('''
# **Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections
# from **ENDF/B** database and the **measured** beam spectrum at this beamline.''')
#
# label_sample = html.Label(['When omitted, natural densities will be used. List of densities can be found ',
#                            html.A("here.", href='http://periodictable.com/Properties/A/Density.al.html',
#                                   target="_blank")])
#
# markdown_compos = dcc.Markdown('''
# NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**.''')
#
# markdown_iso = dcc.Markdown('''
# NOTE: Uncheck the box will **NOT RESET** this table if you have edited it, but the input will not be used in the
# calculations.''')

# # Plot control buttons
# plot_option_div = html.Div(
#     [
#         html.Hr(),
#         html.H3('Result'),
#         html.H5('Plot:'),
#         html.Div(
#             [
#                 html.Div(
#                     [
#                         html.P('X options: '),
#                         dcc.RadioItems(id='x_type',
#                                        options=[
#                                            {'label': 'Energy (eV)', 'value': 'energy'},
#                                            {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
#                                            {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
#                                        ],
#                                        value='energy',
#                                        # n_clicks_timestamp=0,
#                                        )
#                     ], className=col_width_3
#                 ),
#                 html.Div(
#                     [
#                         html.P('Y options: '),
#                         dcc.RadioItems(id='y_type',
#                                        options=[
#                                            {'label': 'Transmission', 'value': 'transmission'},
#                                            {'label': 'Attenuation', 'value': 'attenuation'},
#                                            {'label': 'Attenuation coefficient', 'value': 'mu_per_cm'},
#                                            {'label': "Cross-section (weighted)", 'value': 'sigma'},
#                                            {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
#                                        ],
#                                        value='transmission',
#                                        # n_clicks_timestamp=0,
#                                        )
#                     ], className=col_width_3
#                 ),
#                 html.Div(
#                     [
#                         html.P('Scale options: '),
#                         dcc.RadioItems(id='plot_scale',
#                                        options=[
#                                            {'label': 'Linear', 'value': 'linear'},
#                                            {'label': 'Log x', 'value': 'logx'},
#                                            {'label': 'Log y', 'value': 'logy'},
#                                            {'label': 'Loglog', 'value': 'loglog'},
#                                        ],
#                                        value='linear',
#                                        # n_clicks_timestamp=0,
#                                        )
#                     ], className=col_width_3
#                 ),
#                 html.Div(
#                     [
#                         html.P('Show options: '),
#                         dcc.Checklist(id='show_opt',
#                                       options=[
#                                           {'label': 'Total', 'value': 'total'},
#                                           {'label': 'Layer', 'value': 'layer'},
#                                           {'label': 'Element', 'value': 'ele'},
#                                           {'label': 'Isotope', 'value': 'iso'},
#                                       ],
#                                       value=['layer'],
#                                       # n_clicks_timestamp=0,
#                                       ),
#                     ], className=col_width_3
#                 ),
#             ], className='row'
#         ),
#     ]
# ),