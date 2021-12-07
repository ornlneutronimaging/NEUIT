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
from cerberus import Validator
import plotly.tools as tls

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser

import ImagingReso._utilities as ir_util
from ImagingReso.resonance import Resonance

from config import app_dict
from callbacks.utilities.validator import MyValidator, is_number, validate_input

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
number_name = 'Image index (#)'
class_name = 'Neutron classification'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ratio_name = 'Stoichiometric ratio'
molar_name = 'Molar mass (g/mol)'
number_density_name = 'Atoms (#/cm\u00B3)'
mu_per_cm_name = 'Attenu. co. (/cm)'
layer_name = 'Layer'
ele_name = 'Element'
iso_name = 'Isotope'
iso_ratio_name = 'Isotopic ratio'
weight_name = 'Weight (g)'
weight_name_p = 'Weight %'
atomic_name = 'Atoms (mol)'
atomic_name_p = 'Atomic %'
compos_2nd_col_id = '2nd_input_column'


energy_range_header_df = pd.DataFrame({
    'name': [energy_name, wave_name, speed_name, tof_name, class_name],
    'id': [energy_name, wave_name, speed_name, tof_name, class_name],
    'deletable': [False, False, False, False, False],
    'editable': [True, True, False, False, False],
    'type': ['numeric', 'numeric', 'any', 'any', 'any']
})

sample_header_df = pd.DataFrame({
    'name': [chem_name, thick_name, density_name],
    'id': [chem_name, thick_name, density_name],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric', 'any']
})

compos_header_df = pd.DataFrame({
    'name': [chem_name, weight_name],
    'id': [chem_name, compos_2nd_col_id],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric']
})

compos_header_percent_df = pd.DataFrame({
    'name': [chem_name, weight_name_p, atomic_name_p],
    'id': [chem_name, weight_name_p, atomic_name_p],
    # 'deletable': [False, False, False],
    'editable': [False, False, False],
})

iso_tb_header_df = pd.DataFrame({
    'name': [layer_name, ele_name, iso_name, iso_ratio_name],
    'id': [layer_name, ele_name, iso_name, iso_ratio_name],
    'deletable': [False, False, False, False],
    'editable': [False, False, False, True],
    'type': ['any', 'any', 'any', 'numeric']
})

iso_tb_df_default = pd.DataFrame({
    layer_name: [None],
    ele_name: [None],
    iso_name: [None],
    iso_ratio_name: [None],
})

output_stack_header_df = pd.DataFrame({
    'name': [thick_name, density_name, ratio_name, molar_name, number_density_name, mu_per_cm_name],
    'id': [thick_name, density_name, ratio_name, molar_name, number_density_name, mu_per_cm_name],
    'deletable': [False, False, False, False, False, False],
    'editable': [False, False, False, False, False, False],
})

output_stack_header_short_df = pd.DataFrame({
    'name': [ratio_name, molar_name],
    'id': [ratio_name, molar_name],
    'deletable': [False, False],
    'editable': [False, False],
})

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
    chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    compos_2nd_col_id: {'type': 'number', 'greater_than_zero': True},
}

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


def classify_neutron(energy_ev):
    assert energy_ev >= 0
    e = energy_ev
    if 0 < e <= 2.5e-7:
        return 'Ultra-cold'
    elif 2.5e-7 < e < 0.025:
        return 'Cold'
    elif 0.025 <= e <= 0.2:
        return 'Thermal'
    elif 0.2 < e < 900:
        return 'Epithermal'
    elif 900 < e <= 0.5e6:
        return 'Intermediate'
    elif 0.5e6 < e <= 20e6:
        return 'Fast'
    elif 20e6 < e:
        return 'Ultra-fast'


def fill_range_table_by_e(e_ev, distance_m):
    _e = e_ev
    _lambda = round(ir_util.ev_to_angstroms(array=_e), 5)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {energy_name: _e,
            wave_name: _lambda,
            speed_name: _v,
            tof_name: _tof,
            class_name: _class}


