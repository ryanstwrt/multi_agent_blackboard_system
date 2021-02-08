import src.utils.outputInterface as OI
import src.utils.h5Interface as h5I
import h5py
import os
import numpy as np

def test_init():
    I = h5I.h5Interface()
    assert I.mcnp_file_name == None
    assert I.h5File == None
    assert I.params == None
    assert I.core_name == None
    assert I.assembly_ind_vars == None
    assert I.dt_str == h5py.string_dtype(encoding='utf-8')

def test_get_core_name():
    I = h5I.h5Interface()
    I.params = ['FS65','H75','23Pu4U10Zr','BU']
    I.get_core_name()
    assert I.base_core == 'FS65_H75_23Pu4U10Zr'
    assert I.core_name == 'FS65_H75_23Pu4U10Zr_BU'

def test_create_h5():
    I = h5I.h5Interface()
    I.create_h5()
    assert os.path.exists('SFR_DB.h5') == True
    os.remove('SFR_DB.h5')
    
def test_add_reactor():
    I = h5I.h5Interface()
    I.create_h5()
    I.add_reactor(r'FC_FS65_H75_23Pu4U10Zr_BU.out',path=r'test/mcnp_output')    
    assert I.mcnp_file_name == 'FC_FS65_H75_23Pu4U10Zr_BU.out'
    assert I.core_name == 'FS65_H75_23Pu4U10Zr_BU'
    assert 'FS65_H75_23Pu4U10Zr_BU' in I.h5file['FS65_H75_23Pu4U10Zr'].keys()
    assert 'independent variables' in I.h5file['FS65_H75_23Pu4U10Zr'].keys()
    for i in [1,2,3,4,5,6]:
        assert 'step_{}'.format(i) in I.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU'].keys()
 
    ind_var =  I.h5file['FS65_H75_23Pu4U10Zr']['independent variables']
    assert ind_var['smear'][0] == 65
    assert ind_var['height'][0] == 75
    assert ind_var['pu_content'][0] == 0.875
    assert ind_var['u_content'][0] == (1-0.875)
    assert ind_var['condition'][0] == b'BU'

    step_0 = I.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU']['step_6']['rx_parameters']
    assert step_0['keff'][0] == 1.13466
    assert step_0['keff unc'][0] == 0.00014
    assert step_0['prompt removal lifetime'][0] == 4.1290E-06
    assert step_0['prompt removal lifetime unc'][0] == 1.6569E-09
    assert step_0['avg n lethargy fission'][0] == 7.4123E-01
    assert step_0['avg n energy fission'][0] == 1.6782E-01
    assert step_0['thermal fission frac'][0] == 0.0001
    assert step_0['epithermal fission frac'][0] == 0.3246
    assert np.allclose(step_0['fast fission frac'][0], 0.6754)
    assert step_0['avg n gen per abs fission'][0] == 1.882
    assert step_0['avg n gen per abs all'][0] == 1.2989
    assert step_0['avg n gen per fission'][0] == 2.891
    assert step_0['lifetime escape'][0] == 1.79522E-06
    assert step_0['lifetime capture'][0] == 7.63721E-06
    assert step_0['lifetime fission'][0] == 5.72704E-07
    assert step_0['lifetime removal'][0] == 4.12287E-06
    assert step_0['frac escape'][0] == 1.27694E-01
    assert step_0['frac capture'][0] == 4.80438E-01
    assert step_0['frac fission'][0] == 3.91868E-01
    assert step_0['frac removal'][0] == 1.00000E+00

    assert step_0['generation time'][0] == 421.27908*10E-9
    assert step_0['generation time unc'][0], 5.11714*10E-9
    assert step_0['rossi-alpha'][0] == -8.41612E-06/10E-9
    assert step_0['rossi-alpha unc'][0] == 3.76984E-07/10E-9
    assert step_0['beta'][0] == 0.00355
    assert step_0['beta unc'][0] == 0.00015
    assert step_0['precursor 1']['beta-eff'][0] == 0.00011
    assert step_0['precursor 1']['beta-eff unc'][0] == 0.00002
    assert step_0['precursor 1']['energy'][0] == 0.41927
    assert step_0['precursor 1']['energy unc'][0] == 0.00198
    assert step_0['precursor 1']['lambda-i'][0] == 0.01334
    assert step_0['precursor 1']['lambda-i unc'][0] == 0.00000
    assert step_0['precursor 1']['half-life'][0] == 51.95717

    assem_0 = I.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['142']
    assert assem_0['power fraction'][0] == 1.682E-2
    assert assem_0['burnup'][0] == 5.066E+1
    assert assem_0['actinide inventory']['92235'][0] == 9.714E2
    assert assem_0['actinide inventory']['92235'][-1] == 2.917E-2

    assem_1 = I.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['1882']
    assert assem_1['power fraction'][0] == 1.094E-2
    assert assem_1['burnup'][0] == 3.164E1
    assert assem_1['actinide inventory']['92235'][0] == 1.047E3
    assert assem_1['actinide inventory']['92235'][-1] == 3.116E-2
    os.remove('SFR_DB.h5')

