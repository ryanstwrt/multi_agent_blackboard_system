import osbrain
from osbrain import Agent
import numpy as np
import random
import scipy.interpolate
import ka
import train_surrogate_models as tm
import copy
import database_generator as dg
import math

class KaRp(ka.KaBase):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    
    Attributes
    ----------
    _trigger_val : int
        Base trigger value to send to the blackboard to determine KA priority
    bb_lvl : int
        Abstract level that the Ka writes to

    """
    def on_init(self):
        super().on_init()
        self._trigger_val = 0
        self._base_trigger_val = 0.25
        self.bb_lvl = 3
        self._sm = None
        self.sm_type = 'interpolate'
        self.design_variables = {}
        self.current_design_variables = {}
        self._design_accuracy = 5
        self.objectives = {}
        self.objective_functions = {}
        self._objective_accuracy = 5
        
    def calc_objectives(self):
        """
        Calculate the objective functions based on the core design variables.
        This process is performed via an interpolator or a surrogate model.
        Sets the variables for the _entry and _entry_name
        """
        self.log_debug('Determining core parameters based on SM')
        design = [x for x in self.current_design_variables.values()]
        if 'benchmark' in self.sm_type:
            obj_list = self._sm.predict(self.sm_type.split()[0], design, len(design), len(self.objectives.keys()))
            for num, obj in enumerate(self.objectives.keys()):
                self.objective_functions[obj] = round(float(obj_list[num]), self._objective_accuracy)
        elif self.sm_type == 'interpolate':
            for obj_name, interpolator in self._sm.items():
                self.objective_functions[obj_name] = round(float(interpolator(tuple(design))), self._objective_accuracy)
        else:
            obj_list = self._sm.predict(self.sm_type, [design])
            for num, obj in enumerate(self.objectives.keys()):
                self.objective_functions[obj] = round(float(obj_list[0][num]), self._objective_accuracy)
        a = self.current_design_variables.copy()
        a.update(self.objective_functions)
        self.log_debug('Core Design & Objectives: {}'.format([(x,round(y, self._objective_accuracy)) for x,y in a.items()]))
        self._entry_name = 'core_{}'.format([x for x in self.current_design_variables.values()])
        self._entry = {'reactor parameters': a}
        
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB.
        
        Parameter
        ---------
        message : str
            required message for sending communication
        """
        self.log_debug('Executing agent {}'.format(self.name))
        self.mc_design_variables()
        self.calc_objectives()
        self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel='new')
        self._trigger_val = 0
        
    def handler_trigger_publish(self, message):
        """
        Send a message to the BB indiciating it's trigger value.
        
        Parameters
        ----------
        message : str
            Containts unused message, but required for agent communication.
        """
        self._trigger_val += self._base_trigger_val
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
    
    def scale_objective(self, val, ll, ul):
        """Scale an objective based on the upper/lower"""
        return (val - ll) / (ul - ll)

class KaRpExplore(KaRp):
    """
    Knowledge agent to solve portions reactor physics problems using a SM.
    
    Inherets from KaBase.
    
    Attibutes:

    design_variables : dict
        Dictionary of the independent design variables for the current design (key - variable name, value - variable value)
    objective_funcionts : dict
        Dictionary of the objective functions for the current design (key - objective name, value - objective value)
    objectives : list
        List of the objective name for optimization
    design_variables : dict
        Dictionary of design variables for the problem and allowable rannge for the variables (key - variable name, value - tuple of min/max value)
    _sm : dict/trained_sm class
        Reference to the surrogate model that is used for determining objective functions.
        This can either be a scipy interpolator or a sci-kit learn regression function.
    sm_type : str
        Name of the surrogate model to be used.
        Valid options: (interpolator, lr, pr, gpr, mars, ann, rf)
        See surrogate_modeling for more details
    """

    def on_init(self):
        super().on_init()
        
    def mc_design_variables(self):
        """
        Determine the core design variables using a monte carlo method.
        """
        for dv, dv_dict in self.design_variables.items():
            self.current_design_variables[dv] = round(random.random() * (dv_dict['ul'] - dv_dict['ll']) + dv_dict['ll'], self._design_accuracy)
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))


