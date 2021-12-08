import pandas as pd
import numpy as np

import callbacks.utilities.constants as constants


compos_header_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.weight_name],
    'id': [constants.chem_name,
           constants.compos_2nd_col_id],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric']
})


compos_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.compos_2nd_col_id: {'type': 'number', 'greater_than_zero': True},
}


compos_header_percent_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.weight_name_p,
             constants.atomic_name_p],
    'id': [constants.chem_name,
           constants.weight_name_p,
           constants.atomic_name_p],
    # 'deletable': [False, False, False],
    'editable': [False, False, False],
})


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