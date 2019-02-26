import os

import ImagingReso._utilities as ir_util
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
from ImagingReso.resonance import Resonance
from scipy.interpolate import interp1d
import numpy as np
from cerberus import Validator

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
number_density_name = 'Atoms per cm\u00B3 (#)'
layer_name = 'Layer'
ele_name = 'Element'
iso_name = 'Isotope'
iso_ratio_name = 'Isotopic ratio'
weight_name = 'Weight (g)'
weight_name_p = 'Weight (%)'
atomic_name = 'Atomic (mol)'
atomic_name_p = 'Atomic (%)'
column_1 = 'column_1'
column_2 = 'column_2'
column_3 = 'column_3'
column_4 = 'column_4'
column_5 = 'column_5'

energy_range_header_df = pd.DataFrame({
    'name': [energy_name, wave_name, speed_name, tof_name, class_name],
    'id': [column_1, column_2, column_3, column_4, column_5],
    'deletable': [False, False, False, False, False],
    'editable': [True, False, False, False, False],
})

sample_header_df = pd.DataFrame({
    'name': [chem_name, thick_name, density_name],
    'id': [column_1, column_2, column_3],
    'deletable': [False, False, False],
    'editable': [True, True, True],
})

compos_header_df = pd.DataFrame({
    'name': [chem_name, weight_name, atomic_name],
    'id': [column_1, column_2, column_3],
    'deletable': [False, False, False],
    'editable': [True, True, True],
})

compos_header_p_df = pd.DataFrame({
    'name': [chem_name, weight_name_p, atomic_name_p],
    'id': [column_1, column_2, column_3],
    'deletable': [False, False, False],
    'editable': [False, False, False],
})

iso_tb_header_df = pd.DataFrame({
    'name': [layer_name, ele_name, iso_name, iso_ratio_name],
    'id': [column_1, column_2, column_3, column_4],
    'deletable': [False, False, False, False],
    'editable': [False, False, False, True],
})

iso_tb_df_default = pd.DataFrame({
    column_1: [None],
    column_2: [None],
    column_3: [None],
    column_4: [None],
})

