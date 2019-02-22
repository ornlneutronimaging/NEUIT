import os

import ImagingReso._utilities as ir_util
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from ImagingReso.resonance import Resonance
from scipy.interpolate import interp1d
import numpy as np
from pprint import pprint

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
class_name = 'Neutron classification'
range_tb_header = [energy_name, wave_name, speed_name, tof_name, class_name]

chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ratio_name = 'Stoichiometric ratio'
molar_name = 'Molar mass (g/mol)'
number_density_name = 'Atoms per cm\u00B3 (#)'
weight_name = 'Weight (g)'
weight_name_p = 'Weight (%)'
atomic_name = 'Atomic (mol)'
atomic_name_p = 'Atomic (%)'
sample_tb_header = [chem_name, thick_name, density_name]
converter_tb_header = [chem_name, weight_name, atomic_name]
converter_tb_header_p = [chem_name, weight_name_p, atomic_name_p]

layer_name = 'Layer'
ele_name = 'Element'
iso_name = 'Isotope'
iso_ratio_name = 'Isotopic ratio'
iso_table_header = [layer_name, ele_name, iso_name, iso_ratio_name]
iso_tb_rows_default = [{ele_name: None, iso_name: None, iso_ratio_name: None, layer_name: None}]
iso_tb_df_default = pd.DataFrame(iso_tb_rows_default)
col_3 = 'three columns'
col_6 = 'six columns'


def classify_neutron(energy_ev):
    """

    :param energy_ev:
    :return:
    """
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


def output_error_div(error_message: str):
    error_message_div = dcc.Markdown(error_message)
    return error_message_div


def init_reso_from_tb(range_tb_rows, e_step):
    df_range_tb = pd.DataFrame(range_tb_rows)
    e_min = df_range_tb[energy_name][0]
    e_max = df_range_tb[energy_name][1]
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
    sample_tb_df = sample_tb_df[sample_tb_df[chem_name] != '']
    num_layer = len(sample_tb_df['Chemical formula'])
    for i in range(num_layer):
        if sample_tb_df[chem_name][i] == '':
            raise IOError('Remove empty lines in sample input table.')
        if thick_name in sample_tb_df.keys():
            assert sample_tb_df[thick_name][i] != ''
            if sample_tb_df[density_name][i] == '':
                o_reso.add_layer(formula=sample_tb_df[chem_name][i],
                                 thickness=float(sample_tb_df[thick_name][i]))
            else:
                o_reso.add_layer(formula=sample_tb_df[chem_name][i],
                                 density=float(sample_tb_df[density_name][i]),
                                 thickness=float(sample_tb_df[thick_name][i]))
        if weight_name in sample_tb_df.keys():
            # assert sample_tb_df[weight_name][i] != '' or sample_tb_df[atomic_name][i] != ''
            o_reso.add_layer(formula=sample_tb_df[chem_name][i],
                             thickness=1)
    return o_reso


def unpack_iso_tb_df_and_update(o_reso, iso_tb_df, iso_changed):
    # if layer_name not in iso_tb_df.columns:
    if len(iso_changed) == 0:
        return o_reso
    else:
        layer_list = list(o_reso.stack.keys())
        for each_layer in layer_list:
            element_list = o_reso.stack[each_layer]['elements']
            for each_ele in element_list:
                _ele_ratio_list = []
                for i in range(len(iso_tb_df)):
                    if each_layer == iso_tb_df[layer_name][i] and each_ele == iso_tb_df[ele_name][i]:
                        _ele_ratio_list.append(float(iso_tb_df[iso_ratio_name][i]))
                o_reso.set_isotopic_ratio(compound=each_layer, element=each_ele, list_ratio=_ele_ratio_list)
        return o_reso


def add_del_tb_rows(add_or_del, sample_tb_rows):
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    for _each in sample_tb_header:
        if _each not in df_sample_tb.columns:
            df_sample_tb[_each] = ['']
            _in = False
        else:
            _in = True
    _formula_list = list(df_sample_tb[chem_name])
    _thickness_list = list(df_sample_tb[thick_name])
    _density_list = list(df_sample_tb[density_name])
    if add_or_del == 'add':
        if _in:
            _formula_list.append('')
            _thickness_list.append('')
            _density_list.append('')
    elif add_or_del == 'del':
        _formula_list.pop()
        _thickness_list.pop()
        _density_list.pop()
    else:
        _formula_list = _formula_list
        _thickness_list = _thickness_list
        _density_list = _density_list
    _df_sample = pd.DataFrame({
        chem_name: _formula_list,
        thick_name: _thickness_list,
        density_name: _density_list,
    })
    return _df_sample


def add_del_tb_rows_converter(add_or_del, sample_tb_rows, input_type: str, header: list):
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    for _each in header:
        if _each not in df_sample_tb.columns:
            df_sample_tb[_each] = ['']
            _in = False
        else:
            _in = True
    _formula_list = list(df_sample_tb[chem_name])
    _list = list(df_sample_tb[input_type])
    if add_or_del == 'add':
        if _in:
            _formula_list.append('')
            _list.append('')
    elif add_or_del == 'del':
        _formula_list.pop()
        _list.pop()
    else:
        _formula_list = _formula_list
        _list = _list
    _df_sample = pd.DataFrame({
        chem_name: _formula_list,
        input_type: _list,
    })
    return _df_sample


