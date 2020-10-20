import src.outputInterface as OI
import os
import numpy as np

def test_init():
    interface = OI.OutputReader(r'test/mcnp_output/test_interface.txt')
    assert interface.output == ['Test Interface\n', '\n', 'More Testing']
    assert interface.burnup == False
    assert interface.cycles == 0
    assert interface.cycle_dict == {}
    assert interface.core_name == 'test_interface'
    
def test_convert_rx_params():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    assert interface.core_name == 'FC_FS65_H75_23Pu4U10Zr_BU'
    interface.cycle_dict['step_12'] = {}
    interface.scrap_rx_params(interface.output[268454:268454+83], 12)
    interface.convert_rx_params()
    step_0 = interface.cycle_dict['step_12']['rx_parameters']
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
    assert step_0['precursor 1'][0] == {'beta-eff': 0.00011, 'beta-eff unc': 0.00002, 'energy': 0.41927, 'energy unc': 0.00198, 'energy_units': 'MeV', 'lambda-i': 0.01334, 'lambda-i unc': 0.00000, 'lambda-i_units': '(/sec)', 'half-life': 51.95717, 'half-life_units': '(sec)'}
    assert step_0['precursor 2'][0] == {'beta-eff': 0.00065, 'beta-eff unc': 0.00006, 'energy': 0.51754, 'energy unc': 0.00079, 'energy_units': 'MeV', 'lambda-i': 0.03129, 'lambda-i unc': 0.00000, 'lambda-i_units': '(/sec)', 'half-life': 22.14974, 'half-life_units': '(sec)'}
    assert step_0['precursor 3'][0] == {'beta-eff': 0.00064, 'beta-eff unc': 0.00007, 'energy': 0.42396, 'energy unc': 0.00081, 'energy_units': 'MeV', 'lambda-i': 0.11741, 'lambda-i unc': 0.00001,  'lambda-i_units': '(/sec)', 'half-life': 5.90386, 'half-life_units': '(sec)'}
    assert step_0['precursor 4'][0] == {'beta-eff': 0.00134, 'beta-eff unc': 0.00010, 'energy': 0.53274, 'energy unc': 0.00073, 'energy_units': 'MeV', 'lambda-i': 0.30523, 'lambda-i unc': 0.00002,  'lambda-i_units': '(/sec)', 'half-life': 2.27088, 'half-life_units': '(sec)'}
    assert step_0['precursor 5'][0] == {'beta-eff': 0.00060, 'beta-eff unc': 0.00006, 'energy': 0.49371, 'energy unc': 0.00101, 'energy_units': 'MeV', 'lambda-i': 0.87600, 'lambda-i unc': 0.00006,  'lambda-i_units': '(/sec)', 'half-life': 0.79126, 'half-life_units': '(sec)'}
    assert step_0['precursor 6'][0] == {'beta-eff': 0.00020, 'beta-eff unc': 0.00004, 'energy': 0.53827, 'energy unc': 0.00194, 'energy_units': 'MeV', 'lambda-i': 2.90154, 'lambda-i unc': 0.00056,  'lambda-i_units': '(/sec)', 'half-life': 0.23889, 'half-life_units': '(sec)'}

    