def fill_range_table_by_wave(wave_angstroms, distance_m):
    _lambda = wave_angstroms
    _e = round(ir_util.angstroms_to_ev(array=_lambda), 5)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {energy_name: _e,
            wave_name: _lambda,
            speed_name: _v,
            tof_name: _tof,
            class_name: _class}


def creat_sample_df_from_compos_df(compos_tb_df):
    _compos_tb_df = compos_tb_df[:]
    sample_df = pd.DataFrame()
    sample_df[chem_name] = _compos_tb_df[chem_name]
    sample_df[thick_name] = 1
    sample_df[density_name] = ''
    return sample_df


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


def update_database_key_in_schema(schema, database):
    _new_key = database
    try:
        _old_key = list(schema[chem_name].keys())[3]
        if _new_key is not _old_key:
            schema[chem_name][_new_key] = schema[chem_name].pop(_old_key)
        return schema
    except KeyError:
        _old_key = list(schema[layer_name].keys())[3]
        if _new_key is not _old_key:
            schema[layer_name][_new_key] = schema[layer_name].pop(_old_key)
        return schema


def validate_sample_input(sample_df: pd.DataFrame, sample_schema: dict, database: str):
    # Test sample input format
    sample_schema = update_database_key_in_schema(schema=sample_schema, database=database)
    test_passed_list, output_div_list = validate_input_tb_rows(schema=sample_schema, input_df=sample_df)

    # Test no duplicate layer name
    if all(test_passed_list):
        duplicate_test_passed, duplicate_test_output_div = validate_no_duplicated_layer_name(sample_df=sample_df)
        test_passed_list += duplicate_test_passed
        output_div_list += duplicate_test_output_div

    return test_passed_list, output_div_list


def validate_no_duplicated_layer_name(sample_df: pd.DataFrame):
    """ Returns True when no duplicated layer name. """
    try:
        layer_list = sample_df[chem_name].tolist()
        if len(layer_list) == len(set(layer_list)):
            return [True], [None]
        else:
            return [False], [html.P("INPUT ERROR: same '{}' has been entered more than once.".format(chem_name))]
    except KeyError as error_massage:
        return [False], [error_massage.__str__()]


def validate_iso_input(iso_df: pd.DataFrame, iso_schema: dict, database: str,
                       test_passed_list: list, output_div_list: list):
    # Test iso input format
    iso_schema = update_database_key_in_schema(schema=iso_schema, database=database)
    iso_test_passed_list, iso_output_div_list = validate_input_tb_rows(schema=iso_schema, input_df=iso_df)
    test_passed_list += iso_test_passed_list
    output_div_list += iso_output_div_list
    # Test the sum of iso ratio == 1
    if all(test_passed_list):
        sum_test_passed, sum_test_output_div = validate_sum_of_iso_ratio(iso_df=iso_df)
        test_passed_list += sum_test_passed
        output_div_list += sum_test_output_div

    return test_passed_list, output_div_list


def validate_sum_of_iso_ratio(iso_df: pd.DataFrame):
    try:
        df = iso_df.groupby([layer_name, ele_name]).sum()
        df_boo = df[iso_ratio_name] - 1.0
        boo = df_boo.abs() >= 0.005
        failed_list = list(boo)
        passed_list = []
        div_list = []
        if any(failed_list):
            _list = df.index[boo].tolist()
            for _index, each_fail_layer in enumerate(_list):
                div = html.P("INPUT ERROR: '{}': [sum of isotopic ratios is '{}' not '1']".format(
                    str(each_fail_layer), float(df[boo][iso_ratio_name][_index])))
                passed_list.append(False)
                div_list.append(div)
        else:
            passed_list.append(True)
            div_list.append(None)
        return passed_list, div_list
    except KeyError:
        return [False], [None]


