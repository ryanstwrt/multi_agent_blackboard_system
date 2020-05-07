import fridge.utilities.h5Interface as h5i
import fridge.utilities.reactorInterface as RI

def get_data(design_variables, objective_variables):
    h5_interface = h5i.h5Interface()
    h5_interface.read_h5('/Users/ryanstewart/projects/sfr_database/SFR_DB.h5')
    ind_var_array = []
    obj_var_array = []
    for core in h5_interface.h5file.values():
        try:
            rx_ = RI.reactorInterface(core)
            ind_vars = []
            for var in design_variables:
                ind_vars.append(rx_.rx['independent variables'][var][0])
            obj_vars = []
            for var in objective_variables:
                cycle_length = rx_.extrapolate_value('keff', 'time', 1.0)
                if var == 'doppler':
                    obj_vars.append(rx_.get_doppler_coefficient()/300)
                elif var == 'void':
                    obj_vars.append(rx_.get_void_coefficient())
                elif var == 'cycle length':
                    obj_vars.append(cycle_length)
                elif var == 'pu fraction':
                    obj_vars.append(rx_.rx['independent variables']['pu_fraction'][0])
                elif var == 'keff':
                    obj_vars.append(rx_.rx_step_params['step_0']['keff'][0])
                elif var == 'reactivity swing':
                    rx_swing = rx_.get_reactivity_swing(1.0, cycle_length) * 30 / cycle_length
                    obj_vars.append(rx_swing)
                elif var == 'pu mass':
                    pu_mass = rx_.get_assembly_pu_mass() * 78 / 4
                    obj_vars.append(pu_mass)
                elif var == 'burnup':
                    avg_bu = rx_.get_assembly_avg(cycle_length, 'burnup') * 30 / cycle_length
                    obj_vars.append(avg_bu)
            ind_var_array.append(tuple(ind_vars))
            obj_var_array.append(tuple(obj_vars))
        except:
            pass
    
    return ind_var_array, obj_var_array