def test_get_reactor_ind_vars():
    I = h5I.h5Interface()
    I.params = ['FS65','H75','23Pu4U10Zr','BU']
    I.get_reactor_ind_vars()
    assert I.assembly_ind_vars == {'smear': 65,
                                 'height': 75,
                                 'pu_content': 0.875,
                                 'u_content': (1-0.875),
                                 'condition': b'BU'}

def test_convert_rx_parameters():
    I = h5I.h5Interface()
    I.mcnp_file_name = 'FC_FS65_H75_23Pu4U10Zr_BU'
    I.params = I.mcnp_file_name.split('_')[1:]
    I.core_name = '_'.join(I.params)
    I.base_core = '_'.join(I.params)
    I.h5file = h5py.File(I.core_name + '.h5', 'w')
    I.outputInterface = OI.OutputReader('test/mcnp_output/{}.out'.format(I.mcnp_file_name), burnup=True)
    I.outputInterface.read_input_file()
    I.h5file.create_group(I.core_name)
    I.h5file[I.core_name].create_group(I.core_name)
    I.h5file[I.core_name][I.core_name].create_group('step_6')
    I.h5file[I.core_name][I.core_name]['step_6'].create_group('rx_parameters')
    I.h5file[I.core_name][I.core_name]['step_6'].create_group('assemblies')

    params = I.outputInterface.cycle_dict['step_6']
    for k,v in params.items():
        if k == 'rx_parameters':
            I.convert_rx_parameters(v, 'step_6')
    step_0 = I.h5file['FS65_H75_23Pu4U10Zr_BU']['FS65_H75_23Pu4U10Zr_BU']['step_6']['rx_parameters']
    assert step_0['keff'][0] == 1.13466
    assert step_0['keff unc'][0] == 0.00014
    assert step_0['prompt removal lifetime'][0] == 4.1290E-06
    assert step_0['prompt removal lifetime unc'][0] == 1.6569E-09
    assert step_0['avg n lethargy fission'][0] == 7.4123E-01
    assert step_0['avg n energy fission'][0] == 1.6782E-01
    assert step_0['thermal fission frac'][0] == 0.0001
    assert step_0['epithermal fission frac'][0] == 0.3246
    assert np.allclose(step_0['fast fission frac'][0], 0.6754)
    assert step_0['avg n gen per abs fission'][0] == 1.882
    assert step_0['avg n gen per abs all'][0] == 1.2989
    assert step_0['avg n gen per fission'][0] == 2.891
    assert step_0['lifetime escape'][0] == 1.79522E-06
    assert step_0['lifetime capture'][0] == 7.63721E-06
    assert step_0['lifetime fission'][0] == 5.72704E-07
    assert step_0['lifetime removal'][0] == 4.12287E-06
    assert step_0['frac escape'][0] == 1.27694E-01
    assert step_0['frac capture'][0] == 4.80438E-01
    assert step_0['frac fission'][0] == 3.91868E-01
    assert step_0['frac removal'][0] == 1.00000E+00

    assert step_0['generation time'][0] == 421.27908*10E-9
    assert step_0['generation time unc'][0], 5.11714*10E-9
    assert step_0['rossi-alpha'][0] == -8.41612E-06/10E-9
    assert step_0['rossi-alpha unc'][0] == 3.76984E-07/10E-9
    assert step_0['beta'][0] == 0.00355
    assert step_0['beta unc'][0] == 0.00015
    assert step_0['precursor 1']['beta-eff'][0] == 0.00011
    assert step_0['precursor 1']['beta-eff unc'][0] == 0.00002
    assert step_0['precursor 1']['energy'][0] == 0.41927
    assert step_0['precursor 1']['energy unc'][0] == 0.00198
    assert step_0['precursor 1']['lambda-i'][0] == 0.01334
    assert step_0['precursor 1']['lambda-i unc'][0] == 0.00000
    assert step_0['precursor 1']['half-life'][0] == 51.95717
    
