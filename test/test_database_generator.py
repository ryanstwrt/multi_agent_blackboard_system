import src.database_generator as dbg
import pickle

def test_dbg():
    design_variables = ['height', 'smear', 'pu_content']
    objective_functions = ['reactivity swing', 'burnup', 'pu mass', 'cycle length', 'bol keff', 'eol keff', 'doppler', 'void', 'cycle length', 'excess reactivity']

    ind_var, obj_var, data_dict = dbg.get_data(design_variables, objective_functions, 
                                 database_name='db_test', fixed_cycle_length=False, num_cycles=4, path='test/mcnp_output/')
    assert data_dict == {'/FS65_H75_23Pu4U10Zr': {'independent variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.875}, 'dependent variables': {'reactivity swing': 602.4030176530645, 'burnup': 435.742800668214, 'pu mass': 1435.9608786299002, 'cycle length': 858.7551867219967, 'bol keff': 1.20837, 'eol keff': 1.0, 'doppler': -0.45124404126092305, 'void': -60.34416518672346, 'excess reactivity': 0.0}}}