def validate_density_input(sample_tb_df: pd.DataFrame, test_passed_list: list, output_div_list: list):
    # Test density input required or not
    for _index, _each_formula in enumerate(sample_tb_df[chem_name]):
        try:
            _parsed_dict = ir_util.formula_to_dictionary(_each_formula)
            _num_of_ele_in_formula = len(_parsed_dict[_each_formula]['elements'])
            if _num_of_ele_in_formula > 1 and sample_tb_df[density_name][_index] == '':
                test_passed_list.append(False)
                output_div_list.append(
                    html.P("INPUT ERROR: '{}': ['Density input is required for compound '{}'.']".format(density_name,
                                                                                                        _each_formula)))
            else:
                test_passed_list.append(True)
                output_div_list.append(None)
        except ValueError:
            test_passed_list = test_passed_list
            output_div_list = output_div_list

    return test_passed_list, output_div_list


def validate_energy_input(range_tb_df: pd.DataFrame, test_passed_list: list, output_div_list: list):
    # Test range table
    if range_tb_df[energy_name][0] == range_tb_df[energy_name][1]:
        test_passed_list.append(False)
        output_div_list.append(
            html.P("INPUT ERROR: {}: ['Energy min. can not equal energy max.']".format(str(energy_name))))
    else:
        test_passed_list.append(True)
        output_div_list.append(None)

    for each in range_tb_df[energy_name]:
        if each < 1e-5 or each > 1e8:
            test_passed_list.append(False)
            output_div_list.append(
                html.P("INPUT ERROR: '{}': ['1x10^-5 <= 'Energy' <= 1x10^8']".format(str(energy_name))))
        else:
            test_passed_list.append(True)
            output_div_list.append(None)
    return test_passed_list, output_div_list


def validate_band_width_input(beamline, band_width, band_type, test_passed_list: list, output_div_list: list):
    if beamline in ['imaging', 'imaging_crop']:
        test_passed_list.append(True)
        output_div_list.append(None)
    else:
        if band_width[0] is None:
            test_passed_list.append(False)
            output_div_list.append(
                html.P("INPUT ERROR: '{}': ['Min.' is required!]".format('Band width')))
        if band_width[1] is None:
            test_passed_list.append(False)
            output_div_list.append(
                html.P("INPUT ERROR: '{}': ['Max.' is required!]".format('Band width')))
        if all(test_passed_list):
            # if band_width[0] =  min=2.86E-04, max=9.04E+01,
            if band_width[0] == band_width[1]:
                test_passed_list.append(False)
                output_div_list.append(
                    html.P("INPUT ERROR: '{}': ['Min.' and 'Max.' can not be equal!]".format('Band width')))
            elif band_width[0] > band_width[1]:
                test_passed_list.append(False)
                output_div_list.append(
                    html.P("INPUT ERROR: '{}': ['Min.' < 'Max.' is required!]".format('Band width')))
            else:
                if band_type == 'lambda':
                    if band_width[0] < 2.86E-04 or band_width[0] > 9.04E+01:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{}': ['2.86E-04 \u2264 'Min.' \u2264 9.04E+01' is required!]".format(
                                    'Band width')))
                    if band_width[1] < 2.86E-04 or band_width[1] > 9.04E+01:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{}': ['2.86E-04 \u2264 'Max.' \u2264 9.04E+01' is required!]".format(
                                    'Band width')))
                    _diff = round(band_width[1] - band_width[0], 5)
                    if _diff < 1e-3:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{} - {} = {}': ['Max.' minus 'Min.' >= {} required]".format(
                                    band_width[1],
                                    band_width[0],
                                    _diff,
                                    1e-3)))
                else:
                    if band_width[0] < 1e-5 or band_width[0] > 1e8:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{}': ['1e-5 \u2264 'Min.' \u2264 1e8' is required!]".format(
                                    'Band width')))
                    if band_width[1] < 1e-5 or band_width[1] > 1e8:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{}': ['1e-5 \u2264 'Max.' \u2264 1e8' is required!]".format(
                                    'Band width')))
                    _diff = round(band_width[1] - band_width[0], 7)
                    if _diff < 1e-6:
                        test_passed_list.append(False)
                        output_div_list.append(
                            html.P(
                                "INPUT ERROR: '{} - {} = {}': ['Max.' minus 'Min.' >= {} required]".format(
                                    band_width[1],
                                    band_width[0],
                                    _diff,
                                    1e-6)))
    return test_passed_list, output_div_list


