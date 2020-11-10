import src.ka as ka
import src.performance_measure as pm
import src.train_surrogate_models as tm
import copy
import time
import numpy as np
from numpy import random
from math import factorial

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
        self._base_trigger_val = 0.250001
        self.bb_lvl_data = 3
        self._sm = None
        self.sm_type = 'interpolate'
        self._design_variables = {}
        self.current_design_variables = {}
        self._design_accuracy = 5
        self._objectives = {}
        self.current_objectives = {}
        self._objective_accuracy = 5
        self._constraints = {}
        self.current_constraints = {}
        self._constraint_accuracy = 5
        self._class = 'search'
        self._lvl_data = {}
        self.agent_time = 0
        self._trigger_event = 0
        
    def set_random_seed(self, seed=None):
        """
        Sets the random seed number to provide a reproducabel result
        """
        random.seed(seed=seed)
        
    def action_complete(self):
        """
        Send a message to the BB indicating it's completed its action
        """
        self.send(self._complete_alias, (self.name, self.agent_time, self._trigger_event))
        
    def calc_objectives(self):
        """
        Calculate the objective functions based on the core design variables.
        This process is performed via an interpolator or a surrogate model.
        Sets the variables for the _entry and _entry_name
        """
#        time.sleep(5)
        self.log_debug('Determining core parameters based on SM')
        design = [x for x in self.current_design_variables.values()]
        if 'benchmark' in self.sm_type:
            obj_list = self._sm.predict(self.sm_type.split()[0], design, len(design), len(self._objectives.keys()))
            for num, obj in enumerate(self._objectives.keys()):
                if self._objectives[obj]['variable type'] == float:
                    self.current_objectives[obj] = round(float(obj_list[num]), self._objective_accuracy)
                elif self._objectives[obj]['variable type'] == str:
                    self.current_objectives[obj] = str(obj_list[num])
        elif self.sm_type == 'interpolate':
            self.get_interpolate_objectives(design)
        else:
            self.get_sm_objectives()

        self._entry_name = self.get_design_name(self.current_design_variables)
        self._entry = {'design variables': self.current_design_variables, 
                       'objective functions': self.current_objectives,
                       'constraints': self.current_constraints}
        
    def get_design_name(self, design):
        """
        Generate the design name given the multiple dv options
        """
        name = 'core_'
        dv_ = []
        for dv, dv_data in self._design_variables.items():
            if dv_data['variable type'] == dict:
                dv_.extend(list(design[dv].values()))
            else:
                dv_.append(design[dv])
        name += str(dv_).replace("'", "")
        return name
        

    def get_interpolate_objectives(self, design):
        """
        Get the objective functions based on an interpolator function
        """
        for obj_name, interpolator in self._sm.items():
            if obj_name in self._objectives:
                self.current_objectives[obj_name] = round(float(interpolator(tuple(design))), self._objective_accuracy)
            elif obj_name in self._constraints:
                self.current_constraints[obj_name] = round(float(interpolator(tuple(design))), self._constraint_accuracy)
                
    def get_sm_objectives(self):
        """
        Get the objective functions based on a surrogate model
        """
        obj_dict = self._sm.predict(self.sm_type, self.current_design_variables, output='dict')
        for obj in self._objectives.keys():
            self.current_objectives[obj] = round(float(obj_dict[obj]), self._objective_accuracy)
        for cnst in self._constraints.keys():
            self.current_constraints[cnst] = round(float(obj_dict[cnst]), self._constraint_accuracy)
                
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB.
        
        Parameter
        ---------
        blackbaord : str
            required message for sending communication containing current state of BB
        """
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)
            
        self.log_debug('Executing agent {}'.format(self.name))
        self.search_method()
        self.calc_objectives()
        self.write_to_bb(self.bb_lvl_data, self._entry_name, self._entry, panel='new')
        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.action_complete()
        
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
        """Scale an objective based on the upper/lower value"""
        return (val - ll) / (ul - ll)

class KaGlobal(KaRp):
    """
    Knowledge agent to solve portions reactor physics problems using a stochastic sampling technique.
    
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
        Valid options: (interpolator, lr, pr, gpr, ann, rf)
        See surrogate_modeling for more details
    """

    def on_init(self):
        super().on_init()
        self._class = 'global search mc'
        
    def search_method(self):
        """
        Determine the core design variables using a monte carlo method.
        """        
        for dv, dv_dict in self._design_variables.items():
            if dv_dict['variable type'] == dict:
                length = dv_dict['length']
                design = {}
                for pos in dv_dict['dict']:
                    if dv_dict['dict'][pos]['variable type'] != float:
                        design[pos] = random.choice(dv_dict['dict'][pos]['options'])
                    else:
                        design[pos] = round(random.random() * (dv_dict['dict'][pos]['ul'] - dv_dict['dict'][pos]['ll']) + dv_dict['dict'][pos]['ll'], self._design_accuracy)
                    
                self.current_design_variables[dv] = design
            elif dv_dict['variable type'] == str:
                self.current_design_variables[dv] = random.choice(dv_dict['options'])               
            else:
                self.current_design_variables[dv] = round(random.random() * (dv_dict['ul'] - dv_dict['ll']) + dv_dict['ll'], self._design_accuracy)
        
        self._entry_name = self.get_design_name(self.current_design_variables)
        if self._entry_name in self._lvl_data.keys():
            self.search_method()
                
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))
                
        
class KaLHC(KaRp):
    """
    Knowledge agent who discovers the design space using a latin hyper cube sampling technique.
    This can be beneficialy for adequatly sampling the design space, and for generating an accurate SM for KaSm.
    
    Inherets from KaBase
    
    Attributes:
    """
    
    def on_init(self):
        super().on_init()
        self.lhc_criterion = 'corr'
        self.samples = 50
        self.lhd = []
        self._class = 'global search lhc'        

    def set_random_seed(self, seed=None):
        """
        Sets the random seed number to provide a reproducabel result
        """
        random.seed(seed=seed)
        
    def generate_lhc(self):
        """
        The codes used to generate a latin hybercube was originally published by the following individuals for use with
        Scilab:
            Copyright (C) 2012 - 2013 - Michael Baudin
            Copyright (C) 2012 - Maria Christopoulou
            Copyright (C) 2010 - 2011 - INRIA - Michael Baudin
            Copyright (C) 2009 - Yann Collette
            Copyright (C) 2009 - CEA - Jean-Marc Martinez
    
            website: forge.scilab.org/index.php/p/scidoe/sourcetree/master/macros
        This was translated into python in the pyDOE.
        
            website: https://pythonhosted.org/pyDOE/#source-code
        """
        
        length = 0
        for k,v in self._design_variables.items():
            if v['variable type'] == dict:
                length += v['length']
            else:
                length += 1
            
        lhd = self.lhs(length, samples=self.samples, criterion=self.lhc_criterion)
        self.lhd = lhd.tolist()


    def lhs(self, n, samples=None, criterion=None, iterations=5):
        """
        Generate a latin-hypercube design
    
        Parameters
        ----------
        n : int
            The number of factors to generate samples for
    
        Optional
        --------
        samples : int
            The number of samples to generate for each factor (Default: n)
        criterion : str
            Allowable values are "center" or "c", "maximin" or "m", 
            "centermaximin" or "cm", and "correlation" or "corr". If no value 
            given, the design is simply randomized.
        iterations : int
            The number of iterations in the maximin and correlations algorithms
            (Default: 5).
    
        Returns
        -------
        H : 2d-array
            An n-by-samples design matrix that has been normalized so factor values
            are uniformly spaced between zero and one.
        """
        samples = self.samples
        
        H = self._lhscorrelate(n, samples, iterations)
    
        return H

    def _lhsclassic(self, n, samples):
        # Generate the intervals
        cut = np.linspace(0, 1, samples + 1)    
        
        # Fill points uniformly in each interval
        u = np.random.rand(samples, n)
        a = cut[:samples]
        b = cut[1:samples + 1]
        rdpoints = np.zeros_like(u)
        for j in range(n):
            rdpoints[:, j] = u[:, j]*(b-a) + a
        
        # Make the random pairings
        H = np.zeros_like(rdpoints)
        for j in range(n):
            order = np.random.permutation(range(samples))
            H[:, j] = rdpoints[order, j]
        
        return H

    def _lhscorrelate(self, n, samples, iterations):
        mincorr = np.inf
        
        # Minimize the components correlation coefficients
        for i in range(iterations):
            # Generate a random LHS
            Hcandidate = self._lhsclassic(n, samples)
            R = np.corrcoef(Hcandidate)
            if np.max(np.abs(R[R!=1]))<mincorr:
                mincorr = np.max(np.abs(R-np.eye(R.shape[0])))
                self.log_debug('new candidate solution found with max,abs corrcoef = {}'.format(mincorr))
                H = Hcandidate.copy()
        
        return H
        
        
    def search_method(self):
        """
        Determine the core design variables using a LHC method.
        """
        cur_design = self.lhd.pop(0)
        num = 0
        for dv, dv_dict in self._design_variables.items():
            if dv_dict['variable type'] == dict:
                length = dv_dict['length']
                design = {}
                for pos in dv_dict['dict']:
                    if dv_dict['dict'][pos]['variable type'] != float:
                        val = int(length * cur_design[num])
                        design[pos] = dv_dict['dict'][pos]['options'][val]
                    else:
                        design[pos] = round(cur_design[num] * (dv_dict['dict'][pos]['ul'] - dv_dict['dict'][pos]['ll']) + dv_dict['dict'][pos]['ll'], self._design_accuracy)
                    num +=1

                self.current_design_variables[dv] = design
            elif dv_dict['variable type'] == str:
                self.current_design_variables[dv] = dv_dict['options'][int(len(dv_dict['options']) * cur_design[num])]              
            else:
                self.current_design_variables[dv] = round(cur_design[num] * (dv_dict['ul'] - dv_dict['ll']) + dv_dict['ll'], self._design_accuracy)
            num += 1
            
        self._entry_name = self.get_design_name(self.current_design_variables)
        if self._entry_name in self._lvl_data.keys():
            self.search_method()
            
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))
        
    def handler_trigger_publish(self, message):
        """
        Send a message to the BB indiciating it's trigger value.
        
        Parameters
        ----------
        message : str
            Containts unused message, but required for agent communication.
        """
        self._trigger_val = len(self.lhd) + 0.000006 if len(self.lhd) > 0 else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))

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
    """

    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.bb_lvl_read = 1
        self.perturbation_size = 0.05
        self._lvl_data = None
        self.lvl_read = None
        self.analyzed_design = {}
        self.generated_designs = {}
        self.new_designs = []
        self.neighboorhod_search = 'fixed'
        self._class = 'local search ns'

    def determine_model_applicability(self, dv):
        """
        Determine if a design variable is valid, and if the design has already been examined.
        If the design isn't valid or has already been examined, skip this.
        If the design is new, calculate the objectives and wrtie this to the blackbaord.
        """
        dv_dict = self._design_variables[dv]
        dv_cur_val = self.current_design_variables[dv]
        core_name = self.get_design_name(self.current_design_variables)

        if core_name in self._lvl_data.keys():
            self.log_debug('Core {} not examined; found same core in Level {}'.format(core_name, self.bb_lvl))
            return
        if dv_dict['variable type'] == float:
            if dv_cur_val < dv_dict['ll'] or dv_cur_val > dv_dict['ul']:
                self.log_debug('Core {} not examined; design outside design variables.'.format(core_name))
                return
        
        self.calc_objectives()
        self.generated_designs = {'HV': 0}
        self.write_to_bb(self.bb_lvl_data, self._entry_name, self._entry, panel='new')
        self.log_debug('Perturbed variable {} with value {}'.format(dv, dv_cur_val))    
        
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        
        KA will perturb the core via the perturbations method and write all results the BB
        """
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))
        self.lvl_read = message[1]['level {}'.format(self.bb_lvl_read)]
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)
            
        self.search_method()
        self.agent_time = time.time() - t
        self.action_complete()
                      
    def handler_trigger_publish(self, blackboard):
        """
        Read the BB level and determine if an entry is available.
        
        Paremeters
        ----------
        blackboard : str
            Required message from BB containing the current state of the blackboard
        
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
        new_entry = self.read_bb_lvl(blackboard)
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
        
        core = random.choice(self.new_designs)
        design_ = self._lvl_data[core]['design variables']
        pert = self.perturbation_size if self.neighboorhod_search == 'fixed' else random.uniform(0,self.perturbation_size)
        perts = [1.0 - pert, 1.0 + pert]
        pert_designs = []
            
        for dv, dv_value in design_.items():
            design = copy.copy(design_)
            if self._design_variables[dv]['variable type'] == str:
                options = copy.copy(self._design_variables[dv]['options'])
                options.remove(design[dv])
                design[dv] = str(random.choice(options))
                pert_designs.append((dv,design))
            else:
                for pert in perts:
                    design[dv] = round(dv_value * pert, self._design_accuracy)
                    pert_designs.append((dv,design))
                    design = copy.copy(design_)
        
        for dv, design in pert_designs:
            self.current_design_variables = design
            self._entry_name = self.get_design_name(self.current_design_variables)
            if self._entry_name in self._lvl_data.keys():
                self.log_debug('Core {} not examinedl found same core in level {}'.format(self._entry_name, self.bb_lvl))
            else:
                self.determine_model_applicability(dv)
        
        self.analyzed_design[core] = {'Analyzed': True}

    def read_bb_lvl(self, lvl):
        """
        Determine if there are any 'new' entries on level 1.
        
        Returns
        -------
            True -  if level has entries
            False -  if level is empty
        """
        lvl = lvl['level {}'.format(self.bb_lvl_read)]
        cores = [x for x in self.analyzed_design.keys()]
        self.new_designs = [key for key in lvl if not key in self.analyzed_design]
        return True if self.new_designs else False            
        
