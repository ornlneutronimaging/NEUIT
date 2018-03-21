import glob
import os
import time
import io
import base64
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from numpy import exp, cos, linspace

from ImagingReso.resonance import Resonance
import ImagingReso._utilities as ir_util
from scipy.interpolate import interp1d


def init_reso(e_min, e_max, e_step):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    return o_reso


def add_layer(o_reso, layer, thickness_mm, density_gcm3):
    o_reso.add_layer(formula=layer, thickness=thickness_mm, density=density_gcm3)
    return o_reso


def load_beam_shape(relative_path_to_beam_shape):
    # _path_to_beam_shape = 'static/instrument_file/beam_shape_cg1d.txt'
    # Load beam shape from static
    df = pd.read_csv(relative_path_to_beam_shape, sep='\t', skiprows=0)
    df.columns = ['wavelength_A', 'flux']
    # Get rid of crazy data
    df.drop(df[df.wavelength_A < 0].index, inplace=True)
    df.drop(df[df.flux <= 0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Convert wavelength to energy
    energy_list = ir_util.angstroms_to_ev(df['wavelength_A'])
    df.insert(1, 'energy_eV', energy_list)
    return df
