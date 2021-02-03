import src.h5Interface as h5i
import src.reactorInterface as RI
import pandas as pd

def get_data(design_variables, objective_variables, database_name='SFR_DB', fixed_cycle_length=120, num_cycles=4, path=None, output='list'):
    h5_interface = h5i.h5Interface()
    if path:
        h5_interface.read_h5('{}/{}.h5'.format(path,database_name))        
    else:
        h5_interface.read_h5('/Users/ryanstewart/projects/sfr_database/{}.h5'.format(database_name))
    ind_var_array = []
    obj_var_array = []
    data_dict = {}
    for core in h5_interface.h5file.values():
        core_name = core.name
        data_dict[core_name] = {'independent variables': {}, 'dependent variables': {}}
        try:
            rx_ = RI.reactorInterface(core)
            ind_vars = []
            for var in design_variables:
                ind_vars.append(rx_.rx['independent variables'][var][0])
                data_dict[core_name]['independent variables'][var] = rx_.rx['independent variables'][var][0]
            obj_vars = []
            cycle_length = rx_.extrapolate_value('keff', 'time', 1.0) if fixed_cycle_length == False else fixed_cycle_length

            for var in objective_variables:
                if var == 'doppler':
                    obj_vars.append(rx_.get_doppler_coefficient()/300)
                    data_dict[core_name]['dependent variables'][var] = rx_.get_doppler_coefficient()/300
                elif var == 'void':
                    obj_vars.append(rx_.get_void_coefficient())
                    data_dict[core_name]['dependent variables'][var] = rx_.get_void_coefficient()
                elif var == 'cycle length':
                    obj_vars.append(cycle_length)
                    data_dict[core_name]['dependent variables'][var] = cycle_length
                elif var == 'pu fraction':
                    obj_vars.append(rx_.rx['independent variables']['pu_fraction'][0])
                    data_dict[core_name]['dependent variables'][var] = rx_.rx['independent variables']['pu_fraction'][0]
                elif var == 'bol keff':
                    obj_vars.append(rx_.rx_step_params['step_0']['keff'][0])
                    data_dict[core_name]['dependent variables'][var] = rx_.rx_step_params['step_0']['keff'][0]
                elif var == 'eol keff':
                    obj_vars.append(rx_.extrapolate_value('time', 'keff', cycle_length))
                    data_dict[core_name]['dependent variables'][var] = rx_.extrapolate_value('time', 'keff', cycle_length)
                elif var == 'reactivity swing':
                    rx_swing = rx_.get_reactivity_swing(0.0, cycle_length) * 30 / cycle_length
                    obj_vars.append(rx_swing)
                    data_dict[core_name]['dependent variables'][var] = rx_swing
                elif var == 'pu mass':
                    pu_mass = rx_.get_assembly_pu_mass() * 78 / (num_cycles)
                    obj_vars.append(pu_mass)
                    data_dict[core_name]['dependent variables'][var] = pu_mass
                elif var == 'burnup':
                    avg_bu = rx_.get_assembly_avg(cycle_length, 'burnup') * num_cycles
                    obj_vars.append(avg_bu)
                    data_dict[core_name]['dependent variables'][var] = avg_bu
                elif var == 'assembly power':
                    avg_pf = rx_.get_assembly_avg(cycle_length, 'power fraction') * 300
                    obj_vars.append(avg_pf)
                    data_dict[core_name]['dependent variables'][var] = avg_pf
                elif var == 'avg lhgr':
                    lhgr = rx_.get_assembly_avg(cycle_length, 'power fraction') * 300
                    # LHGR = power / (total length of fuel: pin length * # pins)
                    avg_lhgr = lhgr / (rx_.rx['independent variables']['height'][0] * 271)
                    obj_vars.append(avg_lhgr)
                    data_dict[core_name]['dependent variables'][var] = avg_lhgr
                elif var == 'max lhgr':
                    # convert to kw
                    lhgr = rx_.get_assembly_max(cycle_length, 'power fraction')[1] * 300 * 1000
                    # LHGR = power / (total length of fuel: pin length * # pins) 0.01 converts to m from cm
                    avg_lhgr = lhgr / (rx_.rx['independent variables']['height'][0] * 0.01 * 271) * 1.25
                    obj_vars.append(avg_lhgr)
                    data_dict[core_name]['dependent variables'][var] = avg_lhgr
                elif var == 'pu ratio':
                    pu_ratio_0 = rx_.get_assembly_avg(0, 'pu ratio')                    
                    pu_ratio_1 = rx_.get_assembly_avg(cycle_length * num_cycles, 'pu ratio')
                    # If statment is for pure uranium based fuel, set the pu ratio to 0, as we aren't burning it
                    pu_ratio = pu_ratio_1
                    obj_vars.append(pu_ratio)
                    data_dict[core_name]['dependent variables'][var] = pu_ratio   
                elif var == 'pu240 ratio':
                    pu_ratio_0 = rx_.get_assembly_avg(0, 'pu240 ratio')                    
                    pu_ratio_1 = rx_.get_assembly_avg(cycle_length * num_cycles, 'pu240 ratio')
                    pu_ratio =  pu_ratio_1
                    obj_vars.append(pu_ratio)
                    data_dict[core_name]['dependent variables'][var] = pu_ratio  
                elif var == 'pu disposed':
                    pu_disp_1 = rx_.get_assembly_avg(0, 'pu disposed')                          
                    pu_disp_2 = rx_.get_assembly_avg(cycle_length, 'pu disposed')
                    pu_disp = (pu_disp_1 - pu_disp_2) * 78 / num_cycles
                    obj_vars.append(pu_disp)
                    data_dict[core_name]['dependent variables'][var] = pu_disp                      
                elif var == 'excess reactivity':
                    eol_keff = rx_.extrapolate_value('time', 'keff', cycle_length)
                    excess = (eol_keff - 1.0) / (eol_keff) * 1E5
                    obj_vars.append(excess)
                    data_dict[core_name]['dependent variables'][var] = excess

            ind_var_array.append(tuple(ind_vars))
            obj_var_array.append(tuple(obj_vars))
        except:
            pass

    if output == 'dict':
        return data_dict
    elif output == 'list':
        return ind_var_array, obj_var_array
    elif output == 'DataFrame':
        return pd.DataFrame(ind_var_array, columns=design_variables), pd.DataFrame(obj_var_array, columns=objective_variables)
