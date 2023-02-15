from dash.dependencies import Input, Output, State


from app import app
from callbacks.utilities.initialization import init_app_ids
import callbacks.utilities.constants as constants
from callbacks.utilities.all_apps import (create_table_output_file_name, format_data,
                                          clean_data_tab)

from callbacks.utilities.bragg import parse_cif_file, parse_txt_file
from callbacks.utilities.constants import *


app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)


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
        Output(app_id_dict['texture_table_tab1'], 'data'),
        Output(app_id_dict['texture_checklist_tab1'], 'value'),
        Output(app_id_dict['grain_size_input_tab1'], 'value'),
        Output(app_id_dict['grain_size_checklist_tab1'], 'value'),
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
        State(app_id_dict['texture_checklist_tab1'], 'value'),
        State(app_id_dict['texture_table_tab1'], 'data'),
        State(app_id_dict['texture_table_tab1'], 'columns'),
        State(app_id_dict['grain_size_checklist_tab1'], 'value'),
        State(app_id_dict['grain_size_input_tab1'], 'value'),
        State(app_id_dict['a_tab1'], 'value'),
        State(app_id_dict['b_tab1'], 'value'),
        State(app_id_dict['c_tab1'], 'value'),
        State(app_id_dict['alpha_tab1'], 'value'),
        State(app_id_dict['beta_tab1'], 'value'),
        State(app_id_dict['gamma_tab1'], 'value'),
    ],
)
def upload_feedback(cif_names, add_button_timestamp, texture_add_button_timestamp,
                    prev_upload_time, file_uploads, content_of_table, names_of_columns, prev_texture_add_row_time,
                    texture_checklist_flag, texture_content_of_table, names_of_texture_columns,
                    grain_size_checklist_flag, grain_size_value,
                    a, b, c, alpha, beta, gamma):

    data_fb_list = []
    error_div_list = []

    # input and output checklist values do not have the same format
    # when input is Null, output should be [None]

    grain_size_checklist_flag = [None] if not grain_size_checklist_flag else grain_size_checklist_flag
    texture_checklist_flag = [None] if not texture_checklist_flag else texture_checklist_flag

    # grain_size_checklist_flag = [None, constants.grain_size_flag]

    # we did not import a cif name, we need to add a row
    if cif_names is None:

        if add_button_timestamp != prev_upload_time:
            # we need to add a row in the top table
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, a, b, c, alpha, beta, gamma, \
                   texture_add_button_timestamp, texture_content_of_table, texture_checklist_flag, \
                   grain_size_value, grain_size_checklist_flag
        else:
            # we need to add a row in the texture table
            texture_content_of_table.append({c['id']: '' for c in names_of_texture_columns})
            return [None], [None], content_of_table, add_button_timestamp, a, b, c, alpha, beta, gamma, \
                   texture_add_button_timestamp, texture_content_of_table, texture_checklist_flag, \
                   grain_size_value, grain_size_checklist_flag

    # we are importing a file
    if file_uploads is not None:

        if add_button_timestamp != prev_upload_time:
            # we really clicked the add a row button
            content_of_table.append({c['id']: '' for c in names_of_columns})
            return [None], [None], content_of_table, add_button_timestamp, a, b, c, alpha, beta, gamma, \
                   texture_add_button_timestamp, texture_content_of_table, texture_checklist_flag, \
                   grain_size_value, grain_size_checklist_flag

        elif texture_add_button_timestamp != prev_texture_add_row_time:
            texture_content_of_table.append({c['id']: '' for c in names_of_texture_columns})
            return [None], [None], content_of_table, add_button_timestamp, a, b, c, alpha, beta, gamma, \
                   texture_add_button_timestamp, texture_content_of_table, texture_checklist_flag, \
                   grain_size_value, grain_size_checklist_flag

        # we did not click add a row button
        content_of_table = []
        texture_content_of_table = []

        if cif_names.endswith('.cif'):
            _cif_struc, texture_list, grain_size = parse_cif_file(content=file_uploads)
        elif cif_names.endswith('.txt'):
            _cif_struc, texture_list, grain_size = parse_txt_file(content=file_uploads)

        # fill top structure table
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

        # fill texture table
        if texture_list:

            for _row_index, _texture in enumerate(texture_list):

                if _row_index == 0:
                    texture_checklist_flag = _texture.flag

                _new_table_entry = {constants.index_number_h: _texture.h,
                                    constants.index_number_k: _texture.k,
                                    constants.index_number_l: _texture.l,
                                    constants.r: _texture.r,
                                    constants.beta: _texture.beta}
                texture_content_of_table.append(_new_table_entry)

        # fill grain size
        if grain_size:

            grain_size_checklist_flag = grain_size.flag if grain_size.flag else None
            grain_size_value = grain_size.value

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
           prev_texture_add_row_time, \
           texture_content_of_table, texture_checklist_flag, \
           grain_size_value, grain_size_checklist_flag


# export
@app.callback(Output(app_id_dict["download_tab1"], "data"),
              Input(app_id_dict["download_button_tab1"], "n_clicks"),
              [
                  State(app_id_dict['data_table_tab1'], 'data'),
                  State(app_id_dict['texture_checklist_tab1'], 'value'),
                  State(app_id_dict['texture_table_tab1'], 'data'),
                  State(app_id_dict['grain_size_checklist_tab1'], 'value'),
                  State(app_id_dict['grain_size_input_tab1'], 'value'),
                  State(app_id_dict['a_tab1'], 'value'),
                  State(app_id_dict['b_tab1'], 'value'),
                  State(app_id_dict['c_tab1'], 'value'),
                  State(app_id_dict['alpha_tab1'], 'value'),
                  State(app_id_dict['beta_tab1'], 'value'),
                  State(app_id_dict['gamma_tab1'], 'value'),
              ],
              prevent_initial_call=True,
             )
def func(n_clicks, data_table, texture_flag, texture_table, grain_size_flag, grain_size_value,
         a, b, c, alpha, beta, gamma):

    cleaned_data_table = clean_data_tab(data_tab=data_table)

    _dict = {'table': cleaned_data_table,
             'a': a, 'b': b, 'c': c,
             'alpha': alpha, 'beta': beta, 'gamma': gamma,
             'grain_size': grain_size_value,
             'grain_size_flag': grain_size_flag,
             'texture_table': texture_table,
             constants.texture_flag: texture_flag}

    output_file_name = create_table_output_file_name(table=cleaned_data_table)
    if output_file_name is None:
        return None

    output_data = format_data(dict=_dict)

    return dict(content=output_data,
                filename=output_file_name)


# texture checklist
@app.callback([
                Output(app_id_dict['texture_add_row_tab1'], "disabled"),
                Output(app_id_dict['texture_table_tab1'], "editable"),
                ],
              Input(app_id_dict['texture_checklist_tab1'], "value"))
def method(checklist_tab1_value):

    # button is unchecked
    if len(checklist_tab1_value) == 1:
        return True, False

    else:
        return False, True


# grain size checklist
@app.callback(
    Output(app_id_dict['grain_size_input_tab1'], "disabled"),
    Input(app_id_dict['grain_size_checklist_tab1'], "value"))
def method_grain_size_tab1(checklist_value):

    # button is unchecked
    if len(checklist_value) == 1:
        return True

    return False