def validate_input_tb_rows(schema: dict, input_df: pd.DataFrame):
    input_dict_list = input_df.to_dict('records')
    v = MyValidator(schema)
    # v = Validator(schema)
    passed_list = []
    div_list = []
    for each_input_dict in input_dict_list:
        passed, div = validate_input(v=v, input_dict=each_input_dict)
        div_list.append(div)
        passed_list.append(passed)
    return passed_list, div_list


# def _validate_input(v: Validator, input_dict: dict):
#     passed = v.validate(input_dict)
#     if passed:
#         return passed, None
#     else:
#         error_message_str = v.errors
#     return passed, html.P('INPUT ERROR: {}'.format(error_message_str))


def update_iso_table_callback(sample_tb_rows, prev_iso_tb_rows, database):
    compos_tb_df = pd.DataFrame(sample_tb_rows)
    prev_iso_tb_df = pd.DataFrame(prev_iso_tb_rows)
    try:
        sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
        new_iso_df = form_iso_table(sample_df=sample_df, database=database)
        new_iso_df = update_new_iso_table(prev_iso_df=prev_iso_tb_df, new_iso_df=new_iso_df)
        try:
            return new_iso_df.to_dict('records')
        except AttributeError:
            return iso_tb_df_default.to_dict('records')
    except KeyError:
        return iso_tb_df_default.to_dict('records')


def init_reso_from_tb(range_tb_df, e_step, database):
    v_1 = range_tb_df[energy_name][0]
    v_2 = range_tb_df[energy_name][1]
    if v_1 < v_2:
        o_reso = Resonance(energy_min=v_1, energy_max=v_2, energy_step=e_step, database=database)
    else:
        o_reso = Resonance(energy_min=v_2, energy_max=v_1, energy_step=e_step, database=database)
    return o_reso


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


def convert_input_to_composition(compos_df, compos_type, o_stack):
    if compos_type == weight_name:
        fill_name = atomic_name_p
        update_name = weight_name_p
    else:
        fill_name = weight_name_p
        update_name = atomic_name_p
    result_list = []
    _ele_list = []
    _mol_list = []
    _input_converted_p_list = []
    _input_sum = compos_df[compos_2nd_col_id].sum()
    for _n, each_chem in enumerate(compos_df[chem_name]):
        _molar_mass = o_stack[each_chem]['molar_mass']['value']
        input_num = compos_df[compos_2nd_col_id][_n]
        _current_ele_list = o_stack[each_chem]['elements']
        _current_ratio_list = o_stack[each_chem]['stoichiometric_ratio']
        _input_percentage = input_num * 100 / _input_sum
        _ele_list += _current_ele_list
        if compos_type == weight_name:  # wt. input (g)
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


