import pandas as pd
import os
from scipy.interpolate import interp1d
import numpy as np
from dash import dash_table as dt

import ImagingReso._utilities as ir_util
from ImagingReso.resonance import Resonance

from callbacks.utilities.constants import *
from callbacks.utilities.initialization import (iso_tb_df_default, output_stack_header_df,
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


def update_new_iso_table(prev_iso_df: pd.DataFrame, new_iso_df: pd.DataFrame):
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


def update_iso_table_callback(sample_tb_rows, prev_iso_tb_rows, database):
    compos_tb_df = pd.DataFrame(sample_tb_rows)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_rows)
    try:
        sample_df = create_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
        new_iso_df = form_iso_table(sample_df=sample_df, database=database)
        new_iso_df = update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
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
    total_trans, o_stack = calculate_transmission(sample_tb_df=sample_tb_df,
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
        disclaimer,
        # html.Div(sample_stack_div_list),
    ]
    return output_div_list, o_stack


def load_beam_shape(relative_path_to_beam_shape):
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


def calculate_transmission(sample_tb_df, iso_tb_df, iso_changed, beamline, band_min, band_max, band_type, database):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = {'imaging': 'static/instrument_file/beam_flux_cg1d.txt',
                           'imaging_crop': 'static/instrument_file/beam_flux_cg1d_crop.txt',
                           'snap': 'static/instrument_file/beam_flux_snap.txt',
                           # 'venus': 'static/instrument_file/beam_flux_venus.txt',
                           }
    df_flux_raw = load_beam_shape(_path_to_beam_shape[beamline])
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
    o_signal = o_reso.stack_signal

    _total_trans = _calculate_transmission(flux_df=df_flux, trans_array=o_reso.total_signal[trans_tag])

    for each_layer in o_stack.keys():
        _current_layer_thickness = o_stack[each_layer]['thickness']['value']
        if len(o_stack.keys()) == 1:
            _current_layer_trans = _total_trans
        else:
            _current_layer_trans = _calculate_transmission(flux_df=df_flux,
                                                           trans_array=o_signal[each_layer][trans_tag])
        o_stack[each_layer][trans_tag] = _current_layer_trans
        o_stack[each_layer][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_layer_trans,
                                                                 thickness=_current_layer_thickness)
        for each_ele in o_stack[each_layer]['elements']:
            _current_ele_trans = _calculate_transmission(flux_df=df_flux,
                                                         trans_array=o_signal[each_layer][each_ele][trans_tag])
            o_stack[each_layer][each_ele][trans_tag] = _current_ele_trans
            o_stack[each_layer][each_ele][mu_tag] = _transmission_to_mu_per_cm(transmission=_current_ele_trans,
                                                                               thickness=_current_layer_thickness)
    return _total_trans, o_stack


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
        layer_dict[thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[density_name] = round(o_stack[layer]['density']['value'], 3)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[ratio_name] = ":".join(_ratio_str_list)
        layer_dict[molar_name] = round(o_stack[layer]['molar_mass']['value'], 4)
        layer_dict[number_density_name] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'])
        layer_dict[mu_per_cm_name] = '{:0.3e}'.format(o_stack[layer]['mu_per_cm'])

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
                name_list.append(mu_per_cm_name)
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