class KaLocalHC(KaLocal):
    
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.avg_diff_limit = 5
        self.step_size = 0.05
        self.step_rate = 0.01
        self.step_limit = 100
        self.convergence_criteria = 0.001
        self.hc_type = 'simple'
        self._class = 'local search hc'
        
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
        # Try catch statement is important in MABS, if an entry in lvl_read is no longer present on the BB
        try:
            core = random.choice(self.new_designs)
            entry = self.lvl_read[core]
        except KeyError:
            self.new_designs.remove(core)
            if len(self.new_designs) > 0:
                self.search_method()
            else:
                return
            
        step = self.step_size
        step_design = self._lvl_data[core]['design variables']
        step_objs = self._lvl_data[core]['objective functions']
        step_number = 0
        
        while step > self.convergence_criteria:
            gradient_vector = {}
            next_step = None
            
            # Calculate our gradient vector
            for dv, dv_dict in self._design_variables.items():
                potential_steps = []
                if dv_dict['variable type'] == float:
                    for direction in ['+', '-']:
                        temp_design = copy.copy(step_design)
                        temp_design[dv] += temp_design[dv] * step if direction == '+' else temp_design[dv] * -step
                        temp_design[dv] = round(temp_design[dv], self._design_accuracy)
                        if temp_design[dv] >= dv_dict['ll'] and temp_design[dv] <= dv_dict['ul']:
                            potential_steps.append((direction, temp_design))

                else:
                    temp_design = copy.copy(step_design)
                    options = copy.copy(dv_dict['options'])
                    options.remove(step_design[dv])
                    temp_design[dv] = str(random.choice(options))
                    potential_steps.append(('+', temp_design))

                for direction, design in potential_steps:
                    self.current_design_variables = design
                    self._entry_name = self.get_design_name(self.current_design_variables)
                    if self._entry_name in self._lvl_data.keys():
                        self.log_debug('Core {} not examined, found same core in level {}'.format(self._entry_name, self.bb_lvl))
                    else:
                        self.calc_objectives()
                        gradient_vector['{} {}'.format(direction,dv)] = {'design variables': self.current_design_variables, 
                                                                         'objective functions': {k:v for k,v in self.current_objectives.items()},
                                                                        'constraints': self.current_constraints}
                    
            # Determine which step is the steepest, update our design, and write this to the BB
            if gradient_vector:
                next_step, diff = self.determine_step(step_design, step_objs, gradient_vector)
                if next_step:
                    step_design = gradient_vector[next_step]['design variables']
                    step_objs = gradient_vector[next_step]['objective functions']
                    self.current_design_variables = {k:v for k,v in step_design.items()}
                    self.determine_model_applicability(next_step.split(' ')[1])
            
            #If we don't have a gradient vector or a next step to take, reduce the step size
            if gradient_vector == {} or next_step == None:
                step = step * (1 - self.step_rate)
            step_number += 1
            if step_number > self.step_limit:
                break
                
        if core:
            self.write_to_bb(self.bb_lvl_read, core, entry)
            self.analyzed_design[core] = {'Analyzed': True, 'HV': 0.0}

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
            dict_ = design_dict[pert_dv]
            dv = pert_dv.split(' ')[1]
            dv_dict = self._design_variables[dv]
            design[pert_dv] = {}
            design[pert_dv]['total'] = 0
            
            for name, obj_dict in self._objectives.items():
                base_obj = base_design[name]
                new_obj = dict_['objective functions'][name]
                if new_obj >= obj_dict['ll'] and new_obj <= obj_dict['ul']:
                    obj_scaled_new = self.scale_objective(new_obj, obj_dict['ll'], obj_dict['ul'])
                    obj_scaled_base = self.scale_objective(base_obj, obj_dict['ll'], obj_dict['ul'])
                    dv_scaled_new = self.scale_objective(base[dv], dv_dict['ll'], dv_dict['ul']) if dv_dict['variable type'] == float else 1.0
                    dv_scaled_base = self.scale_objective(design_dict[pert_dv]['design variables'][dv], dv_dict['ll'], dv_dict['ul']) if dv_dict['variable type'] == float else 0.0
                    
                    # We are following the steepest ascent, so positive is better
                    obj_diff = (obj_scaled_new - obj_scaled_base) if obj_dict['goal'] == 'gt' else (obj_scaled_base - obj_scaled_new)
                    dv_diff = abs(dv_scaled_new - dv_scaled_base)
                    derivative = obj_diff / dv_diff if dv_diff != 0 else 0
                    design[pert_dv][name] = derivative
                    design[pert_dv]['total'] += derivative

                    if derivative > 0 and self.hc_type == 'simple':
                        return(pert_dv, derivative)
                    
            truth = True
            for constraint, val in dict_['constraints'].items():
                if val <= self._constraints[constraint]['ll'] or val >= self._constraints[constraint]['ul']:
                    truth = False
            if design[pert_dv]['total'] > 0 and design[pert_dv]['total'] > best_design['total'] and truth:
                best_design = design[pert_dv]
                best_design['pert'] = pert_dv
             
        if best_design['total'] > 0:
            return (best_design['pert'], best_design['total'])
        else:
            return (None, None)
            
        
