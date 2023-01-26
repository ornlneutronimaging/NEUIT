import base64
import sys

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser


def parse_cif_file(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    cif_s = decoded.decode('utf-8')
    p = getParser('cif')
    struc = p.parse(cif_s)
    struc.sg = p.spacegroup
    return struc


def parse_csv_file(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    csv_s = decoded.decode('utf-8')
    print(csv_s)

    cif_structure = {}

    return None
