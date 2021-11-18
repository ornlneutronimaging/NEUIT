def make_ascii_file(metadata=[], data=[], output_file_name=''):
    """
    create an ascii file with the following format
            # metadata1
            # metadata2
            #
            data_row1
            data_row2

    metadata: array
    data: array
    output_file_name: string
    """
    f = open(output_file_name, 'w')
    for _meta in metadata:
        _line = "# " + _meta + "\n"
        f.write(_line)

    f.write("#")

    for _data in data:
        _line = str(_data) + '\n'
        f.write(_line)

    f.close()
