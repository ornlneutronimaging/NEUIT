import os

import ImagingReso._utilities as ir_util
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
from ImagingReso.resonance import Resonance
from scipy.interpolate import interp1d
import numpy as np
import json
from cerberus import Validator

app_dict = {'app1': {'name': 'Neutron transmission',
                     'url': '/apps/transmission'},
            'app2': {'name': 'Neutron resonance',
                     'url': '/apps/resonance'},
            'app3': {'name': 'Composition converter',
                     'url': '/apps/converter'},
            }

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
class_name = 'Neutron classification'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ratio_name = 'Stoichiometric ratio'
molar_name = 'Molar mass (g/mol)'
number_density_name = 'Atoms (#/cm\u00B3)'
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

# iso_tb_df_default = pd.DataFrame()
# iso_tb_df_default[layer_name] = [None]
# iso_tb_df_default[ele_name] = [None]
# iso_tb_df_default[iso_name] = [None]
# iso_tb_df_default[iso_ratio_name] = [None]


output_stack_header_df = pd.DataFrame({
    'name': [thick_name, density_name, ratio_name, molar_name, number_density_name],
    'id': [thick_name, density_name, ratio_name, molar_name, number_density_name],
    'deletable': [False, False, False, False, False],
    'editable': [False, False, False, False, False],
})

col_width_3 = 'three columns'
col_width_6 = 'six columns'
empty_div = html.Div()


def greater_than_zero(field, value, error):
    if not value > 0:
        error(field, "must be greater than '0'")


def type_is_str(field, value, error):
    if type(value) is str:
        error(field, "must be a number between '0' and '1'")


def empty_str(field, value, error):
    if type(value) is str:
        if not value == '':
            error(field, "must be a number >= '0' or leave as 'blank'")


def valid_chem_name(field, value, error):
    if not is_number(value):
        if not validate_chem_name(value):
            error(field, "must be a valid 'chemical formula', input is case sensitive")
    else:
        error(field, "must be a valid 'chemical formula', input is case sensitive")


compos_dict_schema = {
    chem_name: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    compos_2nd_col_id: {'type': 'number', 'validator': greater_than_zero},
}

iso_dict_schema = {
    layer_name: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    ele_name: {'type': 'string', 'empty': False, 'required': True, },
    iso_name: {'type': 'string', 'empty': False, 'required': True, },
    iso_ratio_name: {'type': 'number', 'min': 0, 'max': 1, 'required': True, 'validator': type_is_str, },
}

sample_dict_schema = {
    chem_name: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    thick_name: {'type': 'number', 'min': 0, 'required': True, },
    density_name: {'anyof_type': ['string', 'number'], 'min': 0, 'validator': empty_str, },
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
    # _lambda = ir_util.ev_to_angstroms(array=_e)
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
    # _e = ir_util.angstroms_to_ev(array=_lambda)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {energy_name: _e,
            wave_name: _lambda,
            speed_name: _v,
            tof_name: _tof,
            class_name: _class}


# def drop_df_column_not_needed(input_df: pd.DataFrame, column_name: str):
#     if column_name in input_df.columns:
#         _dropped_df = input_df.drop(columns=[column_name])
#         return _dropped_df
#     else:
#         return input_df


def creat_sample_df_from_compos_df(compos_tb_df):
    _compos_tb_df = compos_tb_df[:]
    sample_df = pd.DataFrame()
    sample_df[chem_name] = _compos_tb_df[chem_name]
    sample_df[thick_name] = 1
    sample_df[density_name] = ''
    return sample_df


