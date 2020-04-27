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
                if var == 'doppler':
                    obj_vars.append(rx_.get_doppler_coefficient()/300)
                elif var == 'void':
                    obj_vars.append(rx_.get_void_coefficient())
                elif var == 'cycle length':
                    a = rx_.extrapolate_value('keff', 'time', 1.0)
                    a = a.flat[0]
                    obj_vars.append(a)
                elif var == 'pu fraction':
                    obj_vars.append(rx_.rx['independent variables']['pu_fraction'][0])
                elif var == 'keff':
                    obj_vars.append(rx_.rx_step_params['step_0']['keff'][0])
            ind_var_array.append(tuple(ind_vars))
            obj_var_array.append(tuple(obj_vars))
        except:
            pass
    
    return ind_var_array, obj_var_array