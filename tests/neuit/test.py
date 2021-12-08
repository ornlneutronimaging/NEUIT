import unittest

from callbacks.utilities._utilities import *
from callbacks.utilities.validator import (_validate_chem_name, validate_input_tb_rows, validate_sum_of_iso_ratio)
from callbacks.utilities.constants import *


class TestUtilities(unittest.TestCase):
    database = '_data_for_unittest'

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

    def test_creat_sample_df_from_compos_df(self):
        expected_df = pd.DataFrame([{chem_name: 'B4C', thick_name: 1, density_name: ''},
                                    {chem_name: 'SiC', thick_name: 1, density_name: ''}])
        test_df = pd.DataFrame([{chem_name: 'B4C', compos_2nd_col_id: '50'},
                                {chem_name: 'SiC', compos_2nd_col_id: '50'}])

        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

        test_df = pd.DataFrame([{chem_name: 'B4C', compos_2nd_col_id: 1},
                                {chem_name: 'SiC', compos_2nd_col_id: -1}])
        new_df = creat_sample_df_from_compos_df(compos_tb_df=test_df)
        self.assertTrue(new_df.equals(expected_df))

    def test_force_col_to_numeric(self):
        expected_list_df = pd.DataFrame([{chem_name: 'B4C', compos_2nd_col_id: 'A'},
                                         {chem_name: 'SiC', compos_2nd_col_id: 50}])
        expected_dict = expected_list_df.to_dict('list')

        test_dict_list = [{chem_name: 'B4C', compos_2nd_col_id: 'A'},
                          {chem_name: 'SiC', compos_2nd_col_id: '50'}]
        new_dict = force_dict_to_numeric(input_dict_list=test_dict_list)
        self.assertDictEqual(new_dict, expected_dict)

    def test_composition_tb_validator(self):
        test_dict_list = [{chem_name: 'B4C', compos_2nd_col_id: 50},
                          {chem_name: 'SiC', compos_2nd_col_id: 50}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([True, True], pass_list)

        test_dict_list = [{chem_name: 'B4C', compos_2nd_col_id: 'A'},
                          {chem_name: 'SiC', compos_2nd_col_id: 50}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

        test_dict_list = [{chem_name: 'B4C', compos_2nd_col_id: 'A'},
                          {chem_name: 'SiC', compos_2nd_col_id: '50'}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

        test_dict_list = [{chem_name: 'B4C', compos_2nd_col_id: -1},
                          {chem_name: 'SiC', compos_2nd_col_id: 0}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=compos_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

    def test_sample_tb_validator(self):
        test_dict_list = [{chem_name: 'B4C', thick_name: 50, density_name: 1},
                          {chem_name: 'SiC', thick_name: 50, density_name: 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([True, True], pass_list)

        test_dict_list = [{chem_name: 'B4C', thick_name: 50, density_name: 'A'},
                          {chem_name: 'SiC', thick_name: 50, density_name: 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

        test_dict_list = [{chem_name: 'B4C', thick_name: 50, density_name: 'A'},
                          {chem_name: 'SiC', thick_name: '50', density_name: '1'}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, False], pass_list)

        test_dict_list = [{chem_name: 'B4C', thick_name: 50, density_name: -1},
                          {chem_name: 'SiC', thick_name: 0, density_name: 1}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=sample_dict_schema, input_df=test_df)
        self.assertEqual([False, True], pass_list)

    def test_isotope_tb_validator(self):
        test_dict_list = [{layer_name: 'B4C', ele_name: 'B', iso_name: '10-B', iso_ratio_name: 0.199},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '11-B', iso_ratio_name: 0.801},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: 0.0468},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0.0309},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=iso_dict_schema, input_df=test_df)
        expected_pass_list = [True, True, True, True, True, True, True, True, True]
        self.assertEqual(expected_pass_list, pass_list)

        test_dict_list = [{layer_name: 'B4C', ele_name: 12, iso_name: '10-B', iso_ratio_name: 0.199},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '', iso_ratio_name: 0.801},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: '', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: -1},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: ''}]
        test_df = pd.DataFrame(test_dict_list)
        pass_list, output_div_list = validate_input_tb_rows(schema=iso_dict_schema, input_df=test_df)
        expected_pass_list = [False, False, True, False, True, False, True, True, False]
        self.assertEqual(expected_pass_list, pass_list)

    def test_isotope_tb_sum_validator(self):
        test_dict_list = [{layer_name: 'B4C', ele_name: 'B', iso_name: '10-B', iso_ratio_name: 0.199},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '11-B', iso_ratio_name: 0.801},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: 0.0468},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0.0309},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual([True], passed)

        test_dict_list = [{layer_name: 'B4C', ele_name: 'B', iso_name: '10-B', iso_ratio_name: -1},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '11-B', iso_ratio_name: 0.801},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: 0.0468},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0.0309},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual([False], passed)

        test_dict_list = [{layer_name: 'B4C', ele_name: 'B', iso_name: '10-B', iso_ratio_name: 0.1},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '11-B', iso_ratio_name: 0.2},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: 0.0468},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0.0309},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual([False], passed)

        test_dict_list = [{layer_name: 'B4C', ele_name: 'B', iso_name: '10-B', iso_ratio_name: 0},
                          {layer_name: 'B4C', ele_name: 'B', iso_name: '11-B', iso_ratio_name: 1},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'B4C', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '28-Si', iso_ratio_name: 0.9223},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '29-Si', iso_ratio_name: 0.0468},
                          {layer_name: 'SiC', ele_name: 'Si', iso_name: '30-Si', iso_ratio_name: 0.0309},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '12-C', iso_ratio_name: 0.9893},
                          {layer_name: 'SiC', ele_name: 'C', iso_name: '13-C', iso_ratio_name: 0.0107}]
        test_df = pd.DataFrame(test_dict_list)
        passed, output_div = validate_sum_of_iso_ratio(iso_df=test_df)
        self.assertEqual([True], passed)

    def test_chem_name_validator(self):
        database_endf7 = 'ENDF_VII'
        database_endf8 = 'ENDF_VIII'
        self.assertTrue(_validate_chem_name('Ag', database=database_endf7)[0])
        self.assertTrue(_validate_chem_name('U2O3', database=database_endf7)[0])
        self.assertTrue(_validate_chem_name('CH3COOH', database=database_endf7)[0])
        print(ir_util.formula_to_dictionary('CH3COOH'))
        self.assertTrue(_validate_chem_name('CuO2H2', database=database_endf7)[0])
        self.assertTrue(_validate_chem_name('LiMg', database=database_endf7)[0])
        self.assertTrue(_validate_chem_name('Li-Mg', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('88', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Dg', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Ci', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Xo', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Asd', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Hug', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('AA', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('ab', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('dd', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('Co1.2Cu1.4', database=database_endf7)[0])
        self.assertFalse(_validate_chem_name('aa', database=database_endf7)[0])
        # self.assertFalse(validate_chem_name('aO'))  # need to work on restricting this type of input
        print(ir_util.formula_to_dictionary('aO'))
        # self.assertFalse(validate_chem_name('H2o'))  # need to work on restricting this type of input
        print(ir_util.formula_to_dictionary('H2o'))
        # Test database used
        self.assertTrue(_validate_chem_name('Pt', database=database_endf8)[0])
        self.assertFalse(_validate_chem_name('Pt', database=database_endf7)[0])
