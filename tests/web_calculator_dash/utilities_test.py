import unittest

from _utilities import *


class TestValidators(unittest.TestCase):
    database = '_data_for_unittest'
    compos_row_tb = [{'Chemical formula': 'B4C', 'Weight (g)': '50'}, {'Chemical formula': 'SiC', 'Weight (g)': '49'}]
    iso_row_tb = [{'Layer': 'B4C', 'Element': 'B', 'Isotope': '10-B', 'Isotopic ratio': 0.199},
                  {'Layer': 'B4C', 'Element': 'B', 'Isotope': '11-B', 'Isotopic ratio': 0.801},
                  {'Layer': 'B4C', 'Element': 'C', 'Isotope': '12-C', 'Isotopic ratio': 0.9893},
                  {'Layer': 'B4C', 'Element': 'C', 'Isotope': '13-C', 'Isotopic ratio': 0.0107},
                  {'Layer': 'SiC', 'Element': 'Si', 'Isotope': '28-Si', 'Isotopic ratio': 0.9223},
                  {'Layer': 'SiC', 'Element': 'Si', 'Isotope': '29-Si', 'Isotopic ratio': 0.0468},
                  {'Layer': 'SiC', 'Element': 'Si', 'Isotope': '30-Si', 'Isotopic ratio': 0.0309},
                  {'Layer': 'SiC', 'Element': 'C', 'Isotope': '12-C', 'Isotopic ratio': 0.9893},
                  {'Layer': 'SiC', 'Element': 'C', 'Isotope': '13-C', 'Isotopic ratio': 0.0107}]

    def test_is_element_in_database(self):
        """assert is_element_in_database works correctly for good and bad input elements"""
        pass