def update_range_tb_by_coordinate(range_table_rows, distance, modified_coord):
    row = modified_coord[0]
    col = modified_coord[1]
    if col == 0:
        input_value = range_table_rows[row][energy_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_e(e_ev=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [wave_name, speed_name, tof_name, class_name]:
                range_table_rows[row][each_col] = 'N/A'
    elif col == 1:  # Changed back to 1 from 4 after updating to pandas>=0.25.0
        input_value = range_table_rows[row][wave_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_wave(wave_angstroms=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [energy_name, speed_name, tof_name, class_name]:
                range_table_rows[row][each_col] = 'N/A'

    return range_table_rows


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
        x_tag = energy_name
    elif x_type == 'lambda':
        x_tag = wave_name
    else:
        x_tag = tof_name
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
        x_label = energy_name
    elif x_type == 'lambda':
        x_label = wave_name
    elif x_type == 'time':
        x_label = tof_name
    else:  # x_type == 'number':
        x_label = number_name
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
    df.insert(loc=1, column=tof_name, value=ir_util.ev_to_s(array=df[energy_name],
                                                            source_to_detector_m=distance_m,
                                                            offset_us=0))
    df.insert(loc=1, column=wave_name, value=ir_util.ev_to_angstroms(df[energy_name]))
    df[tof_name] = df[tof_name] * 1e6
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
            df = df[df[chem_name] != '']
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


def init_app_links(current_app, app_dict_all):
    links_div_list = [html.A('Home', href='/', target="_blank")]
    for _each_app in app_dict_all.keys():
        if current_app != _each_app:
            links_div_list.append(html.Br())
            links_div_list.append(html.A(app_dict[_each_app]['name'], href=app_dict[_each_app]['url'], target="_blank"))
    links_div_list.append(html.H1(app_dict[current_app]['name']))
    return html.Div(links_div_list)


def init_app_about(current_app, app_id_dict):
    more_info_check = dcc.Checklist(
        id=app_id_dict['more_about_app_id'],
        options=[
            {'label': 'More about this app \U0001F4AC', 'value': 'more'},
        ],
        value=[],
        labelStyle={'display': 'inline-block'}
    )

    more_info_div = html.Div(
        [
            app_info_markdown_dict[current_app],
        ],
        id=app_id_dict['app_info_id'],
        style={'display': 'none'},
    )

    return html.Div([more_info_check, more_info_div])


app_info_markdown_dict = {
    'transmission': dcc.Markdown("""
    This tool estimates the neutron transmission/attenuation signals and contrast,
    by defining the sample information such as density, thickness in the neutron beam path.
    Multiple samples or complex compounds can be added as layers in such calculation. 
    Estimating the contrast by changing isotopic ratios is also supported.
    An example is shown by default to demonstrate its usage.
            """),
    'resonance': dcc.Markdown("""
    This tool estimates the energy dependent neutron imaging signals and contrasts,
    specifically for *resonances* in the *epithermal* range.
    Similar to the transmission tool, sample/samples can be entered as layers in such calculation. 
    Estimating the contrast by changing isotopic ratios is also supported.
    An example is shown by default to demonstrate its usage.
            """),
    'converter': dcc.Markdown("""
    This tool helps the conversion between wt.% and at.%. And it populates
    an equivalent chemical formula to represent a complex mixture. Such formula
    can be used as '{}' in other tools available in NEUIT.
    An example is shown by default to demonstrate its usage.
            """.format(chem_name)),
    'tof_plotter': dcc.Markdown("""
    This tool helps plotting data acquired from Timepix2 MCP detector. By dragging and dropping
    spectra files and data files, one can quickly verify if expected resonances or Bragg-edges
    have been captured or not. Optional background file can also be added if normalization is needed.  
            """),
    'bragg': dcc.Markdown("""
    This tool estimates the energy dependent neutron imaging signals and contrasts,
    specifically for *Bragg-edges* in the *cold* or *thermal* range. Currently, it only supports
    dragging and dropping '.cif' files.
            """),
}


def init_app_ids(app_name: str):
    id_dict = {}
    id_dict['more_about_app_id'] = app_name + '_more_about_app'
    id_dict['app_info_id'] = app_name + '_app_info'
    id_dict['sample_upload_id'] = app_name + '_sample_upload'
    id_dict['error_upload_id'] = app_name + '_error_upload'
    id_dict['hidden_upload_time_id'] = app_name + '_time_upload'
    id_dict['add_row_id'] = app_name + '_add_row'
    id_dict['del_row_id'] = app_name + '_del_row'
    id_dict['database_id'] = app_name + '_database'
    id_dict['sample_table_id'] = app_name + '_sample_table'
    id_dict['iso_check_id'] = app_name + '_iso_check'
    id_dict['iso_div_id'] = app_name + '_iso_input'
    id_dict['iso_table_id'] = app_name + '_iso_table'
    id_dict['submit_button_id'] = app_name + '_submit'
    id_dict['result_id'] = app_name + '_result'
    id_dict['error_id'] = app_name + '_error'
    id_dict['output_id'] = app_name + '_output'

    if app_name == 'transmission':  # id names for neutron transmission only
        id_dict['beamline_id'] = app_name + '_beamline'
        id_dict['band_div_id'] = app_name + '_band_div'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_type_id'] = app_name + '_band_type'
        id_dict['band_unit_id'] = app_name + '_band_unit'

    elif app_name == 'resonance':  # id names for neutron resonance only
        id_dict['slider_id'] = app_name + '_e_range_slider'
        id_dict['range_table_id'] = app_name + '_range_table'
        id_dict['e_step_id'] = app_name + '_e_step'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['hidden_prev_distance_id'] = app_name + '_hidden_prev_distance'
        id_dict['hidden_range_input_coord_id'] = app_name + '_hidden_range_input_coord'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['plot_options_div_id'] = app_name + '_plot_options'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'
        id_dict['prev_x_type_id'] = app_name + '_prev_x_type'

    elif app_name == 'converter':  # id names for composition converter only
        id_dict['compos_type_id'] = app_name + '_compos_input_type'

    elif app_name == 'tof_plotter':  # id names for TOF plotter only
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['delay_id'] = app_name + '_delay'
        id_dict['spectra_upload_id'] = app_name + '_spectra'
        id_dict['spectra_upload_fb_id'] = app_name + '_spectra_fb'
        id_dict['data_upload_id'] = app_name + '_data'
        id_dict['data_upload_fb_id'] = app_name + '_data_fb'
        id_dict['background_upload_id'] = app_name + '_background'
        id_dict['background_check_id'] = app_name + '_background_ck'
        id_dict['background_upload_fb_id'] = app_name + '_background_fb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'

    elif app_name == 'bragg':  # id names for bragg edge simulator only
        id_dict['error_id2'] = app_name + '_error2'
        id_dict['temperature_id'] = app_name + '_temperature'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_step_id'] = app_name + '_band_step'
        id_dict['band_unit_id'] = app_name + '_band_unit'
        id_dict['cif_upload_id'] = app_name + '_cif'
        id_dict['cif_upload_fb_id'] = app_name + '_cif_fb'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'

    return id_dict


def init_upload_field(id_str: str, div_str: str, hidden_div_str: str, add_row_id: str, del_row_id: str,
                      database_id: str, app_id: str):
    if app_id == 'converter':
        _compos_type_div = html.Div(
            [
                html.H6('Composition input type:'),
                dcc.RadioItems(id=app_id + '_compos_input_type',
                               options=[
                                   {'label': weight_name, 'value': weight_name},
                                   {'label': atomic_name, 'value': atomic_name},
                               ],
                               value=weight_name,
                               # labelStyle={'display': 'inline-block'},
                               ),
            ], className='row',
        )
        _nuclear_database_div_style = {'display': 'none'}
    else:
        _compos_type_div = None
        _nuclear_database_div_style = {'display': 'block'}

    # Upload div
    upload_field = html.Div(
        [
            # Database dropdown
            html.Div(
                [
                    html.H6('Nuclear database:',
                            # className=col_width_3,
                            ),
                    dcc.Dropdown(
                        id=database_id,
                        options=[
                            {'label': 'ENDF/B-VII.1', 'value': 'ENDF_VII'},
                            {'label': 'ENDF/B-VIII.0', 'value': 'ENDF_VIII'},
                        ],
                        value='ENDF_VIII',
                        searchable=False,
                        clearable=False,
                        className=col_width_3,
                    ),
                ], className='row', style=_nuclear_database_div_style,
            ),
            _compos_type_div,
            # Sample input
            html.H3('Sample info'),
            dcc.Upload(id=id_str,
                       children=html.Div([
                           'Drag and Drop or ',
                           html.A('Select Files'),
                           " (previously exported '###.csv')",
                       ]),
                       style={
                           'width': '100%',
                           'height': '60px',
                           'lineHeight': '60px',
                           'borderWidth': '1px',
                           'borderStyle': 'dashed',
                           'borderRadius': '5px',
                           'textAlign': 'center',
                           'margin': '10px'
                       },
                       # Allow multiple files to be uploaded
                       multiple=True,
                       last_modified=0,
                       ),
            html.Div(id=div_str),
            html.Div(id=hidden_div_str, style={'display': 'none'}, children=0),
            html.Button('+', id=add_row_id, n_clicks_timestamp=0),
            html.Button('-', id=del_row_id, n_clicks_timestamp=0),
        ])
    return upload_field


def init_iso_table(id_str: str):
    iso_table = dt.DataTable(
        data=iso_tb_df_default.to_dict('records'),
        columns=iso_tb_header_df.to_dict('records'),
        # editable=True,
        row_selectable=False,
        filter_action='none',
        sort_action='none',
        row_deletable=False,
        # export_format='csv',
        style_cell_conditional=iso_tb_even_4_col,
        style_data_conditional=iso_tb_gray_cols,
        fixed_rows={'headers': True, 'data': 0},
        style_table={
            'maxHeight': '300',
            'overflowY': 'scroll'
        },
        id=id_str
    )
    return iso_table


app_links_list = []
for i, each_app in enumerate(app_dict.keys()):
    current_number_str = str(i + 1) + '. '
    current_app_name = app_dict[each_app]['name']
    current_url = app_dict[each_app]['url']
    app_links_list.append(current_number_str)
    app_links_list.append(dcc.Link(current_app_name, href=current_url))
    app_links_list.append(html.Br())
app_links_div = html.Div(app_links_list)

sample_tb_even_3_col = [
    {'if': {'column_id': chem_name},
     'width': '33%'},
    {'if': {'column_id': thick_name},
     'width': '33%'},
    {'if': {'column_id': density_name},
     'width': '33%'},
]

iso_tb_even_4_col = [
    {'if': {'column_id': layer_name},
     'width': '25%'},
    {'if': {'column_id': ele_name},
     'width': '25%'},
    {'if': {'column_id': iso_name},
     'width': '25%'},
    {'if': {'column_id': iso_ratio_name},
     'width': '25%'},
]

range_tb_even_5_col = [
    {'if': {'column_id': energy_name},
     'width': '20%'},
    {'if': {'column_id': wave_name},
     'width': '20%'},
    {'if': {'column_id': speed_name},
     'width': '20%'},
    {'if': {'column_id': tof_name},
     'width': '20%'},
    {'if': {'column_id': class_name},
     'width': '20%'},
]

output_tb_uneven_6_col = [
    {'if': {'column_id': thick_name},
     'width': '22%'},
    {'if': {'column_id': density_name},
     'width': '22%'},
    {'if': {'column_id': ratio_name},
     'width': '22%'},
    {'if': {'column_id': molar_name},
     'width': '11%'},
    {'if': {'column_id': number_density_name},
     'width': '11%'},
    {'if': {'column_id': mu_per_cm_name},
     'width': '11%'},
]

color = 'rgb(240, 240, 240)'
range_tb_gray_cols = [
    {'if': {'column_id': speed_name},
     'backgroundColor': color},
    {'if': {'column_id': tof_name},
     'backgroundColor': color},
    {'if': {'column_id': class_name},
     'backgroundColor': color},
]

iso_tb_gray_cols = [
    {'if': {'column_id': layer_name},
     'backgroundColor': color},
    {'if': {'column_id': ele_name},
     'backgroundColor': color},
    {'if': {'column_id': iso_name},
     'backgroundColor': color},
    # striped_rows,
]

markdown_sample = dcc.Markdown('''
NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**. Density input can **ONLY**
be **omitted (leave as blank)** if the input formula is a single element.''')

markdown_disclaimer_sns = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from **ENDF/B** database and the **simulated** beam spectrum at this beamline.''')

markdown_disclaimer_hfir = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from **ENDF/B** database and the **measured** beam spectrum at this beamline.''')

label_sample = html.Label(['When omitted, natural densities will be used. List of densities can be found ',
                           html.A("here.", href='http://periodictable.com/Properties/A/Density.al.html',
                                  target="_blank")])

markdown_compos = dcc.Markdown('''
NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**.''')

markdown_iso = dcc.Markdown('''
NOTE: Uncheck the box will **NOT RESET** this table if you have edited it, but the input will not be used in the
calculations.''')

# Plot control buttons
plot_option_div = html.Div(
    [
        html.Hr(),
        html.H3('Result'),
        html.H5('Plot:'),
        html.Div(
            [
                html.Div(
                    [
                        html.P('X options: '),
                        dcc.RadioItems(id='x_type',
                                       options=[
                                           {'label': 'Energy (eV)', 'value': 'energy'},
                                           {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                           {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
                                       ],
                                       value='energy',
                                       # n_clicks_timestamp=0,
                                       )
                    ], className=col_width_3
                ),
                html.Div(
                    [
                        html.P('Y options: '),
                        dcc.RadioItems(id='y_type',
                                       options=[
                                           {'label': 'Transmission', 'value': 'transmission'},
                                           {'label': 'Attenuation', 'value': 'attenuation'},
                                           {'label': 'Attenuation coefficient', 'value': 'mu_per_cm'},
                                           {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                           {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                       ],
                                       value='transmission',
                                       # n_clicks_timestamp=0,
                                       )
                    ], className=col_width_3
                ),
                html.Div(
                    [
                        html.P('Scale options: '),
                        dcc.RadioItems(id='plot_scale',
                                       options=[
                                           {'label': 'Linear', 'value': 'linear'},
                                           {'label': 'Log x', 'value': 'logx'},
                                           {'label': 'Log y', 'value': 'logy'},
                                           {'label': 'Loglog', 'value': 'loglog'},
                                       ],
                                       value='linear',
                                       # n_clicks_timestamp=0,
                                       )
                    ], className=col_width_3
                ),
                html.Div(
                    [
                        html.P('Show options: '),
                        dcc.Checklist(id='show_opt',
                                      options=[
                                          {'label': 'Total', 'value': 'total'},
                                          {'label': 'Layer', 'value': 'layer'},
                                          {'label': 'Element', 'value': 'ele'},
                                          {'label': 'Isotope', 'value': 'iso'},
                                      ],
                                      value=['layer'],
                                      # n_clicks_timestamp=0,
                                      ),
                    ], className=col_width_3
                ),
            ], className='row'
        ),
    ]
),


def shape_matplot_to_plotly(fig, y_type, plot_scale):
    plotly_fig = tls.mpl_to_plotly(fig)
    # Layout
    plotly_fig.layout.showlegend = True
    plotly_fig.layout.autosize = True
    plotly_fig.layout.height = 600
    plotly_fig.layout.width = 900
    plotly_fig.layout.margin = {'b': 52, 'l': 80, 'pad': 0, 'r': 15, 't': 15}
    plotly_fig.layout.xaxis1.tickfont.size = 15
    plotly_fig.layout.xaxis1.titlefont.size = 18
    plotly_fig.layout.yaxis1.tickfont.size = 15
    plotly_fig.layout.yaxis1.titlefont.size = 18
    plotly_fig.layout.xaxis.autorange = True
    if y_type in ['attenuation', 'transmission']:
        plotly_fig['layout']['yaxis']['autorange'] = False
        if plot_scale in ['logy', 'loglog']:
            plot_scale = 'linear'
    else:
        plotly_fig['layout']['yaxis']['autorange'] = True

    if plot_scale == 'logx':
        plotly_fig['layout']['xaxis']['type'] = 'log'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
    elif plot_scale == 'logy':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    elif plot_scale == 'loglog':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'log'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    else:
        plotly_fig['layout']['xaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
    return plotly_fig
