import pandas as pd
import os
from scipy.interpolate import interp1d
import numpy as np
from dash import dash_table as dt
import io
import json
import base64
from datetime import datetime
from bem import xscalc, matter
from bem import xtaloriprobmodel as xopm

import ImagingReso._utilities as ir_util
from ImagingReso.resonance import Resonance

from callbacks.utilities.constants import *
from callbacks.utilities.initialization import (iso_tb_df_default,
                                                output_stack_header_df_wave,
                                                output_stack_header_df,
                                                output_stack_header_short_df,
                                                output_tb_uneven_6_col)
from callbacks.utilities.validator import is_number

sample_header_df = pd.DataFrame({
    'name': [chem_name,
             thick_name,
             density_name],
    'id': [chem_name,
           thick_name,
           density_name],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric', 'any']
})

bragg_sample_header_df = pd.DataFrame({
    'name': [chem_name,
             index_number_h,
             index_number_k,
             index_number_l,
             ],
    'id': [chem_name,
             index_number_h,
             index_number_k,
             index_number_l,
           ],
    'type': ['text', 'numeric', 'numeric', 'numeric',
            ],
    })

bragg_texture_header_df = pd.DataFrame({
    'name': [index_number_h,
             index_number_k,
             index_number_l,
             r,
             beta],
    'id': [index_number_h,
           index_number_k,
           index_number_l,
           r,
           beta],
    'type': ['numeric', 'numeric', 'numeric', 'numeric', 'numeric'],
    })

iso_dict_schema = {
    # layer_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    layer_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    ele_name: {'type': 'string', 'empty': False, 'required': True, },
    iso_name: {'type': 'string', 'empty': False, 'required': True, },
    iso_ratio_name: {'type': 'number', 'min': 0, 'max': 1, 'required': True, 'between_zero_and_one': True, },
}

sample_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    thick_name: {'type': 'number', 'min': 0, 'required': True, },
    density_name: {'anyof_type': ['string', 'number'], 'min': 0, 'empty_str': True, },
}


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


def x_type_to_x_tag(x_type):
    # Determine X names to plot
    if x_type == 'energy':
        x_tag = energy_name
    elif x_type == 'lambda':
        x_tag = wave_name
    else:
        x_tag = tof_name
    return x_tag


def create_sample_df_from_compos_df(compos_tb_df):
    _compos_tb_df = compos_tb_df[:]
    sample_df = pd.DataFrame()
    sample_df[chem_name] = _compos_tb_df[chem_name]
    sample_df[thick_name] = 1
    sample_df[density_name] = ''
    return sample_df


def unpack_sample_tb_df_and_add_layer(o_reso, sample_tb_df):
    num_layer = len(sample_tb_df[chem_name])
    for layer_index in range(num_layer):
        if density_name not in sample_tb_df.columns:  # sample density name is NOT in the tb
            if thick_name not in sample_tb_df.columns:  # for compos_df, only have column "compos_2nd_col_id"
                try:
                    o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                     thickness=1)  # dummy layer to generate the stack
                except ValueError:
                    pass
            else:  # sample thickness is in the tb
                try:
                    o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                     thickness=float(sample_tb_df[thick_name][layer_index]))
                except ValueError:
                    pass
        elif sample_tb_df[density_name][layer_index] == '':  # sample density name is in the tb
            try:  # sample density is NOT in the tb
                o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                 thickness=float(sample_tb_df[thick_name][layer_index]))
            except ValueError:
                pass
        else:  # sample density is in the tb
            try:
                o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                 thickness=float(sample_tb_df[thick_name][layer_index]),
                                 density=float(sample_tb_df[density_name][layer_index]))
            except ValueError:
                pass
    return o_reso


