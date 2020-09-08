import fridge.utilities.h5Interface as h5i
import fridge.utilities.reactorInterface as RI

def get_data(design_variables, objective_variables, database_name='SFR_DB', fixed_cycle_length=100):
    h5_interface = h5i.h5Interface()
    h5_interface.read_h5('/Users/ryanstewart/projects/sfr_database/{}.h5'.format(database_name))
    ind_var_array = []
    obj_var_array = []
    data_dict = {}
    num_cycles = 4
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
#                elif var == 'pu_content':
 #                   obj_vars.append(rx_.rx['independent variables']['pu_content'][0])
                elif var == 'excess reactivity':
                    given_cycle = rx_.extrapolate_value('keff', 'time', 1.0)
                    rx_swing_1 = rx_.get_reactivity_swing(0.0, cycle_length) * 30 / cycle_length
                    rx_swing_2 = rx_.get_reactivity_swing(0.0, given_cycle) * 30 / cycle_length
                    swing = rx_swing_1 - rx_swing_2
                    obj_vars.append(swing)
                    data_dict[core_name]['dependent variables'][var] = swing

            ind_var_array.append(tuple(ind_vars))
            obj_var_array.append(tuple(obj_vars))
        except:
            pass
    return ind_var_array, obj_var_array, data_dict