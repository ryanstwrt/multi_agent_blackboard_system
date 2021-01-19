import src.database_generator as dbg
import pandas as pd
import pickle

def test_dbg():
    design_variables = ['height', 'smear', 'pu_content']
    objective_functions = ['reactivity swing', 'burnup', 'pu mass', 'cycle length', 'bol keff', 'eol keff', 'doppler', 'void', 'cycle length', 'excess reactivity']

    out = dbg.get_data(design_variables, objective_functions, 
                                 database_name='db_test', fixed_cycle_length=False, num_cycles=4, path='test/mcnp_output/', output='dict')
    assert out == {'/FS65_H75_23Pu4U10Zr': {'independent variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.875}, 'dependent variables': {'reactivity swing': 602.4030176530645, 'burnup': 430.156354505801, 'pu mass': 156.24960000000002, 'cycle length': 858.7551867219967, 'bol keff': 1.20837, 'eol keff': 1.0, 'doppler': -0.45124404126092305, 'void': -60.34416518672346, 'excess reactivity': 0.0}}}
    
    out_var, out_obj = dbg.get_data(design_variables, objective_functions, 
                                 database_name='db_test', fixed_cycle_length=False, num_cycles=4, path='test/mcnp_output/', output='list')
    assert out_var == [(75.0, 65.0, 0.875)]
    assert out_obj == [(602.4030176530645, 430.156354505801, 156.24960000000002, 858.7551867219967, 1.20837, 1.0, -0.45124404126092305, -60.34416518672346, 858.7551867219967, 0.0)]
    
    df_dv, df_obj = dbg.get_data(design_variables, objective_functions, 
                                 database_name='db_test', fixed_cycle_length=False, num_cycles=4, path='test/mcnp_output/', output='DataFrame')
    assert df_dv.equals(pd.DataFrame([(75.0, 65.0, 0.875)], columns=design_variables)) == True
    assert df_obj.equals(pd.DataFrame([(602.4030176530645, 430.156354505801, 156.24960000000002, 858.7551867219967, 1.20837, 1.0, -0.45124404126092305, -60.34416518672346, 858.7551867219967, 0.0)], columns=objective_functions)) == True