output_stack_header_df = pd.DataFrame({
    'name': [thick_name, density_name, ratio_name],
    'id': [column_1, column_2, column_3],
    'deletable': [False, False, False],
    'editable': [False, False, False],
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
    if not validate_chem_name(value):
        error(field, "must be a valid 'chemical formula', input is case sensitive")


compos_dict_schema = {
    column_1: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    column_2: {'type': 'number', 'validator': greater_than_zero},
    column_3: {'type': 'number', 'validator': greater_than_zero},
}

iso_dict_schema = {
    column_1: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    column_2: {'type': 'string', 'empty': False, 'required': True, },
    column_3: {'type': 'string', 'empty': False, 'required': True, },
    column_4: {'type': 'number', 'min': 0, 'max': 1, 'required': True, 'validator': type_is_str, },
}

sample_dict_schema = {
    column_1: {'type': 'string', 'empty': False, 'required': True, 'validator': valid_chem_name, },
    column_2: {'type': 'number', 'min': 0, 'required': True, },
    column_3: {'anyof_type': ['string', 'number'], 'min': 0, 'validator': empty_str, },
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


def drop_df_column_not_needed(input_df: pd.DataFrame, column_name: str):
    if column_name in input_df.columns:
        _dropped_df = input_df.drop(columns=[column_name])
        return _dropped_df
    else:
        return input_df


def creat_sample_df_from_compos_df(compos_tb_df):
    _compos_tb_df = compos_tb_df[:]
    sample_df = pd.DataFrame()
    sample_df[column_1] = _compos_tb_df[column_1]
    sample_df[column_2] = 1
    sample_df[column_3] = ''
    return sample_df


def is_number_tryexcept(s):
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
            if is_number_tryexcept(each_item):
                _current_output_list.append(float(each_item))
            else:
                _current_output_list.append(each_item)
        output_dict[each_key] = _current_output_list
    return output_dict


def validate_sample_input(sample_df: pd.DataFrame, iso_df: pd.DataFrame, sample_schema: dict, iso_schema: dict):
    # Test sample input format
    test_passed_list, output_div_list = validate_input_tb_rows(schema=sample_schema, input_df=sample_df)

    # Test iso input format
    if all(test_passed_list):
        iso_test_passed_list, iso_output_div_list = validate_input_tb_rows(schema=iso_schema, input_df=iso_df)
        test_passed_list += iso_test_passed_list
        output_div_list += iso_output_div_list

    # Test the sum of iso ratio == 1
    if all(test_passed_list):
        sum_test_passed, sum_test_output_div = validate_sum_of_iso_ratio(iso_df=iso_df)
        test_passed_list.append(sum_test_passed)
        output_div_list.append(sum_test_output_div)

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
        df = iso_df.groupby([column_1, column_2]).sum()
        df_boo = df[column_4] - 1.0
        boo = df_boo.abs() >= 0.005
        passed_list = list(boo)
        if any(passed_list):
            _list = df.index[boo].tolist()
            return False, html.P("INPUT ERROR: {}: ['sum of isotopic ratios is not 1']".format(str(_list)))
        else:
            return True, None
    except KeyError:
        return False


def validate_chem_name(input_name: str):
    """ Returns True if string is a number. """
    try:
        ir_util.formula_to_dictionary(input_name)
        return True
    except ValueError:
        return False


def init_reso_from_tb(range_tb_df, e_step):
    e_min = range_tb_df[column_1][0]
    e_max = range_tb_df[column_1][1]
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
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
    energy_list = ir_util.angstroms_to_ev(df['wavelength_A'])
    df.insert(1, 'energy_eV', energy_list)
    return df


def unpack_sample_tb_df_and_add_layer(o_reso, sample_tb_df):
    num_layer = len(sample_tb_df[column_1])
    for i in range(num_layer):
        if sample_tb_df[column_3][i] == '':
            try:
                o_reso.add_layer(formula=sample_tb_df[column_1][i],
                                 thickness=float(sample_tb_df[column_2][i]))
            except ValueError:
                pass
        else:
            try:
                o_reso.add_layer(formula=sample_tb_df[column_1][i],
                                 thickness=float(sample_tb_df[column_2][i]),
                                 density=float(sample_tb_df[column_3][i]))
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
                for i in range(len(iso_tb_df)):
                    if each_layer == iso_tb_df[column_1][i] and each_ele == iso_tb_df[column_2][i]:
                        _ele_ratio_list.append(float(iso_tb_df[column_4][i]))
                o_reso.set_isotopic_ratio(compound=each_layer, element=each_ele, list_ratio=_ele_ratio_list)
        return o_reso


def calculate_transmission_cg1d_and_form_stack_table(sample_tb_df, iso_tb_df, iso_changed):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    __o_reso = Resonance(energy_min=0.00025, energy_max=0.12525, energy_step=0.000625)
    _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=sample_tb_df)
    o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)

    # interpolate with the beam shape energy
    interp_type = 'cubic'
    energy = o_reso.total_signal['energy_eV']
    trans = o_reso.total_signal['transmission']
    interp_function = interp1d(x=energy, y=trans, kind=interp_type)
    # add interpolated transmission value to beam shape df
    trans = interp_function(df['energy_eV'])
    # calculated transmitted flux
    trans_flux = trans * df['flux']
    _total_trans = sum(trans_flux) / sum(df['flux']) * 100
    # total_trans = round(_total_trans, 3)

    o_stack = o_reso.stack
    div_list = []
    layers = list(o_stack.keys())
    layer_dict = {}
    for l, layer in enumerate(layers):
        elements_in_current_layer = o_stack[layer]['elements']
        l_str = str(l + 1)
        current_layer_list = [
            html.P("Layer {}: {}".format(l_str, layer)),
        ]
        layer_dict[column_1] = o_stack[layer]['thickness']['value']
        layer_dict[column_2] = round(o_stack[layer]['density']['value'], 3)
        # layer_dict[density_name] = round(o_stack[layer]['density']['value'], 4)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[column_3] = ":".join(_ratio_str_list)
        _df_layer = pd.DataFrame([layer_dict])
        current_layer_list.append(
            dt.DataTable(data=_df_layer.to_dict('records'),
                         columns=output_stack_header_df.to_dict('records'),
                         editable=False,
                         row_selectable=False,
                         filtering=False,
                         sorting=False,
                         row_deletable=False,
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
            iso_dict[number_density_name_id] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'][ele])
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
                             filtering=False,
                             sorting=False,
                             row_deletable=False,
                             ))

        div_list.append(html.Div(current_layer_list))
        div_list.append(html.Br())

    return _total_trans, div_list, o_stack


def convert_input_to_composition(compos_df, compos_type, o_stack):
    if compos_type == weight_name:
        fill_name = column_3
        update_name = column_2
    else:
        fill_name = column_2
        update_name = column_3
    result_list = []
    _ele_list = []
    _mol_list = []
    _input_converted_p_list = []
    _input_sum = compos_df[update_name].sum()
    for _n, each_chem in enumerate(compos_df[column_1]):
        _molar_mass = o_stack[each_chem]['molar_mass']['value']
        input_num = compos_df[update_name][_n]
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

    _dict = {column_1: lay_list,
             column_2: ele_list,
             column_3: iso_list,
             column_4: iso_ratio_list,
             }
    _df = pd.DataFrame(_dict)

    return _df


markdown_sample = dcc.Markdown(
    '''NOTE: Formula is **case sensitive**, atomic ratio must be **integers**. Density input can be omitted (leave as blank) 
    only if the input formula is single element, natural densities available
    [here](http://periodictable.com/Properties/A/Density.al.html) are used.''')

markdown_iso = dcc.Markdown("""NOTE: Please edit **ONLY** the 'Isotopic ratio' column.
                        Editing of 'Sample info' will **RESET** contents in isotope table.""")

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
                                           {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                           {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                       ],
                                       value='attenuation',
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
                                      values=['iso'],
                                      ),
                    ], className=col_width_3
                ),
            ], className='row'
        ),
    ]
),
