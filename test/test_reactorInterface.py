import src.utils.h5Interface as h5I
import src.utils.reactorInterface as rI
import os

h5_interface = h5I.h5Interface(output_name='reactor_interface')
h5_interface.create_h5()
for root, dirs, files in os.walk('test/mcnp_output/'):
    for file in files:
        if '.out' in file and 'checkpoint' not in file:
            h5_interface.add_reactor(file, path=root)  

rx = rI.reactorInterface(h5_interface.h5file['FS65_H75_23Pu4U10Zr'])

            
def test_init():
    assert rx.rx == h5_interface.h5file['FS65_H75_23Pu4U10Zr']
    assert rx.rx_name == 'FS65_H75_23Pu4U10Zr'
    for step, assem_step in zip(['step_0','step_1','step_2','step_3','step_4','step_5','step_6'], rx.assemblies.keys()):
        assert step == assem_step
    assert rx.rx_base == h5_interface.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr']['step_0']['rx_parameters']
    assert rx.rx_void == h5_interface.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_Void']['step_0']['rx_parameters']
    assert rx.rx_temp == h5_interface.h5file['FS65_H75_23Pu4U10Zr']['FS65_H75_23Pu4U10Zr_600K']['step_0']['rx_parameters']
    assert round(rx.density,4) == 15.8212
        
def test_get_assem_avg():
    avg_pow = rx.get_assembly_avg(300, 'power fraction')
    assert round(avg_pow, 6) == .012821
    avg_bu = rx.get_assembly_avg(300, 'burnup')
    assert round(avg_bu, 6) == 37.567179

def test_get_assem_min():
    min_pow = rx.get_assembly_min(300, 'power fraction')
    assert min_pow == ('1322', 9.136E-3)
    min_pow_2 = rx.get_assembly_min(0, 'power fraction')
    assert min_pow_2 == ('1522', 8.716E-3)
    min_bu = rx.get_assembly_min(300, 'burnup')
    assert min_bu == ('1722', 2.612E1)
    
def test_get_assem_max():
    max_pow = rx.get_assembly_max(300, 'power fraction')
    assert max_pow == ('122', 1.684E-2)
    max_pow_2 = rx.get_assembly_max(0, 'power fraction')
    assert max_pow_2 == ('222', 1.767E-2)
    max_bu = rx.get_assembly_max(300, 'burnup')
    assert max_bu == ('222', 5.070E1)

def test_get_peak_to_avg():
    peak_power = rx.get_peak_to_average(300, 'power fraction')
    assert (peak_power[0], round(peak_power[1],4)) == ('122', 1.3135)
    peak_bu = rx.get_peak_to_average(300, 'burnup')
    assert (peak_bu[0], round(peak_bu[1],4)) == ('222', 1.3496)

def test_get_doppler_coefficient():
    dopp = rx.get_doppler_coefficient()
    assert round(dopp,4) == round(-135.3732,4)
#    assert round(dopp,4) == round(-0.45121,4)

def test_get_void_coefficient():
    void = rx.get_void_coefficient()
    assert round(void,2) == -60.34
    
def test_extrapolate_value():
    cycle_length = rx.extrapolate_value('keff', 'time', 1.0)
    known_days1 = rx.extrapolate_value('time', 'keff', 300)
    known_days2 = rx.extrapolate_value('time', 'keff', 0)
    fast_fraction = rx.extrapolate_value('time', 'fast fission frac', 300)
    p_frac = rx.extrapolate_value('time', 'power fraction', 300, assem='122')

    assert known_days1 == 1.13466
    assert known_days2 == 1.20837
    assert round(cycle_length, 0) == 859
    assert round(fast_fraction, 4) == 0.6754
    assert p_frac == 1.684E-2
    
def test_get_reactivity_swing():
    rx_swing = rx.get_reactivity_swing(0, 300)
    assert round(rx_swing, 2) == 6099.95

def test_get_bu_list():
    time = rx.get_bu_list('time', False)
    keff = rx.get_bu_list('keff', False)
    power_fraction = rx.get_bu_list('power fraction', '122')
    
    assert time == [0,50,100,150,200,250,300]
    assert keff == [1.20837, 1.19608, 1.18370, 1.17161, 1.15918, 1.14671, 1.13466]
    assert power_fraction == [1.765E-2, 1.746E-2, 1.734E-2, 1.723E-2, 1.710E-2, 1.695E-2, 1.684E-2]

def test_get_assembly_to_avg():
    avg_pow = rx.get_assembly_to_avg(300, 'power fraction', '122')
    assert round(avg_pow, 4) == 1.3135
    avg_bu = rx.get_assembly_to_avg(300, 'burnup', '122')
    assert round(avg_bu, 4) == 1.3485

def test_get_pu_ratio():
    bu_list = rx.assemblies['step_0']['1002']['actinide inventory']
    pu_ratio = rx.get_pu_ratio(bu_list)
    assert round(pu_ratio,2) == 0.94

def test_get_pu240_pu239_ratio():
    bu_list = rx.assemblies['step_0']['1002']['actinide inventory']
    pu_ratio = rx.get_pu240_pu239_ratio(bu_list)
    assert round(pu_ratio,3) == 0.064
    
def test_get_pu_mass():
    pu_mass = rx.get_assembly_pu_mass()
    assert round(pu_mass,2) == 8.01
    
    
os.remove('reactor_interface.h5')