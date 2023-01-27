import base64
import sys
import json

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser

from .constants import (index_number_l, index_number_k, index_number_h,
                        interaxial_angle_beta, interaxial_angle_gamma, interaxial_angle_alpha,
                        chem_name)



def parse_cif_file(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    cif_s = decoded.decode('utf-8')
    p = getParser('cif')
    struc = p.parse(cif_s)
    struc.sg = p.spacegroup
    return struc


class Lattice:
    alpha = None
    beta = None
    gamma = None

    a = None
    b = None
    c = None

    def __init__(self, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma


class Structure:
    element = None
    lattice = None
    x = None
    y = None
    z = None

    def __init__(self, element=None, lattice=None, x=None, y=None, z=None):
        self.element = element
        self.lattice = lattice
        self.x = x
        self.y = y
        self.z = z


def parse_txt_file(content):
    '''
    parse the ascii file (created by exporting the structure within each tab
    and create a structure that matches the cif structure
    '''
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    str_dictionary = decoded.decode('utf-8')
    dictionary = json.loads(str_dictionary)

    table = dictionary['table']
    cif_structure = []

    lattice = Lattice(a=dictionary['a'], b=dictionary['b'], c=dictionary['c'],
                      alpha=dictionary['alpha'], beta=dictionary['beta'], gamma=dictionary['gamma'])

    for _index, _entry in enumerate(table):

        _structure = Structure(element=_entry[chem_name],
                               lattice=lattice,
                               x=_entry[index_number_h],
                               y=_entry[index_number_k],
                               z=_entry[index_number_l])
        cif_structure.append(_structure)

    return cif_structure
