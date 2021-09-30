from mabs.ka.ka_s.base import KaLocal
import copy
from numpy import random
import mabs.utils.utilities as utils

class HillClimb(KaLocal):
    
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.avg_diff_limit = 5
        self.step_size = 0.1
        self.step_rate = 0.1
        self.step_limit = 100
        self.convergence_criteria = 0.001
        self.hc_type = 'simple'
        self._class = 'local search hc'
        
    def calculate_derivative(self, base_dv, base_obj, step_design, dv, obj):
        obj_dict = self._objectives[obj]
        dv_dict = self._design_variables[dv]
        if obj_dict['variable type'] == float:
            if step_design['objective functions'][obj] <= obj_dict['ll'] or step_design['objective functions'][obj] >= obj_dict['ul']:
                return -1000.0
    
        obj_scaled_new = utils.convert_objective_to_minimize(obj_dict, utils.scale_value(step_design['objective functions'][obj], obj_dict), scale=True)
        obj_scaled_base = utils.convert_objective_to_minimize(obj_dict, utils.scale_value(base_obj[obj], obj_dict), scale=True) 
        dv_scaled_new = utils.scale_value(step_design['design variables'][dv], dv_dict) if ('options' not in dv_dict.keys() and 'permutation' not in dv_dict.keys()) else 1.0
        dv_scaled_base = utils.scale_value(base_dv[dv], dv_dict) if ('options' not in dv_dict.keys() and 'permutation' not in dv_dict.keys()) else 0.0
        
        # We are following the steepest ascent, so positive is better
        obj_diff = (obj_scaled_base - obj_scaled_new)
        dv_diff = abs(dv_scaled_new - dv_scaled_base)
        derivative = obj_diff / dv_diff if dv_diff != 0 else 0
        #TODO: Fix this at sometime
        return round(derivative, 10)        
        #return derivative        

        
    def determine_step(self, base, base_design, design_dict):
        """
        Determine which design we should use to take a step, based on a scaled derivative (objectives and dv are scaled)
        """
        design = {}
        best_design = {}
        best_design['total'] = 0

        design_list = [x for x in design_dict.keys()]
        if self.hc_type == 'simple':
            random.shuffle(design_list)

        for pert_dv in design_list:
            pert_design = design_dict[pert_dv]
            dv = pert_dv.split(' ')[1]
            design[pert_dv] = {}
            design[pert_dv]['total'] = 0
            for obj, obj_dict in self._objectives.items():
                derivative = self.calculate_derivative(base, base_design, pert_design, dv, obj)
                design[pert_dv][obj] = derivative
                design[pert_dv]['total'] += derivative
                                    
            violated = False
            for constraint, val in pert_design['constraints'].items():
                constraint_dict = self._constraints[constraint]
                violated = utils.test_limits(val, constraint_dict) if type(val) == (float or int) else self.test_list_limits(val, constraint_dict)
            if design[pert_dv]['total'] > 0 and design[pert_dv]['total'] > best_design['total'] and not violated:
                best_design = design[pert_dv]
                best_design['pert'] = pert_dv
             
        if best_design['total'] > 0:
            return (best_design['pert'], best_design['total'])
        else:
            return (None, None)
    
    def search_method(self):
        """
        Basic hill climbing algorithm for local search.
        
        Searches local area by taking some x number of steps to determine a more optimal solution.
        
        1. Cycle through each DV and increment/decrement by step_value
        2. Determine which DV has the steepest descent
        2a. If no increase descent, decrease step size
        2b. If increase descent, increase step size; Replace design with current DV
        3a. If step_size < some value exit
        3b. Else, repeat 
        """
        core = None
        entry = None

        core = self.select_core()
        if core == False:
            return
        entry = self.lvl_read[core]
            
        step = self.step_size
        step_design = self._lvl_data[core]['design variables']
        step_objs = self._lvl_data[core]['objective functions']
        step_number = 0
        
        while step > self.convergence_criteria:
            gradient_vector = {}
            next_step = None
            potential_steps = []
            permutation_samples = 5
            # Calculate our gradient vector
            for dv, dv_dict in self._design_variables.items():
                dv_type = type(step_design[dv])
                if 'permutation' in dv_dict:
                    idx = range(len(self._design_variables[dv]))
                    for perm_step in range(permutation_samples):
                        temp_design = copy.copy(step_design)
                        i1, i2 = random.choice(idx, size=2, replace=False)
                        temp_design[dv][i1], temp_design[dv][i2] = temp_design[dv][i2], temp_design[dv][i1]
                        potential_steps.append((str(perm_step), dv, temp_design))
                        
                elif 'options' in dv_dict:
                    temp_design = copy.copy(step_design)
                    options = copy.copy(dv_dict['options'])
                    options.remove(step_design[dv])
                    temp_design[dv] = dv_type(random.choice(options))
                    potential_steps.append(('+', dv, temp_design))
                elif dv_dict['variable type'] == float:
                    for direction in ['+', '-']:
                        temp_design = copy.copy(step_design)
                        temp_design[dv] += temp_design[dv] * step if direction == '+' else temp_design[dv] * -step
                        temp_design[dv] = round(temp_design[dv], self._design_accuracy)
                        if temp_design[dv] >= dv_dict['ll'] and temp_design[dv] <= dv_dict['ul']:
                            potential_steps.append((direction, dv, temp_design))
            if self.hc_type == 'simple':
                random.shuffle(potential_steps)
                
            while len(potential_steps) != 0:
                direction, dv, design = potential_steps.pop()
                self._entry_name = self.get_design_name(design)
                self.current_design_variables = design 
                if self.determine_model_applicability(dv):
                    if self.parallel and self.hc_type != 'simple':
                        self.parallel_executor()
                    else:
                        self.calc_objectives()
                        if self.determine_write_to_bb():
                            gradient_vector['{} {}'.format(direction,dv)] = {'design variables': self.current_design_variables, 
                                                                     'objective functions': {k:v for k,v in self.current_objectives.items()},
                                                                     'constraints': self.current_constraints}
                    if self.hc_type == 'simple':
                        test_step = {'{} {}'.format(direction,dv): gradient_vector['{} {}'.format(direction,dv)]}
                        next_step, diff = self.determine_step(step_design, step_objs, test_step)
                        if next_step:
                            step_design = gradient_vector[next_step]['design variables']
                            step_objs = gradient_vector[next_step]['objective functions']
                            break
                if self.kill_switch:
                    break
            if self.parallel and self.hc_type != 'simple':
                self.determine_parallel_complete()
            if self.kill_switch:
                break
            
            # Determine which step is the steepest, update our design, and write this to the BB
            if gradient_vector and self.hc_type != 'simple':
                next_step, diff = self.determine_step(step_design, step_objs, gradient_vector)
                if next_step:
                    step_design = gradient_vector[next_step]['design variables']
                    step_objs = gradient_vector[next_step]['objective functions']
            
            #If we don't have a gradient vector or a next step to take, reduce the step size
            if gradient_vector == {} or next_step == None:
                step = step * (1 - self.step_rate)
            step_number += 1
            if step_number > self.step_limit:
                break
     