class KaLocal(KaRp):
    """
    Knowledge agent to solve portions reactor physics problems using a SM.
    
    Inherets from KaBase.
    
    Attibutes
    ---------
    All inherited attributes from KaRp
    
    bb_lvl_read : int
        Abstract level that the Ka reads from to gather information
    perturbations : list of floats
        List of values to perturb each independent variable by
    new_panel : str
        Name of the panel where new information can be found 
    old_panel : str
        Name of the panel where information that has already been examined can be found
    """

    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5
        self.bb_lvl_read = 1
        self.perturbation_size = 0.05
        self._design_accuracy = 5
        self._fitness_selection_fraction = 0.7
        self.avg_diff_limit = 5
        self.new_panel = 'new'
        self.old_panel = 'old'
        self.lvl_data = None
        self.lvl_read = None
        self.analyzed_design = {}

    def determine_model_applicability(self, dv, complete=False):
        """
        Determine if a design variable is valid, and if the design has already been examined.
        If the design isn't valid or has already been examined, skip this.
        If the design is new, calculate the objectives and wrtie this to the blackbaord.
        """
        dv_dict = self.design_variables[dv]
        dv_cur_val = self.current_design_variables[dv]
        if dv_cur_val < dv_dict['ll'] or dv_cur_val > dv_dict['ul']:
            self.log_debug('Core {} not examined; design outside design variables.'.format([x for x in self.current_design_variables.values()]))
        elif 'core_{}'.format([x for x in self.current_design_variables.values()]) in self.lvl_data.keys():
            self.log_debug('Core {} not examined; found same core in Level {}'.format([x for x in self.current_design_variables.values()], self.bb_lvl))
        else:
            self.calc_objectives()
            self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel='new', complete=complete)
            self.log_debug('Perturbed variable {} with value {}'.format(dv, dv_cur_val))    
        
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        
        KA will perturb the core via the perturbations method and write all results the BB
        """
        self.log_debug('Executing agent {}'.format(self.name))
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        self.lvl_data = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]['old']
        self.search_method()
                      
    def handler_trigger_publish(self, message):
        """
        Read the BB level and determine if an entry is available.
        
        Paremeters
        ----------
        message : str
            Required message from BB
        
        Returns
        -------
        send : message
            _trigger_response_alias : int
                Alias for the trigger response 
            name : str
                Alias for the agent, such that the trigger value get assigned to the right agent on the BB
            _trigger_val : int
                Trigger value for knowledge agent
        """
        new_entry = self.read_bb_lvl()
        self._trigger_val = self._base_trigger_val if new_entry else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def search_method(self):
        """
        Perturb a core design
        
        This first selects a core at random from abstract level 1 (from the 'new' panel).
        It then perturbs each design variable independent by the values in perturbations, this produces n*m new cores (n = # of design variables, m = # of perturbations)
        
        These results are written to the BB level 3, so there are design_vars * pert added to level 3.
        """
        core, entry = random.choice(list(self.lvl_read.items()))

        design_ = {k: self.lvl_data[core]['reactor parameters'][k] for k in self.design_variables.keys()}
        perts = [1.0 - self.perturbation_size, 1.0 + self.perturbation_size]
        for dv, dv_value in design_.items():
            for pert in perts:
                design = copy.copy(design_)
                design[dv] = round(dv_value * pert, self._design_accuracy)
                self.current_design_variables = design
                self.determine_model_applicability(dv, complete=False)
        self.move_entry(self.bb_lvl_read, core, entry, self.old_panel, self.new_panel, write_complete=True)
        self.analyzed_design[core] = {'Analyzed': True}
        
    def genetic_algorithm(self):
        """
        Basic genetic algorithm for expediting our search
        """
        pass
    
    def read_bb_lvl(self):
        """
        Determine if there are any 'new' entries on level 1.
        
        Returns
        -------
            True -  if level has entries
            False -  if level is empty
        """
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        return True if lvl != {} else False
    
class KaLocalHC(KaLocal):
    
    def on_init(self):
        super().on_init()
        self.step_size = 0.05
        self.step_rate = 0.1
        self.step_limit = 100
        self.convergence_criteria = 0.005
        self.hc_type = 'steepest descent'
        
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

        core, entry = random.choice(list(self.lvl_read.items()))

        step = self.step_size
        design_ = {k: self.lvl_data[core]['reactor parameters'][k] for k in self.design_variables.keys()}
        design_objs = {k: self.lvl_data[core]['reactor parameters'][k] for k in self.objectives.keys()}
        step_number = 0
        hc_log = {}
        avg_diff = 0
        prev_avg = 1
        
        while step > self.convergence_criteria:
            steepest_dict = {}
            for dv in self.design_variables:
                for direction in ['+', '-']:
                    temp_design = copy.copy(design_)
                    if direction == '+':
                        temp_design[dv] += temp_design[dv] * step
                    else:
                        temp_design[dv] -= temp_design[dv] * step
                    temp_design[dv] = round(temp_design[dv], 5)
                    
                    if temp_design[dv] >= self.design_variables[dv]['ll'] and temp_design[dv] <= self.design_variables[dv]['ul']:
                        self.current_design_variables = temp_design
                        self.calc_objectives()
                        steepest_dict['{} {}'.format(direction,dv)] = {'design variables': temp_design, 
                                                                       'objective functions': {k:round(v,3) for k,v in self.objective_functions.items()}}
            if steepest_dict:
                next_step, diff = self.determine_step(design_, design_objs, steepest_dict)
                if next_step:
                    hc_log[step_number] = diff
                    avg_diff = sum(hc_log.values()) / len(hc_log)
                    prev_avg = avg_diff
                    design_ = steepest_dict[next_step]['design variables']
                    design_objs = steepest_dict[next_step]['objective functions']
                    self.current_design_variables = {k:v for k,v in steepest_dict[next_step]['design variables'].items()}
                    self.determine_model_applicability(next_step.split(' ')[1], complete=False)
                    
                if len(hc_log) > self.avg_diff_limit:
                    step = round(step * (1-self.step_rate),5) if abs(1 - avg_diff/prev_avg) < step else step
                if next_step == None:
                    step = round(step * (1-self.step_rate),5)
            else:
                step = round(step * (1-self.step_rate), 5)
            hc_log.pop(list(hc_log)[0]) if len(hc_log) > self.avg_diff_limit else hc_log
            step_number += 1
            if step_number > self.step_limit:
                break
        self.move_entry(self.bb_lvl_read, core, entry, self.old_panel, self.new_panel, write_complete=True) 
        self.analyzed_design[core] = {'Analyzed': True}

    def determine_step(self, base, base_design, design_dict):
        """
        Determine which design we should use to take a step, based on a scaled derivative (objectives and dv are scaled)
        """
        design = {}
        best_design = {}
        best_design['total'] = 0
        for pert_dv, dict_ in design_dict.items():
            dv = pert_dv.split(' ')[1]
            design[pert_dv] = {}
            design[pert_dv]['total'] = 0
            for name, obj in self.objectives.items():
                base_obj = base_design[name]
                new_obj = dict_['objective functions'][name]
                if new_obj >= self.objectives[name]['ll'] and new_obj <= self.objectives[name]['ul']:
                    obj_scaled_new = self.scale_objective(new_obj, self.objectives[name]['ll'], self.objectives[name]['ul'])
                    obj_scaled_base = self.scale_objective(base_obj, self.objectives[name]['ll'], self.objectives[name]['ul'])
                    
                    dv_scaled_new = self.scale_objective(base[dv], self.design_variables[dv]['ll'], self.design_variables[dv]['ul'])
                    dv_scaled_base = self.scale_objective(design_dict[pert_dv]['design variables'][dv], self.design_variables[dv]['ll'], self.design_variables[dv]['ul'])
        
                    obj_diff = (obj_scaled_new - obj_scaled_base) if obj['goal'] == 'gt' else (obj_scaled_base - obj_scaled_new)
                    dv_diff = abs(dv_scaled_new- dv_scaled_base)
                    derivative = obj_diff / dv_diff
                    design[pert_dv][name] = derivative
                    design[pert_dv]['total'] += derivative

            if design[pert_dv]['total'] > 0 and design[pert_dv]['total'] > best_design['total']:
                best_design = design[pert_dv]
                best_design['pert'] = pert_dv
                
        if best_design['total'] > 0:
            return (best_design['pert'], best_design['total'])
        else:
            return (None, None)
        
class KaLocalRW(KaLocal):
    
    def on_init(self):
        super().on_init()
        self.step_size = 0.01
        self.walk_length = 10
        
    def search_method(self):
        """
        Basic random walk algorithm for searching around a viable design.
        """
        core, entry = random.choice(list(self.lvl_read.items()))
        design = {k: self.lvl_data[core]['reactor parameters'][k] for k in self.design_variables.keys()}
        
        for x in enumerate(range(self.walk_length)):
            dv = random.choice(list(self.design_variables))
            step = round(random.random() * self.step_size, self._design_accuracy)
            direction = random.choice(['+','-'])
            design[dv] = design[dv] + step if direction == '+' else design[dv] - step
            design[dv] = round(design[dv], self._design_accuracy)
            self.log_debug('Design Variable: {} Step: {} {}\n New Design: {}'.format(dv, direction, step, design))
            self.current_design_variables = design
            self.determine_model_applicability(dv, complete=False)
        self.move_entry(self.bb_lvl_read, core, entry, self.old_panel, self.new_panel, write_complete=True)
        self.analyzed_design[core] = {'Analyzed': True}