# def add_del_tb_rows(n_add_time, n_del_time, sample_tb_rows):
#     df_sample_tb = pd.DataFrame(sample_tb_rows)
#     for _each in [chem_name, thick_name, density_name]:
#         if _each not in df_sample_tb.columns:
#             df_sample_tb[_each] = ['']
#             _in = False
#         else:
#             _in = True
#     _formula_list = list(df_sample_tb[chem_name])
#     _thickness_list = list(df_sample_tb[thick_name])
#     _density_list = list(df_sample_tb[density_name])
#     if n_add_time > n_del_time:
#         if _in:
#             _formula_list.append('')
#             _thickness_list.append('')
#             _density_list.append('')
#     elif n_add_time == n_del_time:
#         _formula_list = _formula_list
#         _thickness_list = _thickness_list
#         _density_list = _density_list
#     else:
#         _formula_list.pop()
#         _thickness_list.pop()
#         _density_list.pop()
#     _df_sample = pd.DataFrame({
#         chem_name: _formula_list,
#         thick_name: _thickness_list,
#         density_name: _density_list,
#     })
#     return _df_sample


def calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows, iso_tb_rows, iso_changed):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    __o_reso = Resonance(energy_min=0.00025, energy_max=0.12525, energy_step=0.000625)

    df_sample_tb = pd.DataFrame(sample_tb_rows)
    _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=df_sample_tb)
    df_iso_tb = pd.DataFrame(iso_tb_rows)
    o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=df_iso_tb, iso_changed=iso_changed)

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
        layer_dict[thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[density_name] = o_stack[layer]['density']['value']
        # layer_dict[density_name] = round(o_stack[layer]['density']['value'], 4)
        _ratio_str_list = [str(_p) for _p in o_stack[layer]['stoichiometric_ratio']]
        layer_dict[ratio_name] = ":".join(_ratio_str_list)
        _df_layer = pd.DataFrame([layer_dict])
        current_layer_list.append(
            dt.DataTable(rows=_df_layer.to_dict('records'),
                         columns=[thick_name, density_name, ratio_name],
                         editable=False,
                         row_selectable=False,
                         filterable=False,
                         sortable=False,
                         # id='sample_table'
                         ))

        for e, ele in enumerate(elements_in_current_layer):
            _iso_list = o_stack[layer][ele]['isotopes']['list']
            _iso_ratios = o_stack[layer][ele]['isotopes']['isotopic_ratio']
            iso_dict = {}
            for i, iso in enumerate(_iso_list):
                iso_dict[iso] = round(_iso_ratios[i], 4)
            iso_dict[molar_name] = round(o_stack[layer][ele]['molar_mass']['value'], 4)
            iso_dict[number_density_name] = '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'][ele])
            _df_iso = pd.DataFrame([iso_dict])
            current_layer_list.append(
                dt.DataTable(rows=_df_iso.to_dict('records'),
                             columns=_df_iso.columns,
                             editable=False,
                             row_selectable=False,
                             filterable=False,
                             sortable=False,
                             ))
            # ele_dict = {molar_name: round(o_stack[layer][ele]['molar_mass']['value'], 4),
            #             number_density_name: '{:0.3e}'.format(o_stack[layer]['atoms_per_cm3'][ele])}
            # _df_ele = pd.DataFrame([ele_dict])
            # current_layer_list.append(
            #     dt.DataTable(rows=_df_ele.to_dict('records'),
            #                  columns=_df_ele.columns,
            #                  editable=False,
            #                  row_selectable=False,
            #                  filterable=False,
            #                  sortable=False,
            #                  ))

        div_list.append(html.Div(current_layer_list))
        div_list.append(html.Br())

    return _total_trans, div_list, o_stack


def convert_input_to_composition(sample_tb_rows, input_type, o_stack):
    df_input = pd.DataFrame(sample_tb_rows)
    df_input = df_input[df_input[chem_name] != '']
    df_input[input_type] = pd.to_numeric(df_input[input_type])  # , errors='ignore')
    if input_type == weight_name:
        fill_name = atomic_name_p
        update_name = weight_name_p
    else:
        fill_name = weight_name_p
        update_name = atomic_name_p
        df_input.drop(columns=[weight_name], inplace=True)
    result_list = []
    _ele_list = []
    _mol_list = []
    _input_converted_p_list = []
    _input_sum = df_input[input_type].sum()
    for _n, each_chem in enumerate(df_input[chem_name]):
        _molar_mass = o_stack[each_chem]['molar_mass']['value']
        input_num = df_input[input_type][_n]
        _current_ele_list = o_stack[each_chem]['elements']
        _current_ratio_list = o_stack[each_chem]['stoichiometric_ratio']
        _input_percentage = input_num * 100 / _input_sum
        _ele_list += _current_ele_list
        if input_type == weight_name:  # wt. input (g)
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
    df_input[fill_name] = np.round(_output_array, 3)
    df_input[update_name] = np.round(_input_converted_p_array, 3)
    return df_input, _ele_list, _mol_list


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
        effective_str += _e + str(int(round(mol_sum_for_ele_array[index], 3)*1000))
    return effective_str


def form_iso_table(sample_tb_rows):
    o_reso = Resonance(energy_min=1, energy_max=2, energy_step=1)
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=df_sample_tb)
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

    _dict = {'Layer': lay_list,
             'Element': ele_list,
             'Isotope': iso_list,
             'Isotopic ratio': iso_ratio_list,
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
                    ], className=col_3
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
                    ], className=col_3
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
                    ], className=col_3
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
                    ], className=col_3
                ),
            ], className='row'
        ),
    ]
),
