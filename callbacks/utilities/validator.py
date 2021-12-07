from cerberus import Validator
from dash import html
import pandas as pd

import ImagingReso._utilities as ir_util
from callbacks.utilities.database import update_database_key_in_schema
import callbacks.utilities.constants as constants

def is_number(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False


def _validate_chem_name(input_name: str, database: str):
    """ Returns True if string is a number. """
    try:
        ir_util.formula_to_dictionary(formula=input_name, database=database)
        return [True, None]
    except ValueError as error_massage:
        return [False, error_massage.__str__()]


def validate_input(v: Validator, input_dict: dict):
    passed = v.validate(input_dict)
    if passed:
        return passed, None
    else:
        error_message_str = v.errors
    return passed, html.P('INPUT ERROR: {}'.format(error_message_str))


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


def validate_no_duplicated_layer_name(sample_df: pd.DataFrame):
    """ Returns True when no duplicated layer name. """
    try:
        layer_list = sample_df[constants.chem_name].tolist()
        if len(layer_list) == len(set(layer_list)):
            return [True], [None]
        else:
            return [False], [html.P("INPUT ERROR: same '{}' has been entered more than once.".format(constants.chem_name))]
    except KeyError as error_massage:
        return [False], [error_massage.__str__()]


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
        df = iso_df.groupby([constants.layer_name, constants.ele_name]).sum()
        df_boo = df[constants.iso_ratio_name] - 1.0
        boo = df_boo.abs() >= 0.005
        failed_list = list(boo)
        passed_list = []
        div_list = []
        if any(failed_list):
            _list = df.index[boo].tolist()
            for _index, each_fail_layer in enumerate(_list):
                div = html.P("INPUT ERROR: '{}': [sum of isotopic ratios is '{}' not '1']".format(
                    str(each_fail_layer), float(df[boo][constants.iso_ratio_name][_index])))
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
    for _index, _each_formula in enumerate(sample_tb_df[constants.chem_name]):
        try:
            _parsed_dict = ir_util.formula_to_dictionary(_each_formula)
            _num_of_ele_in_formula = len(_parsed_dict[_each_formula]['elements'])
            if _num_of_ele_in_formula > 1 and sample_tb_df[constants.density_name][_index] == '':
                test_passed_list.append(False)
                output_div_list.append(
                    html.P("INPUT ERROR: '{}': ['Density input is required for compound '{}'.']".format(constants.density_name,
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
    if range_tb_df[constants.energy_name][0] == range_tb_df[constants.energy_name][1]:
        test_passed_list.append(False)
        output_div_list.append(
            html.P("INPUT ERROR: {}: ['Energy min. can not equal energy max.']".format(str(constants.energy_name))))
    else:
        test_passed_list.append(True)
        output_div_list.append(None)

    for each in range_tb_df[constants.energy_name]:
        if each < 1e-5 or each > 1e8:
            test_passed_list.append(False)
            output_div_list.append(
                html.P("INPUT ERROR: '{}': ['1x10^-5 <= 'Energy' <= 1x10^8']".format(str(constants.energy_name))))
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


class MyValidator(Validator):
    def _validate_greater_than_zero(self, greater_than_zero, field, value):
        """ Test if a value is greater but not equals to zero.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        _boo = bool(value > 0)
        if greater_than_zero and not _boo:
            self._error(field, "'{}' must be greater than '0'".format(value))

    def _validate_between_zero_and_one(self, between_zero_and_one, field, value):
        """ Test if a value is "0 <= value <= 1"'.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        _boo = bool(0 <= value <= 1)
        if between_zero_and_one and not _boo:
            self._error(field, "'{}' must be a number between '0' and '1'".format(value))

    def _validate_empty_str(self, empty_str, field, value):
        """ Test when input type is str, the value must be an empty str.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if type(value) is str:
            _boo = bool(value == '')
            if empty_str and not _boo:
                self._error(field,
                            "'{}' must be a number >= '0' or leave as 'blank' to use natural density".format(value))

    def _validate_ENDF_VIII(self, ENDF_VIII, field, value):
        """ Test if the value is a valid chemical formula.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not is_number(value):
            __validated_result = _validate_chem_name(value, database='ENDF_VIII')
            _boo = __validated_result[0]
            if ENDF_VIII and not _boo:
                self._error(field, __validated_result[1])
        else:
            self._error(field, "must be a valid 'chemical formula', input is case sensitive")

    def _validate_ENDF_VII(self, ENDF_VII, field, value):
        """ Test if the value is a valid chemical formula.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not is_number(value):
            __validated_result = _validate_chem_name(value, database='ENDF_VII')
            _boo = __validated_result[0]
            if ENDF_VII and not _boo:
                self._error(field, __validated_result[1])
        else:
            self._error(field, "must be a valid 'chemical formula', input is case sensitive")