def form_iso_table(sample_df: pd.DataFrame, database: str):
    o_reso = Resonance(energy_min=1, energy_max=2, energy_step=1, database=database)
    o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=sample_df)
    layer_list = list(o_reso.stack.keys())
    lay_list = []
    ele_list = []
    iso_list = []
    iso_ratio_list = []
    for each_layer in layer_list:
        current_ele_list = o_reso.stack[each_layer]['elements']
        for each_ele in current_ele_list:
            current_iso_list = o_reso.stack[each_layer][each_ele]['isotopes']['list']
            current_iso_ratio_list = o_reso.stack[each_layer][each_ele]['isotopes']['isotopic_ratio']
            for i, each_iso in enumerate(current_iso_list):
                lay_list.append(each_layer)
                ele_list.append(each_ele)
                iso_list.append(each_iso)
                iso_ratio_list.append(round(current_iso_ratio_list[i], 4))

    _df = pd.DataFrame({
        layer_name: lay_list,
        ele_name: ele_list,
        iso_name: iso_list,
        iso_ratio_name: iso_ratio_list,
    })
    return _df


def update_iso_table_callback(sample_tb_rows, prev_iso_tb_rows, database):
    compos_tb_df = pd.DataFrame(sample_tb_rows)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_rows)
    try:
        sample_df = create_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
        new_iso_df = form_iso_table(sample_df=sample_df, database=database)
        new_iso_df = _update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
        try:
            return new_iso_df.to_dict('records')
        except AttributeError:
            return iso_tb_df_default.to_dict('records')
    except KeyError:
        return iso_tb_df_default.to_dict('records')


def force_dict_to_numeric(input_dict_list: list):
    input_df = pd.DataFrame(input_dict_list)
    input_dict = input_df.to_dict('list')
    keys = input_dict.keys()
    output_dict = {}
    for each_key in keys:
        _current_list = input_dict[each_key]
        _current_output_list = []
        for each_item in _current_list:
            if is_number(each_item):
                _current_output_list.append(float(each_item))
            else:
                _current_output_list.append(each_item)
        output_dict[each_key] = _current_output_list
    return output_dict


def form_transmission_result_div(sample_tb_rows, iso_tb_rows, iso_changed, database,
                                 beamline, band_min, band_max, band_type):
    disclaimer = markdown_disclaimer_sns
    if beamline == 'snap':
        beamline_name = 'SNAP (BL-3), SNS'
    elif beamline == 'venus':
        beamline_name = 'VENUS (BL-10), SNS'
    elif beamline == 'imaging_crop':
        beamline_name = u'IMAGING (CG-1D) \u2264 5.35 \u212B, HFIR'
        disclaimer = markdown_disclaimer_hfir
    else:  # beamline == 'imaging':
        beamline_name = 'IMAGING (CG-1D), HFIR'
        disclaimer = markdown_disclaimer_hfir
    # Modify input for testing
    sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
    sample_tb_df = pd.DataFrame(sample_tb_dict)
    if len(iso_changed) == 1:
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        iso_tb_df = pd.DataFrame(iso_tb_dict)
    else:
        iso_tb_df = form_iso_table(sample_df=sample_tb_df, database=database)

    # Calculation starts
    total_trans_at_peak, total_trans, o_stack = calculate_transmission(sample_tb_df=sample_tb_df,
                                                                       iso_tb_df=iso_tb_df,
                                                                       iso_changed=iso_changed,
                                                                       beamline=beamline,
                                                                       band_min=band_min,
                                                                       band_max=band_max,
                                                                       band_type=band_type,
                                                                       database=database)
    output_div_list = [
        html.Hr(),
        html.H3('Result at ' + beamline_name),
        html.P('Transmission (total): {} %'.format(round(total_trans, 3))),
        html.P('Attenuation (total): {} %'.format(round(100 - total_trans, 3))),
        # html.Div(sample_stack_div_list),
    ]
    if beamline in ['imaging', 'imaging_crop']:
        output_div_list.append(
            html.P(u'Transmission (at {} \u212B): {} %'.format(peak_wave[beamline], round(total_trans_at_peak, 3))))
        output_div_list.append(html.P(
            u'Attenuation (at {} \u212B): {} %'.format(peak_wave[beamline], round(100 - total_trans_at_peak, 3))))
    output_div_list.append(disclaimer)
    return output_div_list, o_stack


