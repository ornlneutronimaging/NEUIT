import unittest

from _utilities import *


class TestUtilities(unittest.TestCase):
    database = '_data_for_unittest'
    compos_row_tb = [{'Chemical formula': 'B4C', 'Weight (g)': '50'}, {'Chemical formula': 'SiC', 'Weight (g)': '49'}]
    iso_row_tb = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': 0.199},
                  {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 0.801},
                  {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                  {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                  {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                  {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                  {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                  {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                  {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]

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
        expected_df = pd.DataFrame([{'column_1': 'B4C', 'column_2': 1, 'column_3': ''},
                                    {'column_1': 'SiC', 'column_2': 1, 'column_3': ''}])
        test_df = pd.DataFrame([{'column_1': 'B4C', 'column_2': '50', 'column_3': '1'},
                                {'column_1': 'SiC', 'column_2': '50', 'column_3': '1'}])

        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

        test_df = pd.DataFrame([{'column_1': 'B4C', 'column_2': '50'},
                                {'column_1': 'SiC', 'column_2': '50'}])
        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

        test_df = pd.DataFrame([{'column_1': 'B4C', 'column_3': '1'},
                                {'column_1': 'SiC', 'column_3': '1'}])
        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

        test_df = pd.DataFrame([{'column_1': 'B4C', 'column_3': 1},
                                {'column_1': 'SiC', 'column_3': -1}])
        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

    def test_force_col_to_numeric(self):
        expected_list_df = pd.DataFrame([{'column_1': 'B4C', 'column_2': 50, 'column_3': 'A'},
                                         {'column_1': 'SiC', 'column_2': 50, 'column_3': 1}])
        expected_dict = expected_list_df.to_dict('list')

        test_dict_list = [{'column_1': 'B4C', 'column_2': '50', 'column_3': 'A'},
                          {'column_1': 'SiC', 'column_2': '50', 'column_3': '1'}]
        new_dict = force_dict_to_numeric(input_dict_list=test_dict_list)
        self.assertDictEqual(new_dict, expected_dict)

    def test_composition_tb_validator(self):
        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 1},
                          {'column_1': 'SiC', 'column_2': 50, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([True, True], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 'A'},
                          {'column_1': 'SiC', 'column_2': 50, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 'A'},
                          {'column_1': 'SiC', 'column_2': '50', 'column_3': '1'}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': -1},
                          {'column_1': 'SiC', 'column_2': 0, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

    def test_sample_tb_validator(self):
        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 1},
                          {'column_1': 'SiC', 'column_2': 50, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([True, True], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 'A'},
                          {'column_1': 'SiC', 'column_2': 50, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': 'A'},
                          {'column_1': 'SiC', 'column_2': '50', 'column_3': '1'}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 50, 'column_3': -1},
                          {'column_1': 'SiC', 'column_2': 0, 'column_3': 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

    def test_isotope_tb_validator(self):
        test_dict_list = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': 0.199},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 0.801},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=iso_dict_schema, input_df=test_df)
        expected_pass_list = [True, True, True, True, True, True, True, True, True]
        self.assertEqual(expected_pass_list, pass_list)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 12, 'column_3': '10-B', 'column_4': 0.199},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '', 'column_4': 0.801},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': '', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': -1},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': ''}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=iso_dict_schema, input_df=test_df)
        expected_pass_list = [False, False, True, False, True, False, True, True, False]
        self.assertEqual(expected_pass_list, pass_list)

    def test_isotope_tb_sum_validator(self):
        test_dict_list = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': 0.199},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 0.801},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual(True, passed)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': -1},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 0.801},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual(False, passed)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': 0.1},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 0.2},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual(False, passed)

        test_dict_list = [{'column_1': 'B4C', 'column_2': 'B', 'column_3': '10-B', 'column_4': 0},
                          {'column_1': 'B4C', 'column_2': 'B', 'column_3': '11-B', 'column_4': 1},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'B4C', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '28-Si', 'column_4': 0.9223},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '29-Si', 'column_4': 0.0468},
                          {'column_1': 'SiC', 'column_2': 'Si', 'column_3': '30-Si', 'column_4': 0.0309},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '12-C', 'column_4': 0.9893},
                          {'column_1': 'SiC', 'column_2': 'C', 'column_3': '13-C', 'column_4': 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual(True, passed)

    def test_chem_name_validator(self):
        self.assertTrue(validate_chem_name('Ag'))
        self.assertFalse(validate_chem_name('Dg'))
        self.assertFalse(validate_chem_name('Ci'))
        self.assertFalse(validate_chem_name('Xo'))
        self.assertFalse(validate_chem_name('Asd'))
        self.assertTrue(validate_chem_name('U2O3'))
        self.assertTrue(validate_chem_name('CH3COOH'))
        self.assertTrue(validate_chem_name('CuO2H2'))
        self.assertFalse(validate_chem_name('Hug'))
        self.assertFalse(validate_chem_name('AA'))
        self.assertFalse(validate_chem_name('ab'))
        self.assertFalse(validate_chem_name('dd'))
        self.assertFalse(validate_chem_name('Co1.2Cu1.4'))
        self.assertTrue(validate_chem_name('LiMg'))
        self.assertTrue(validate_chem_name('Li-Mg'))
        self.assertFalse(validate_chem_name('aa'))