class KaLocalRW(KaLocal):
    
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.step_size = 0.01
        self.walk_length = 10
        self._class = 'local search rw'
        
    def search_method(self):
        """
        Basic random walk algorithm for searching around a viable design.
        """
        core = random.choice(self.new_designs)
        entry = self.lvl_read[core]
        design = self._lvl_data[core]['design variables']
        
        for x in enumerate(range(self.walk_length)):
            dv = random.choice(list(self._design_variables))
            step = round(random.random() * self.step_size, self._design_accuracy)
            direction = random.choice(['+','-'])
            design[dv] = design[dv] + step if direction == '+' else design[dv] - step
            design[dv] = round(design[dv], self._design_accuracy)
            self.current_design_variables = design
            self.determine_model_applicability(dv)
        self.analyzed_design[core] = {'Analyzed': True, 'HV': 0.0}
        
class KaLocalGA(KaLocal):
    """
    Pseudo-basic gentic algorithm for helping global and local searches
    """
     
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00004
        self.previous_populations = {}
        self.crossover_rate = 0.8
        self.offspring_per_generation = 20
        self.mutation_rate = 0.1
        self.crossover_type = 'single point'
        self.num_cross_over_points = 1
        self.mutation_type = 'random'
        self.pf_size = 40
        self.b = 2
        self.k = 5
        self.T = 100
        self._class = 'local search ga'
        
    def handler_trigger_publish(self, message):
        """
        Read the BB level and determine if an entry is available.
        GA is currently triggered if we find that the PF level has solutions that it has not analyzed greater than some aribratry amount pf_size.
        
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
        lvl = message['level {}'.format(self.bb_lvl_read)]
        new = set([x for x in lvl.keys()])
        old = set([x for x in self.analyzed_design.keys()])
        intersection = old.intersection(new)
        self._trigger_val = self._base_trigger_val if len(new) - len(old) >= self.pf_size else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def search_method(self):
        """
        Search method for the GA is to perform crossover and mutation to generate new designs.
        
        Currently two crossover types are allowed: single-point and linear.
        Currently two mutation types are allowed: random and non-uniform.
        """
        self.pf_size = int(self.pf_size*1.05)

        population = [x for x in self.lvl_read.keys()]
        original_pop_len = len(population)
        children = []
        num_children = 0
                
        while num_children < self.offspring_per_generation:
            if len(population) < 2:
                break
            design1 = population.pop(random.choice(range(len(population))))
            design2 = population.pop(random.choice(range(len(population))))
            parent1 = self._lvl_data[design1]
            parent2 = self._lvl_data[design2]
            self.analyzed_design[design1] = {'Analyzed': True}
            self.analyzed_design[design2] = {'Analyzed': True}
            # Crosover to determine new children
            if self.crossover_type == 'single point':
                children = self.single_point_crossover(parent1, parent2, self.num_cross_over_points)
            elif self.crossover_type == 'linear crossover':
                children = self.linear_crossover(parent1, parent2)
            else:
                self.log_warning('Warning: cross-over type {} is not implemented, reverting to `single-point` cross-over.'.format(self.crossover_rate))
                children = self.single_point_crossover(parent1, parent2, self.num_cross_over_points)

            # Determine if we mutate a child
            for child in children:
                if random.random() < self.mutation_rate:
                    if self.mutation_type == 'random':
                        child = self.random_mutation(child)
                    elif self.mutation_type == 'non-uniform':
                        child = self.non_uniform_mutation(child)
                    else:
                        self.log_warning('Warning: mutation type {} is not implemented, reverting to `random` mutation.'.format(self.mutation_type))
                        child = self.random_mutation(child)
                self.current_design_variables = child
                self.determine_model_applicability(next(iter(child)))
                num_children += len(children)

            
    def single_point_crossover(self, genotype1, genotype2, num_crossover_points):
        """
        Single point crossover where we simply select a design variables and cross the two parents at that variable
        Paremeters:
        -----------
        genotype1 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        genotype2 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        Returns:
        --------
        c1 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c2 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        """
        # Prevent a null crossover
        crossover = 0
        while crossover == 0:
            crossover = random.choice(range(len(self._design_variables)))
        p1_dv = [x for x in genotype1['design variables'].values()]
        p2_dv = [x for x in genotype2['design variables'].values()]

        c1_dv = p1_dv[:crossover] + p2_dv[crossover:]
        c2_dv = p2_dv[:crossover] + p1_dv[crossover:]
        c1 = {dv:c1_dv[num] for num, dv in enumerate(self._design_variables.keys())}
        c2 = {dv:c2_dv[num] for num, dv in enumerate(self._design_variables.keys())}

        return [c1, c2]
    
    def linear_crossover(self, genotype1, genotype2):
        """
        Linear crossover for GA, where we take fractions of each design variable and sum them up to generate a new design variable
        
        Paremeters:
        -----------
        genotype1 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        genotype2 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        Returns:
        --------
        c1 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c2 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c3 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        """
        c1 = {}
        c2 = {}
        c3 = {}
        for dv, value in genotype1['design variables'].items():
            c1[dv] = round(0.5 * value + 0.5 * genotype2['design variables'][dv], self._objective_accuracy)
            c2[dv] = round(1.5 * value - 0.5 * genotype2['design variables'][dv], self._objective_accuracy)
            if c2[dv] > self._design_variables[dv]['ul']:
                c2[dv] = self._design_variables[dv]['ul']
            elif c2[dv] < self._design_variables[dv]['ll']:
                c2[dv] = self._design_variables[dv]['ll']
            c3[dv] = round(-0.5 * value + 1.5 * genotype2['design variables'][dv], self._objective_accuracy)
            if c3[dv] > self._design_variables[dv]['ul']:
                c3[dv] = self._design_variables[dv]['ul']
            elif c3[dv] < self._design_variables[dv]['ll']:
                c3[dv] = self._design_variables[dv]['ll']
        return [c1, c2, c3]
        
    
    def random_mutation(self, genotype):
        """
        Perform a random mutation, take a DV and allow it to vary it within a small perturbation
        Paremeters:
        -----------
        genotype : dict
            dictionary of design to be mutated, keys are design variable names, values are design variable values
        Returns:
        --------
        genotype : dict
            dictionary of mutated design with one of the dezign variables changed within the perturbation size
        """
        dv_mutate = random.choice([x for x in self._design_variables.keys()])
        ll = genotype[dv_mutate]*(1-self.perturbation_size)
        ul = genotype[dv_mutate]*(1+self.perturbation_size)
        genotype[dv_mutate] = round(random.random() * (ul - ll) + ll, self._design_accuracy)
        # Check to make sure we don't violate upper/lower limits, if we do, set it to the limit.
        genotype[dv_mutate] = min(self._design_variables[dv_mutate]['ul'], genotype[dv_mutate])
        genotype[dv_mutate] = max(self._design_variables[dv_mutate]['ll'], genotype[dv_mutate])
        return genotype
    
    def non_uniform_mutation(self, genotype):
        """
        Utilize Michalewicz's non-uniform mutation,
        
        For the following, assume a constant alpha as well
        Notes: For a constant k/T, smaller values of b lead to a larger distribution
               For a constant b, a smaller k/T ratio leads to a larger distribution
               
        Paremeters:
        -----------
        genotype : dict
            dictionary of design to be mutated, keys are design variable names, values are design variable values
        Returns:
        --------
        genotype : dict
            dictionary of mutated design with one of the dezign variables changed according to a non-uniform mutation
        """
        
        # can we update the k/T parameter as a function of hypervolume convergence?
        dv_mutate = random.choice([x for x in self._design_variables.keys()])
        mutation_direction = random.choice(['up', 'down'])
        
        alpha = random.random()
        exponent = (1 - self.k / self.T)**self.b
        delta_k = genotype[dv_mutate] * (1 - alpha**exponent)
        
        if mutation_direction == 'up':
            new_gene = genotype[dv_mutate] + delta_k
            genotype[dv_mutate] = round(min(new_gene, self._design_variables[dv_mutate]['ul']), self._design_accuracy)
        else:
            new_gene = genotype[dv_mutate] - delta_k
            genotype[dv_mutate] = round(max(new_gene, self._design_variables[dv_mutate]['ll']), self._design_accuracy)
        return genotype

    
class KaLocalSm(KaLocal):
    """
    Knowledge Agent who generates a SM based on the data level of the BB to find areas of interest
    """
    
    def on_init(self):
        super().on_init()
        self.bb_lvl_read = 3
        self._base_trigger_val = 5.0005
        self.sm_type = 'gpr'
        self._sm = None
        self._class = 'local search sm'

    def handler_trigger_publish(self, message):
        """

        """
        data_size = len(message['level {}'.format(self.bb_lvl_read)])

        self._trigger_val = self._base_trigger_val if len(new) - len(old) >= self.pf_size else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))

    def generate_sm(self, data):
        """
        Generate a simple surogate model based on the data provided in the data level of the blackboard.
        """
        self._sm = tm.Surrogate_Models()
        self._sm.random = 10983
        self._sm.update_database([x for x in self._objectives.keys()], [x for x in self._design_variables.keys()], database=data)
        self._sm.update_model(self.sm_type)        
        
    def search_method(self):
        """
        Generate a SM and find an areas of interest
        Option 1: Look at the ll/ul and find the objectives with the smallest range compared to this.
        Option 2: Fix an objecives to a specific value (high/low/median) sweep over other parameters to find viable cores
        Option 3: Randomly sample the objectives within llul
        """
        pass
    
    def random_sample(self):
        pass