def calculate_transmission(sample_tb_df, iso_tb_df, iso_changed, beamline, band_min, band_max, band_type, database):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = {'imaging': 'static/instrument_file/beam_flux_cg1d.txt',
                           'imaging_crop': 'static/instrument_file/beam_flux_cg1d_crop.txt',
                           'snap': 'static/instrument_file/beam_flux_snap.txt',
                           # 'venus': 'static/instrument_file/beam_flux_venus.txt',
                           }
    df_flux_raw = _load_beam_shape(_path_to_beam_shape[beamline])
    if beamline in ['imaging', 'imaging_crop']:
        e_min = df_flux_raw['energy_eV'].min()
        e_max = df_flux_raw['energy_eV'].max()
    else:
        if band_type == 'lambda':
            e_min = round(ir_util.angstroms_to_ev(band_max), 6)
            e_max = round(ir_util.angstroms_to_ev(band_min), 6)
        else:  # band_type == 'energy'
            e_min = band_min
            e_max = band_max

    e_step = (e_max - e_min) / (100 - 1)
    __o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step, database=database)
    _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=sample_tb_df)
    o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)
    o_stack = o_reso.stack

    # interpolate with the beam shape energy
    energy = o_reso.total_signal['energy_eV'].round(6)  # !!!need to fix ImagingReso energy_eV columns
    interp_type = 'cubic'
    interp_flux_function = interp1d(x=df_flux_raw['energy_eV'], y=df_flux_raw['flux'], kind=interp_type)
    flux_interp = interp_flux_function(energy)
    df_flux_interp = pd.DataFrame()
    df_flux_interp['energy_eV'] = energy
    df_flux_interp['flux'] = flux_interp
    df_flux = df_flux_interp[:]
    trans_tag = 'transmission'
    mu_tag = 'mu_per_cm'
    trans_at_peak_tag = trans_tag + '_peak'
    mu_at_peak_tag = mu_tag + '_peak'

    o_signal = o_reso.stack_signal
    _total_trans = _calculate_transmission(flux_df=df_flux, trans_array=o_reso.total_signal[trans_tag])

    if beamline in ['imaging', 'imaging_crop']:
        wave = ir_util.ev_to_angstroms(energy).round(2)
        peak_neutron_idx = np.where(wave == peak_wave[beamline])[0][0]
        _peak = wave[peak_neutron_idx]
        _total_trans_at_peak = round(o_reso.total_signal[trans_tag][peak_neutron_idx] * 100, 6)
    else:
        _total_trans_at_peak = ''

    for each_layer in o_stack.keys():
        _current_layer_thickness = o_stack[each_layer]['thickness']['value']
        if len(o_stack.keys()) == 1:
            _current_layer_trans = _total_trans
            if beamline in ['imaging', 'imaging_crop']:
                _current_layer_trans_at_peak = _total_trans_at_peak
        else:
            _current_layer_trans = _calculate_transmission(flux_df=df_flux,
                                                           trans_array=o_signal[each_layer][trans_tag])
            if beamline in ['imaging', 'imaging_crop']:
                _current_layer_trans_at_peak = o_signal[each_layer][trans_tag][peak_neutron_idx]
        o_stack[each_layer][trans_tag] = _current_layer_trans
        o_stack[each_layer][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_layer_trans,
                                                                 thickness=_current_layer_thickness)
        if beamline in ['imaging', 'imaging_crop']:
            o_stack[each_layer][trans_at_peak_tag] = _current_layer_trans_at_peak
            o_stack[each_layer][mu_at_peak_tag] = _transmission_to_mu_per_cm(
                transmission=_current_layer_trans_at_peak,
                thickness=_current_layer_thickness)
        for each_ele in o_stack[each_layer]['elements']:
            _current_ele_trans = _calculate_transmission(flux_df=df_flux,
                                                         trans_array=o_signal[each_layer][each_ele][trans_tag])
            o_stack[each_layer][each_ele][trans_tag] = _current_ele_trans
            o_stack[each_layer][each_ele][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_ele_trans,
                                                                               thickness=_current_layer_thickness)
            if beamline in ['imaging', 'imaging_crop']:
                _current_ele_trans_at_peak = round(o_signal[each_layer][each_ele][trans_tag][peak_neutron_idx] * 100, 6)
                o_stack[each_layer][each_ele][trans_at_peak_tag] = _current_ele_trans_at_peak
                o_stack[each_layer][each_ele][mu_at_peak_tag] = _transmission_to_mu_per_cm(
                    transmission=_current_ele_trans_at_peak,
                    thickness=_current_layer_thickness)
    return _total_trans_at_peak, _total_trans, o_stack


