from cerberus import Validator
from dash import html

import ImagingReso._utilities as ir_util


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