def test_scrap_rx_params():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    assert interface.core_name == 'FC_FS65_H75_23Pu4U10Zr_BU'
    interface.cycle_dict['step_12'] = {}
    interface.scrap_rx_params(interface.output[268454:268454+83], 12)
    step_0 = interface.cycle_dict['step_12']['rx_parameters']
    assert step_0['keff'] == 1.13466
    assert step_0['keff_unc'] == 0.00014
    assert step_0['prompt_removal_lifetime'] == (4.1290E-06, 1.6569E-09, 'seconds')
    assert step_0['avg_n_lethargy_fission'] == (7.4123E-01, 'mev')
    assert step_0['avg_n_energy_fission'] == (1.6782E-01, 'mev')
    assert step_0['thermal_fission_frac'] == (0.01)
    assert step_0['epithermal_fission_frac'] == (32.46)
    assert step_0['fast_fission_frac'] == (67.54)
    assert step_0['avg_n_gen_per_abs_fission'] == (1.882)
    assert step_0['avg_n_gen_per_abs_all'] == (1.2989)
    assert step_0['avg_n_gen_per_fission'] == (2.891)
 
    assert step_0['lifespan_esc'] == (1.79522E-06)
    assert step_0['lifespan_capt'] == (7.63721E-06)
    assert step_0['lifespan_fission'] == (5.72704E-07)
    assert step_0['lifespan_rem'] == (4.12287E-06)
    assert step_0['frac_esc'] == (1.27694E-01)
    assert step_0['frac_capt'] == (4.80438E-01)
    assert step_0['frac_fission'] == (3.91868E-01)
    assert step_0['frac_rem'] == (1.00000E+00)

    assert step_0['generation_time'] == (421.27908, 5.11714, ' (nsec)\n')
    assert step_0['rossi-alpha'] == (-8.41612E-06, 3.76984E-07, ' (/nsec)\n')
    assert step_0['beta'] == (0.00355, 0.00015)
    assert step_0['precursors'] == {1: {'beta-eff': 0.00011, 'beta-eff unc': 0.00002, 'energy': 0.41927, 'energy unc': 0.00198, 'energy_units': 'MeV', 'lambda-i': 0.01334, 'lambda-i unc': 0.00000, 'lambda-i_units': '(/sec)', 'half-life': 51.95717, 'half-life_units': '(sec)'},
                                    2: {'beta-eff': 0.00065, 'beta-eff unc': 0.00006, 'energy': 0.51754, 'energy unc': 0.00079, 'energy_units': 'MeV', 'lambda-i': 0.03129, 'lambda-i unc': 0.00000, 'lambda-i_units': '(/sec)', 'half-life': 22.14974, 'half-life_units': '(sec)'},
                                    3: {'beta-eff': 0.00064, 'beta-eff unc': 0.00007, 'energy': 0.42396, 'energy unc': 0.00081, 'energy_units': 'MeV', 'lambda-i': 0.11741, 'lambda-i unc': 0.00001,  'lambda-i_units': '(/sec)', 'half-life': 5.90386, 'half-life_units': '(sec)'},
                                    4: {'beta-eff': 0.00134, 'beta-eff unc': 0.00010, 'energy': 0.53274, 'energy unc': 0.00073, 'energy_units': 'MeV', 'lambda-i': 0.30523, 'lambda-i unc': 0.00002,  'lambda-i_units': '(/sec)', 'half-life': 2.27088, 'half-life_units': '(sec)'},
                                    5: {'beta-eff': 0.00060, 'beta-eff unc': 0.00006, 'energy': 0.49371, 'energy unc': 0.00101, 'energy_units': 'MeV', 'lambda-i': 0.87600, 'lambda-i unc': 0.00006,  'lambda-i_units': '(/sec)', 'half-life': 0.79126, 'half-life_units': '(sec)'},
                                    6: {'beta-eff': 0.00020, 'beta-eff unc': 0.00004, 'energy': 0.53827, 'energy unc': 0.00194, 'energy_units': 'MeV', 'lambda-i': 2.90154, 'lambda-i unc': 0.00056,  'lambda-i_units': '(/sec)', 'half-life': 0.23889, 'half-life_units': '(sec)'}}

def test_get_global_parameters():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    assert interface.core_name == 'FC_FS65_H75_23Pu4U10Zr_BU'
    interface.get_global_parameters()
    assert interface.cycle_dict['step_0']['rx_parameters']['keff'][0] == 1.20837
    assert interface.cycle_dict['step_1']['rx_parameters']['keff'][0] == 1.19608
    assert interface.cycle_dict['step_2']['rx_parameters']['keff'][0] == 1.18370
    assert interface.cycle_dict['step_3']['rx_parameters']['keff'][0] == 1.17161
    assert interface.cycle_dict['step_4']['rx_parameters']['keff'][0] == 1.15918
    assert interface.cycle_dict['step_5']['rx_parameters']['keff'][0] == 1.14671
    assert interface.cycle_dict['step_6']['rx_parameters']['keff'][0] == 1.13466
    
def test_scrap_assembly_power():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    interface.cycles = 7
    for x in range(interface.cycles):
        interface.cycle_dict['step_{}'.format(x)] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'] = {}
        
    interface.scrap_assembly_power(interface.output[269920:269920+4+7])
    assert interface.cycle_dict['step_0']['assemblies'] == {1902: {'duration': 0.0,
                                                       'time': 0.0,
                                                       'power fraction': 9.960E-3,
                                                       'burnup': 0.0}}
    assert interface.cycle_dict['step_6']['assemblies'] == {1902: {'duration': 50.0,
                                                       'time': 300.0,
                                                       'power fraction': 1.027E-2,
                                                       'burnup': 2.961E+1}}