def is_number(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False


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


def validate_sample_input(sample_df: pd.DataFrame, sample_schema: dict):
    # Test sample input format
    test_passed_list, output_div_list = validate_input_tb_rows(schema=sample_schema, input_df=sample_df)
    return test_passed_list, output_div_list


def validate_iso_input(iso_df: pd.DataFrame, iso_schema: dict, test_passed_list: list, output_div_list: list):
    # Test iso input format
    iso_test_passed_list, iso_output_div_list = validate_input_tb_rows(schema=iso_schema, input_df=iso_df)
    test_passed_list += iso_test_passed_list
    output_div_list += iso_output_div_list

    # Test the sum of iso ratio == 1
    if all(test_passed_list):
        sum_test_passed, sum_test_output_div = validate_sum_of_iso_ratio(iso_df=iso_df)
        test_passed_list += sum_test_passed
        output_div_list += sum_test_output_div

    return test_passed_list, output_div_list


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
    if beamline == 'imaging':
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
    v = Validator(schema)
    passed_list = []
    div_list = []
    for each_input_dict in input_dict_list:
        passed, div = _validate_input(v=v, input_dict=each_input_dict)
        div_list.append(div)
        passed_list.append(passed)
    return passed_list, div_list


def _validate_input(v: Validator, input_dict: dict):
    passed = v.validate(input_dict)
    if passed:
        return passed, None
    else:
        error_message_str = v.errors
    return passed, html.P('INPUT ERROR: {}'.format(error_message_str))


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


def validate_chem_name(input_name: str):
    """ Returns True if string is a number. """
    try:
        ir_util.formula_to_dictionary(input_name)
        return True
    except ValueError:
        return False


def init_reso_from_tb(range_tb_df, e_step):
    v_1 = range_tb_df[energy_name][0]
    v_2 = range_tb_df[energy_name][1]
    if v_1 < v_2:
        o_reso = Resonance(energy_min=v_1, energy_max=v_2, energy_step=e_step)
    else:
        o_reso = Resonance(energy_min=v_2, energy_max=v_1, energy_step=e_step)
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
        if density_name not in sample_tb_df.columns:
            if thick_name not in sample_tb_df.columns:  # for compos_df, only have column "compos_2nd_col_id"
                try:
                    o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                     thickness=1)
                except ValueError:
                    pass
            else:
                try:
                    o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                     thickness=float(sample_tb_df[thick_name][layer_index]))
                except ValueError:
                    pass
        elif sample_tb_df[density_name][layer_index] == '':
            try:
                o_reso.add_layer(formula=sample_tb_df[chem_name][layer_index],
                                 thickness=float(sample_tb_df[thick_name][layer_index]))
            except ValueError:
                pass
        else:
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


def calculate_transmission(sample_tb_df, iso_tb_df, iso_changed, beamline, band_min, band_max, band_type):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = {'imaging': 'static/instrument_file/beam_flux_cg1d.txt',
                           'snap': 'static/instrument_file/beam_flux_snap.txt',
                           # 'venus': 'static/instrument_file/beam_flux_venus.txt',
                           }
    df_flux_raw = load_beam_shape(_path_to_beam_shape[beamline])
    if beamline == 'imaging':
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
    __o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=sample_tb_df)
    o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)
    o_stack = o_reso.stack

    # interpolate with the beam shape energy
    interp_type = 'cubic'
    energy = o_reso.total_signal['energy_eV'].round(6)  # !!!need to fix ImagingReso energy_eV columns
    trans = o_reso.total_signal['transmission']

    interp_flux_function = interp1d(x=df_flux_raw['energy_eV'], y=df_flux_raw['flux'], kind=interp_type)
    print(min(energy), max(energy))
    print(min(df_flux_raw['energy_eV']), max(df_flux_raw['energy_eV']))
    flux_interp = interp_flux_function(energy)
    df_flux_interp = pd.DataFrame()
    df_flux_interp['energy_eV'] = energy
    df_flux_interp['flux'] = flux_interp
    df_flux = df_flux_interp[:]
    trans_ = trans

    # calculated transmitted flux
    trans_flux = trans_ * df_flux['flux']
    integr_total = np.trapz(y=df_flux['flux'] / df_flux['energy_eV'], x=df_flux['energy_eV'], dx=1e-6).round(3)
    integr_trans = np.trapz(y=trans_flux / df_flux['energy_eV'], x=df_flux['energy_eV'], dx=1e-6).round(3)
    _total_trans = integr_trans / integr_total * 100

    return _total_trans, o_stack


