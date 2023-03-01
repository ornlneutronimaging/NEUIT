import base64
import sys
import json

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser

from .constants import (index_number_l, index_number_k, index_number_h,
                        index_number_a, index_number_b, index_number_c,
                        r, beta, texture_flag,
                        interaxial_angle_beta, interaxial_angle_gamma, interaxial_angle_alpha,
                        chem_name)



def parse_cif_file(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    cif_s = decoded.decode('utf-8')
    p = getParser('cif')
    struc = p.parse(cif_s)
    struc.sg = p.spacegroup
    return struc, None, None


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


class Texture:
    h = None
    k = None
    l = None
    r = None
    beta = None
    flag = None

    def __init__(self, h=None, k=None, l=None, r=None, beta=None, flag=None):
        self.h = h
        self.k = k
        self.l = l
        self.r = r
        self.beta = beta
        self.flag = flag


class GrainSize:
    flag = None
    value = None

    def __init__(self, flag=None, value=None):
        self.flag = flag
        self.value = value


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
                               x=_entry[index_number_a],
                               y=_entry[index_number_b],
                               z=_entry[index_number_c])
        cif_structure.append(_structure)

    if len(dictionary[texture_flag]) == 2:
        _texture_flag = dictionary[texture_flag]
    else:
        _texture_flag = [None]

    texture_table = dictionary['texture_table']
    texture_list = []
    for _index, _entry in enumerate(texture_table):

        _texture = Texture(h=_entry[index_number_h],
                           k=_entry[index_number_k],
                           l=_entry[index_number_l],
                           r=_entry[r],
                           beta=_entry[beta],
                           flag=_texture_flag)
        texture_list.append(_texture)

    grain_size = GrainSize(value=dictionary['grain_size'],
                           flag=dictionary['grain_size_flag'])

    return cif_structure, texture_list, grain_size