def test_convert_assembly_parameters():
    I = h5I.h5Interface()
    I.mcnp_file_name = 'FC_FS65_H75_23Pu4U10Zr_BU'
    I.params = I.mcnp_file_name.split('_')[1:]
    I.core_name = '_'.join(I.params)
    I.base_core = '_'.join(I.params)
    I.h5file = h5py.File(I.core_name + '.h5', 'w')
    I.outputInterface = OI.OutputReader('test/mcnp_output/{}.out'.format(I.mcnp_file_name), burnup=True)
    I.outputInterface.read_input_file()
    I.h5file.create_group(I.core_name)
    I.h5file[I.core_name].create_group(I.core_name)
    I.h5file[I.core_name][I.core_name].create_group('step_6')
    I.h5file[I.core_name][I.core_name]['step_6'].create_group('rx_parameters')
    I.h5file[I.core_name][I.core_name]['step_6'].create_group('assemblies')
    params = I.outputInterface.cycle_dict['step_6']
    for k,v in params.items():
        if k == 'assemblies':
            I.convert_assembly_parameters(v, 'step_6')
    assem_0 = I.h5file['FS65_H75_23Pu4U10Zr_BU']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['142']
    assert assem_0['power fraction'][0] == 1.682E-2
    assert assem_0['burnup'][0] == 5.066E+1
    assert assem_0['actinide inventory']['92235'][0] == 9.714E2
    assert assem_0['actinide inventory']['92235'][-1] == 2.917E-2

    assem_1 = I.h5file['FS65_H75_23Pu4U10Zr_BU']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['1882']
    assert assem_1['power fraction'][0] == 1.094E-2
    assert assem_1['burnup'][0] == 3.164E1
    assert assem_1['actinide inventory']['92235'][0] == 1.047E3
    assert assem_1['actinide inventory']['92235'][-1] == 3.116E-2
    os.remove('FS65_H75_23Pu4U10Zr_BU.h5')
    
def test_create_database():
    h5_interface = h5I.h5Interface(output_name='db_test')
    h5_interface.create_h5()
    for root, dirs, files in os.walk('test/mcnp_output'):
        for file in files:
            if '.out' in file and 'checkpoint' not in file:
                try:
                    h5_interface.add_reactor(file, path=root)  
                except ValueError:
                    pass
    assem_1 = h5_interface.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['1882']
    assert assem_1['power fraction'][0] == 1.094E-2

def test_read_db():
    h5_interface = h5I.h5Interface()
    h5_interface.read_h5('db_test.h5')
    assem_1 = h5_interface.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_BU']['step_6']['assemblies']['1882']
    assert assem_1['power fraction'][0] == 1.094E-2
    os.remove('db_test.h5')
