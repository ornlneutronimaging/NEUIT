import callbacks.utilities.constants as constants


def update_database_key_in_schema(schema, database):
    _new_key = database
    try:
        _old_key = list(schema[constants.chem_name].keys())[3]
        if _new_key is not _old_key:
            schema[constants.chem_name][_new_key] = schema[constants.chem_name].pop(_old_key)
        return schema
    except KeyError:
        _old_key = list(schema[constants.layer_name].keys())[3]
        if _new_key is not _old_key:
            schema[constants.layer_name][_new_key] = schema[constants.layer_name].pop(_old_key)
        return schema