def form_transmission_result_div(sample_tb_rows, iso_tb_rows, iso_changed, beamline, band_min, band_max, band_type):
    disclaimer = markdown_disclaimer_sns
    if beamline == 'snap':
        beamline_name = 'SNAP (BL-3), SNS'
    elif beamline == 'venus':
        beamline_name = 'VENUS (BL-10), SNS'
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
        iso_tb_df = form_iso_table(sample_df=sample_tb_df)

    # Calculation starts
    total_trans, o_stack = calculate_transmission(sample_tb_df=sample_tb_df,
                                                  iso_tb_df=iso_tb_df,
                                                  iso_changed=iso_changed,
                                                  beamline=beamline,
                                                  band_min=band_min,
                                                  band_max=band_max,
                                                  band_type=band_type)
    output_div_list = [
        html.Hr(),
        html.H3('Result at ' + beamline_name),
        html.P('Transmission (total): {} %'.format(round(total_trans, 3))),
        html.P('Attenuation (total): {} %'.format(round(100 - total_trans, 3))),
        disclaimer,
        # html.Div(sample_stack_div_list),
    ]
    return output_div_list, o_stack


def form_sample_stack_table_div(o_stack):
    sample_stack_div_list = [html.Hr(), html.H5('Sample stack:')]
    layers = list(o_stack.keys())
    layer_dict = {}
    for l, layer in enumerate(layers):
        elements_in_current_layer = o_stack[layer]['elements']
        l_str = str(l + 1)
        current_layer_list = [
            html.P("Layer {}: {}".format(l_str, layer)),
        ]
        layer_dict[thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[density_name] = round(o_stack[layer]['density']['value'], 3)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[ratio_name] = ":".join(_ratio_str_list)
        layer_dict[molar_name] = round(o_stack[layer]['molar_mass']['value'], 4)
        layer_dict[number_density_name] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'])
        _df_layer = pd.DataFrame([layer_dict])
        current_layer_list.append(
            dt.DataTable(data=_df_layer.to_dict('records'),
                         columns=output_stack_header_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filter_action='none',
                         sort_action='none',
                         row_deletable=False,
                         style_cell_conditional=output_tb_uneven_5_col,
                         ))

        for e, ele in enumerate(elements_in_current_layer):
            _iso_list = o_stack[layer][ele]['isotopes']['list']
            _iso_ratios = o_stack[layer][ele]['isotopes']['isotopic_ratio']
            iso_dict = {}
            name_list = []
            id_list = []
            deletable_list = []
            editable_list = []
            for i, iso in enumerate(_iso_list):
                current_id = 'column_' + str(i + 1)
                name_list.append(iso)
                id_list.append(current_id)
                deletable_list.append(False)
                editable_list.append(False)
                iso_dict[current_id] = round(_iso_ratios[i], 4)

            _i = len(id_list)
            name_list.append(molar_name)
            molar_name_id = 'column_' + str(_i + 1)
            id_list.append(molar_name_id)
            deletable_list.append(False)
            editable_list.append(False)
            name_list.append(number_density_name)
            number_density_name_id = 'column_' + str(_i + 2)
            id_list.append(number_density_name_id)
            deletable_list.append(False)
            editable_list.append(False)

            iso_dict[molar_name_id] = round(o_stack[layer][ele]['molar_mass']['value'], 4)
            iso_dict[number_density_name_id] = '{:0.3e}'.format(o_stack[layer][ele]['atoms_per_cm3'])
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
                             style_cell_conditional=[
                                 {'if': {'column_id': molar_name_id},
                                  'width': '14%'},
                                 {'if': {'column_id': number_density_name_id},
                                  'width': '14%'},
                             ]
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


def form_iso_table(sample_df: pd.DataFrame):
    o_reso = Resonance(energy_min=1, energy_max=2, energy_step=1)
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
    pre_len = len(prev_iso_df)
    new_len = len(new_iso_df)
    if pre_len < new_len:
        while len(prev_iso_df) < len(new_iso_df):
            prev_iso_df = prev_iso_df.append(iso_tb_df_default, ignore_index=True)
    elif pre_len > new_len:
        while len(new_iso_df) < len(prev_iso_df):
            new_iso_df = new_iso_df.append(iso_tb_df_default, ignore_index=True)
    prev_iso_df = prev_iso_df[[layer_name, ele_name, iso_name, iso_ratio_name]]  # Force order of col to be the same
    _indices = prev_iso_df == new_iso_df
    new_iso_df[iso_ratio_name][_indices[layer_name]] = prev_iso_df[iso_ratio_name][_indices[layer_name]]
    new_iso_df = new_iso_df[new_iso_df[new_iso_df.columns[0]].notnull()]
    return new_iso_df


def update_range_tb_by_coordinate(range_table_rows, distance, modified_coord):
    row = modified_coord[0]
    col = modified_coord[1]
    if col == 0:
        input_value = range_table_rows[row][energy_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_e(e_ev=float(input_value), distance_m=distance)
            # for each_col in range_table_rows[row].keys():
            #     range_table_rows[row][each_col] = things_to_fill[each_col]
            range_table_rows[row][energy_name] = input_value
            range_table_rows[row][wave_name] = things_to_fill[wave_name]
            range_table_rows[row][speed_name] = things_to_fill[speed_name]
            range_table_rows[row][tof_name] = things_to_fill[tof_name]
            range_table_rows[row][class_name] = things_to_fill[class_name]
        else:
            for each_col in [wave_name, speed_name, tof_name, class_name]:
                range_table_rows[row][each_col] = 'N/A'
    elif col == 1:
        input_value = range_table_rows[row][wave_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_wave(wave_angstroms=float(input_value), distance_m=distance)
            # for each_col in range_table_rows[row].keys():
            range_table_rows[row][energy_name] = things_to_fill[energy_name]
            range_table_rows[row][wave_name] = input_value
            range_table_rows[row][speed_name] = things_to_fill[speed_name]
            range_table_rows[row][tof_name] = things_to_fill[tof_name]
            range_table_rows[row][class_name] = things_to_fill[class_name]
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


def shape_reso_df_to_output(y_type, x_type, show_opt, jsonified_data, prev_show_opt, to_csv):
    df_dict = load_dfs(jsonified_data=jsonified_data)
    # Determine Y df and y_label to plot
    if y_type == 'transmission':
        y_label = 'Transmission'
    elif y_type == 'attenuation':
        y_label = 'Attenuation'
    elif y_type == 'sigma':
        y_label = 'Cross-sections (barn)'
    elif y_type == 'sigma_raw':
        y_label = 'Cross-sections (barn)'
    else:  # y_type == 'miu_per_cm':
        y_label = 'Attenuation coefficient \u03BC (cm\u207B\u00B9)'

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


# Layout
striped_rows = {'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'}

editable_white = {'if': {'column_editable': False},
                  'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white'}


def init_iso_table(id_str: str):
    iso_table = dt.DataTable(
        data=iso_tb_df_default.to_dict('records'),
        columns=iso_tb_header_df.to_dict('records'),
        # editable=True,
        row_selectable=False,
        filter_action='none',
        sort_action='none',
        row_deletable=False,
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
    current_str = str(i + 1) + '. ' + app_dict[each_app]['name']
    current_url = app_dict[each_app]['url']
    app_links_list.append(dcc.Link(current_str, href=current_url))
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

output_tb_uneven_5_col = [
    {'if': {'column_id': thick_name},
     'width': '24%'},
    {'if': {'column_id': density_name},
     'width': '24%'},
    {'if': {'column_id': ratio_name},
     'width': '24%'},
    {'if': {'column_id': molar_name},
     'width': '14%'},
    {'if': {'column_id': number_density_name},
     'width': '14%'},
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
NOTE: Formula is **case sensitive**, stoichiometric ratio must be **integer**. 
Density input can **ONLY** be **omitted (leave as blank)** if the input formula is a single element.''')

markdown_disclaimer_sns = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from ENDF/B-VII.1 database and the *simulated* beam spectrum at this beamline.''')

markdown_disclaimer_hfir = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from ENDF/B-VII.1 database and the *measured* beam spectrum at this beamline.''')

label_sample = html.Label(['Natural densities used are from ',
                           html.A("here", href='http://periodictable.com/Properties/A/Density.al.html',
                                  target="_blank")])

markdown_compos = dcc.Markdown('''
NOTE: Formula is **case sensitive**, stoichiometric ratio must be **integer**.''')

markdown_iso = dcc.Markdown('''
NOTE: Uncheck the box will **NOT RESET** this table if you have edited it,
but the input will not be used in calculations.''')

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
                                           {'label': 'Attenuation', 'value': 'attenuation'},
                                           {'label': 'Transmission', 'value': 'transmission'},
                                           {'label': 'Attenuation coefficient', 'value': 'miu_per_cm'},
                                           {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                           {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                       ],
                                       value='attenuation',
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
                                      value=['iso'],
                                      # n_clicks_timestamp=0,
                                      ),
                    ], className=col_width_3
                ),
            ], className='row'
        ),
    ]
),