def unpack_iso_tb_df_and_update(o_reso, iso_tb_df, iso_changed):
    if len(iso_changed) == 0:
        return o_reso
    else:
        layer_list = list(o_reso.stack.keys())
        for each_layer in layer_list:
            element_list = o_reso.stack[each_layer]['elements']
            for each_ele in element_list:
                _ele_ratio_list = []
                for iso_i in range(len(iso_tb_df)):
                    if each_layer == iso_tb_df[layer_name][iso_i] and each_ele == iso_tb_df[ele_name][iso_i]:
                        _ele_ratio_list.append(float(iso_tb_df[iso_ratio_name][iso_i]))
                o_reso.set_isotopic_ratio(compound=each_layer, element=each_ele, list_ratio=_ele_ratio_list)
        return o_reso


def form_sample_stack_table_div(o_stack, beamline, full_stack=True):
    sample_stack_div_list = [html.Hr(), html.H4('Sample stack:')]
    layers = list(o_stack.keys())
    layer_dict = {}

    # For short sample stack output
    if full_stack:
        if beamline in ['imaging', 'imaging_crop']:
            output_header_df = output_stack_header_df_wave
        else:
            output_header_df = output_stack_header_df
    else:
        output_header_df = output_stack_header_short_df

    for l_num, layer in enumerate(layers):
        elements_in_current_layer = o_stack[layer]['elements']
        l_str = str(l_num + 1)
        current_layer_list = [
            html.H5("Layer {}: {}".format(l_str, layer)),
        ]
        layer_dict[thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[density_name] = round(o_stack[layer]['density']['value'], 3)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[ratio_name] = ":".join(_ratio_str_list)
        layer_dict[molar_name] = round(o_stack[layer]['molar_mass']['value'], 4)
        layer_dict[number_density_name] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'])
        layer_dict[mu_per_cm_name] = round(o_stack[layer]['mu_per_cm'], 4)
        if beamline in ['imaging', 'imaging_crop']:
            layer_dict[mu_per_cm_at_peak_name] = round(o_stack[layer]['mu_per_cm_peak'], 4)

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
            name_list.append(molar_name)
            molar_name_id = 'column_' + str(_i + 1)
            id_list.append(molar_name_id)
            deletable_list.append(False)
            editable_list.append(False)
            iso_dict[molar_name_id] = round(o_stack[layer][ele]['molar_mass']['value'], 4)

            # For short sample stack output
            if full_stack:
                name_list.append(number_density_name)
                number_density_name_id = 'column_' + str(_i + 2)
                id_list.append(number_density_name_id)
                deletable_list.append(False)
                editable_list.append(False)
                iso_dict[number_density_name_id] = '{:0.3e}'.format(o_stack[layer][ele]['atoms_per_cm3'])

                name_list.append(mu_per_cm_name)
                mu_per_cm_name_id = 'column_' + str(_i + 3)
                id_list.append(mu_per_cm_name_id)
                deletable_list.append(False)
                editable_list.append(False)
                iso_dict[mu_per_cm_name_id] = round(o_stack[layer][ele]['mu_per_cm'], 4)

                if beamline in ['imaging', 'imaging_crop']:
                    # Add mu_per_cm_at_peak
                    name_list.append(mu_per_cm_at_peak_name)
                    mu_per_cm_at_peak_id = 'column_' + str(_i + 4)
                    id_list.append(mu_per_cm_at_peak_id)
                    deletable_list.append(False)
                    editable_list.append(False)
                    iso_dict[mu_per_cm_at_peak_id] = round(o_stack[layer][ele]['mu_per_cm_peak'], 4)

                    cell_conditional = [
                        {'if': {'column_id': molar_name_id},
                         'width': '11%'},
                        {'if': {'column_id': number_density_name_id},
                         'width': '11%'},
                        {'if': {'column_id': mu_per_cm_name_id},
                         'width': '11%'},
                        {'if': {'column_id': mu_per_cm_at_peak_id},
                         'width': '11%'},
                    ]
                else:
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


def update_rows_util(n_add, n_del, list_of_contents, upload_time, prev_upload_time, list_of_names, rows, columns):
    error_message = None
    if upload_time != prev_upload_time:
        if list_of_contents is not None:
            _rows = []
            for c, n in zip(list_of_contents, list_of_names):
                current_rows, error_message = _parse_contents_to_rows(c, n, rows)
                _rows.extend(current_rows)
            rows = _rows
    else:
        rows = _add_del_rows(n_add=n_add, n_del=n_del, rows=rows, columns=columns)
    return rows, error_message, upload_time


def _add_del_rows(n_add, n_del, rows, columns):
    if n_add > n_del:
        rows.append({c['id']: '' for c in columns})
    elif n_add < n_del:
        if len(rows) > 1:
            rows = rows[:-1]
    else:
        rows = rows[:]
    return rows


def _parse_contents_to_rows(contents, filename, rows):
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
            df = df[df[chem_name] != '']
            rows = df.to_dict('records')

    return rows, div


def _calculate_transmission(flux_df: pd.DataFrame, trans_array: np.array):
    # calculated transmitted flux
    trans_flux = trans_array * flux_df['flux']
    integr_total = np.trapz(y=flux_df['flux'] / flux_df['energy_eV'], x=flux_df['energy_eV'], dx=1e-6).round(3)
    integr_trans = np.trapz(y=trans_flux / flux_df['energy_eV'], x=flux_df['energy_eV'], dx=1e-6).round(3)
    _trans = integr_trans / integr_total * 100
    return _trans


def _transmission_to_mu_per_cm(transmission, thickness):
    mu_per_cm = -np.log(transmission / 100) / (thickness / 10)
    return mu_per_cm


def _load_beam_shape(relative_path_to_beam_shape):
    # Load beam shape from static
    df = pd.read_csv(relative_path_to_beam_shape, sep='\t', skiprows=0)
    df.columns = ['wavelength_A', 'flux']
    # Get rid of crazy data
    df.drop(df[df.wavelength_A < 0].index, inplace=True)
    df.drop(df[df.flux <= 0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Convert wavelength to energy
    energy_array = ir_util.angstroms_to_ev(df['wavelength_A'])
    df.insert(1, 'energy_eV', round(energy_array, 6))
    # df.insert(1, 'energy_eV', energy_array)
    return df


def _update_new_iso_table(prev_iso_df: pd.DataFrame, new_iso_df: pd.DataFrame):
    prev_iso_layer_list = list(prev_iso_df[layer_name])  # previous list of layers
    new_iso_layer_list = list(new_iso_df[layer_name])  # new list of layers

    prev_index = []  # index of the new layers that exists in prev layers
    new_index = []  # index of the prev layers that needs to be passed along
    for line_idx, each_new_layer in enumerate(new_iso_layer_list):
        if each_new_layer in prev_iso_layer_list:
            new_index.append(line_idx)
    for line_idx, each_prev_layer in enumerate(prev_iso_layer_list):
        if each_prev_layer in new_iso_layer_list:
            prev_index.append(line_idx)

    if len(prev_index) != 0:
        for idx, each in enumerate(new_index):
            new_iso_df.iloc[each] = prev_iso_df.loc[prev_index[idx]]

    return new_iso_df


def load_dfs(jsonified_data):
    datasets = _load_jsonified_data(jsonified_data=jsonified_data)
    df_dict = _extract_df(datasets=datasets)
    return df_dict


def _load_jsonified_data(jsonified_data):
    datasets = json.loads(jsonified_data)
    return datasets


def _extract_df(datasets):
    df_name_list = ['x', 'y']
    df_dict = {}
    for each_name in df_name_list:
        df_dict[each_name] = pd.read_json(datasets[each_name], orient='split')
    return df_dict


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


def clean_data_tab(data_tab=None):
    '''
    remove all the rows with no chemical formula defined
    '''
    data_tab_cleaned = []
    if not data_tab:
        return data_tab_cleaned

    for _entry in data_tab:
        if _entry[chem_name] == '':
            continue
        else:
            data_tab_cleaned.append(_entry)
    return data_tab_cleaned


def clean_texture_data(data=None):
    '''
    remove all rows with missing r or missing beta
    '''
    data_cleaned = []
    if not data:
        return data_cleaned

    for _entry in data:
        if _entry[index_number_h] == '':
            continue

        if _entry[index_number_k] == '':
            continue

        if _entry[index_number_l] == '':
            continue

        if (_entry[r] == '') and (_entry[beta] == ''):
            continue

        data_cleaned.append(_entry)

    return data_cleaned


def boolean_value_of_texture_checklist_to_flag(data=None, flag=None):
    '''
    convert a DASH flag value into a boolean
    '''
    if data == []:
        return False

    elif len(flag) == 1:
        return False

    return True


def boolean_value_of_grain_size_checklist_to_flag(flag=None):
    '''
    convert dash checklist value into boolean
    '''
    if len(flag) == 1:
        return False

    return True


def update_xs_dict(xs_dict=None,
                   data_tab=None,
                   a=None, b=None, c=None,
                   alpha=None, beta=None, gamma=None,
                   temperature=None,
                   log_label='tab2',
                   wavelengths_A=None,
                   texture_flag=False,
                   texture_data=None,
                   grain_size_flag=False,
                   grain_size=None):
    '''
    calculating the structure for the given data_tab
    '''
    print(f"No errors found in {log_label}, working with {log_label}:")

    if not data_tab:
        print(f"- data_tab is empty!")
        return

    print(f"{texture_flag =}")
    print(f"{texture_data =}")
    print(f"{grain_size_flag = }")
    print(f"{grain_size =}")

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
    # try:

    print(f"{type(grain_size) =}")

    if texture_flag:

        print(f" with texture flag")

        texture_model = xopm.MarchDollase()
        for _row in texture_data:

            print(f"{_row =}")
            h = _row[index_number_h]
            k = _row[index_number_k]
            l = _row[index_number_l]

            if _row[r]:
                texture_model.r[(h, k, l)] = _row[r]

            if _row['beta']:
                texture_model.r[(h, k, l)] = _row['beta']

        if grain_size_flag:
            print(f" with grain size")
            print(f"-> {grain_size =}")
            _xscalculator = xscalc.XSCalculator(_structure, temperature,
                                                texture_model,
                                                # max_diffraction_index=4,
                                                size=grain_size)

        else:
            print(f" no grain size")
            _xscalculator = xscalc.XSCalculator(_structure, temperature,
                                                texture_model,
                                                max_diffraction_index=4)

    elif grain_size_flag:
        print(f" with grain size and no texture")
        _xscalculator = xscalc.XSCalculator(_structure, temperature,
                                            # max_diffraction_index=4,
                                            size=grain_size)

    else:
        print(f" no grain size or texture")
        _xscalculator = xscalc.XSCalculator(_structure, temperature,
                                            max_diffraction_index=4)

    # except AttributeError as msg:
    #     return msg

    xs_dict[_name_only + ' (total)'] = [np.real(_value) for _value in _xscalculator.xs(wavelengths_A)]
    xs_dict[_name_only + ' (abs)'] = [np.real(_value) for _value in _xscalculator.xs_abs(wavelengths_A)]
    xs_dict[_name_only + ' (coh el)'] = _xscalculator.xs_coh_el(wavelengths_A)
    xs_dict[_name_only + ' (inc el)'] = _xscalculator.xs_inc_el(wavelengths_A)
    xs_dict[_name_only + ' (coh inel)'] = _xscalculator.xs_coh_inel(wavelengths_A)
    xs_dict[_name_only + ' (inc inel)'] = _xscalculator.xs_inc_inel(wavelengths_A)
    print("- Calculation done!")

    return None


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