import unittest

from _utilities import *


class TestUtilities(unittest.TestCase):
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

    def test_classify_neutron(self):
        """assert neutron classifier works correctly"""
        neutron_class = classify_neutron(2.4e-7)
        self.assertEqual(neutron_class, 'Ultra-cold')
        neutron_class = classify_neutron(0.02)
        self.assertEqual(neutron_class, 'Cold')
        neutron_class = classify_neutron(0.04)
        self.assertEqual(neutron_class, 'Thermal')
        neutron_class = classify_neutron(0.21)
        self.assertEqual(neutron_class, 'Epithermal')
        neutron_class = classify_neutron(0.01)
        self.assertNotEqual(neutron_class, 'Epithermal')
        neutron_class = classify_neutron(901)
        self.assertEqual(neutron_class, 'Intermediate')
        neutron_class = classify_neutron(0.51e6)
        self.assertEqual(neutron_class, 'Fast')
        neutron_class = classify_neutron(20.1e6)
        self.assertEqual(neutron_class, 'Ultra-fast')

    def test_drop_df_column_not_needed(self):
        """assert correct column has been dropped"""
        test_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': ['50', '50'],
            'column_3': ['1', '1'],
        })
        expected_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_3': ['1', '1'],
        })
        new_df = drop_df_column_not_needed(input_df=test_df, column_name='column_2')
        self.assertEqual(new_df.to_dict('list'), expected_df.to_dict('list'))

    def test_creat_sample_df_from_compos_df(self):
        test_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': ['50', '50'],
            'column_3': ['1', '1'],
        })
        expected_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': [1, 1],
            'column_3': [np.nan, np.nan],
        })
        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

    def test_force_col_to_numeric(self):
        test_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': ['50', '50'],
            'column_3': ['A', '1'],
        })
        expected_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': [50, 50],
            'column_3': ['A', '1'],
        })
        new_df = force_col_to_numeric(input_df=test_df, col_name='column_2')
        self.assertTrue(new_df.equals(expected_df))

        # test 'ignore' when str and number appear
        expected_df = pd.DataFrame({
            'column_1': ['B4C', 'SiC'],
            'column_2': ['50', '50'],
            'column_3': ['A', '1'],
        })
        new_df = force_col_to_numeric(input_df=test_df, col_name='column_3')
        self.assertTrue(new_df.equals(expected_df))

    def test_validate_input_loop(self):
        # Test compos validator
        test_df = pd.DataFrame({
            'column_1': ['B4C', 2123, 'B4C', 'B4C', 'B4C'],
            'column_2': [1, 1, '50', 1, 1],
            'column_3': [1, 1, 1, '50', ''],
        })
        expected_passed_list = [True, False, False, False, False]
        passed_list, div_list = validate_input_loop(schema=compos_dict_schema, input_rows=test_df)
        print(passed_list)
        print(div_list)
        self.assertEqual(passed_list, expected_passed_list)

        # Test sample validator
        test_df = pd.DataFrame({
            'column_1': ['B4C', 2123, 'B4C', 'B4C', 'B4C'],
            'column_2': [1, 1, '50', 1, 1],
            'column_3': [1, 1, 1, '50', ''],
        })
        expected_passed_list = [True, False, False, False, False]
        passed_list, div_list = validate_input_loop(schema=compos_dict_schema, input_rows=test_df)
        print(passed_list)
        print(div_list)
        self.assertEqual(passed_list, expected_passed_list)
