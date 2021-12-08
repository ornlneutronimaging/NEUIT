import pandas as pd

from ImagingReso.resonance import Resonance

import callbacks.utilities.constants as constants
from callbacks.utilities.initialization import iso_tb_df_default


sample_header_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.thick_name,
             constants.density_name],
    'id': [constants.chem_name,
           constants.thick_name,
           constants.density_name],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric', 'any']
})


def create_sample_df_from_compos_df(compos_tb_df):
    _compos_tb_df = compos_tb_df[:]
    sample_df = pd.DataFrame()
    sample_df[constants.chem_name] = _compos_tb_df[constants.chem_name]
    sample_df[constants.thick_name] = 1
    sample_df[constants.density_name] = ''
    return sample_df


def unpack_sample_tb_df_and_add_layer(o_reso, sample_tb_df):
    num_layer = len(sample_tb_df[constants.chem_name])
    for layer_index in range(num_layer):
        if constants.density_name not in sample_tb_df.columns:  # sample density name is NOT in the tb
            if constants.thick_name not in sample_tb_df.columns:  # for compos_df, only have column "compos_2nd_col_id"
                try:
                    o_reso.add_layer(formula=sample_tb_df[constants.chem_name][layer_index],
                                     thickness=1)  # dummy layer to generate the stack
                except ValueError:
                    pass
            else:  # sample thickness is in the tb
                try:
                    o_reso.add_layer(formula=sample_tb_df[constants.chem_name][layer_index],
                                     thickness=float(sample_tb_df[constants.thick_name][layer_index]))
                except ValueError:
                    pass
        elif sample_tb_df[constants.density_name][layer_index] == '':  # sample density name is in the tb
            try:  # sample density is NOT in the tb
                o_reso.add_layer(formula=sample_tb_df[constants.chem_name][layer_index],
                                 thickness=float(sample_tb_df[constants.thick_name][layer_index]))
            except ValueError:
                pass
        else:  # sample density is in the tb
            try:
                o_reso.add_layer(formula=sample_tb_df[constants.chem_name][layer_index],
                                 thickness=float(sample_tb_df[constants.thick_name][layer_index]),
                                 density=float(sample_tb_df[constants.density_name][layer_index]))
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
        constants.layer_name: lay_list,
        constants.ele_name: ele_list,
        constants.iso_name: iso_list,
        constants.iso_ratio_name: iso_ratio_list,
    })
    return _df


def update_new_iso_table(prev_iso_df: pd.DataFrame, new_iso_df: pd.DataFrame):
    prev_iso_layer_list = list(prev_iso_df[constants.layer_name])  # previous list of layers
    new_iso_layer_list = list(new_iso_df[constants.layer_name])  # new list of layers

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