def test_get_assembly_parameters():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    interface.cycles = 7
    for x in range(interface.cycles):
        interface.cycle_dict['step_{}'.format(x)] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'] = {}
    interface.get_assembly_parameters()
    assem = interface.cycle_dict['step_0']['assemblies'][122]
    assert interface.cycle_dict['step_0']['assemblies'][122]['power fraction'] == 1.765E-2
    assert interface.cycle_dict['step_0']['assemblies'][122]['actinide inventory']['mass'][92235] == 1204
    assert interface.cycle_dict['step_0']['assemblies'][1902]['power fraction']== 9.960E-3    
    assert interface.cycle_dict['step_6']['assemblies'][1902]['duration'] == 50.0
    assert interface.cycle_dict['step_6']['assemblies'][1902]['time'] == 300.0
    assert interface.cycle_dict['step_6']['assemblies'][1902]['power fraction'] ==1.027E-2
    assert interface.cycle_dict['step_6']['assemblies'][1902]['burnup'] == 2.961E+1
    assert interface.cycle_dict['step_6']['assemblies'][1902]['actinide inventory']['mass'][92235] == 1.059E3
    assert interface.cycle_dict['step_6']['assemblies'][1902]['actinide inventory']['mass fraction'][96244] == 7.470E-10
    
def test_scrap_assembly_nuclide_data():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    interface.cycles = 7
    for x in range(interface.cycles):
        interface.cycle_dict['step_{}'.format(x)] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'][122] = {}
    interface.scrap_assembly_nuclide_data(interface.output[269933:269933+interface.cycles*33], 122)
    assert interface.cycle_dict['step_0']['assemblies'][122]['actinide inventory'][92235] == {'mass': 1.204E3, 
                                                                                              'activity': 0.0,
                                                                                              'specific activity': 0.0,
                                                                                              'atom density': 1.429E-3,
                                                                                              'atom fraction': 3.077E-2,
                                                                                              'mass fraction': 3.526E-2}
    assert interface.cycle_dict['step_1']['assemblies'][122]['actinide inventory'][92235] == {'mass': 1.163E3, 
                                                                                              'activity': 2.514E-3,
                                                                                              'specific activity': 2.161E-6,
                                                                                              'atom density': 1.381E-3,
                                                                                              'atom fraction': 2.976E-2,
                                                                                              'mass fraction': 3.423E-2}
    assert interface.cycle_dict['step_6']['assemblies'][122]['actinide inventory'][92235] == {'mass': 9.713E2, 
                                                                                              'activity': 2.099E-3,
                                                                                              'specific activity': 2.161E-6,
                                                                                              'atom density': 1.153E-3,
                                                                                              'atom fraction': 2.484E-2,
                                                                                              'mass fraction': 2.917E-2}

def test_convert_assembly_params():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out')
    interface.cycles = 7
    for x in range(interface.cycles):
        interface.cycle_dict['step_{}'.format(x)] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'] = {}
        interface.cycle_dict['step_{}'.format(x)]['assemblies'][122] = {}

    interface.scrap_assembly_nuclide_data(interface.output[269933:269933+interface.cycles*33], 122)
    interface.convert_assembly_params()
    assert interface.cycle_dict['step_0']['assemblies'][122]['actinide inventory']['mass'][92235] == 1204
    assert interface.cycle_dict['step_6']['assemblies'][122]['actinide inventory']['mass fraction'][92235] == 2.917E-02

def test_read_inputfile():
    interface = OI.OutputReader(r'test/mcnp_output/FC_FS65_H75_23Pu4U10Zr_BU.out', burnup=True)
    interface.read_input_file()
    assert interface.cycle_dict['step_0']['rx_parameters']['keff'][0] == 1.20837
    assert interface.cycle_dict['step_6']['rx_parameters']['keff'][0] == 1.13466
    assert interface.cycle_dict['step_0']['rx_parameters']['keff unc'][0] == 0.00016    
    assert interface.cycle_dict['step_6']['rx_parameters']['keff unc'][0] == 0.00014  
    print(interface.cycle_dict['step_0'].keys())
    assem_0 = interface.cycle_dict['step_0']['assemblies'][142]
    assert assem_0['power fraction'] == 1.763E-2
    assert assem_0['actinide inventory']['mass'][92235] == 1204
    assert assem_0['actinide inventory']['mass fraction'][92235] == 3.526E-2

    assem_1 = interface.cycle_dict['step_6']['assemblies'][1882]
    assert assem_1['burnup'] == 3.164E1
    assert assem_1['actinide inventory']['mass'][92235] == 1.047E3
    assert assem_1['actinide inventory']['mass fraction'][92235] == 3.116E-2
    
    