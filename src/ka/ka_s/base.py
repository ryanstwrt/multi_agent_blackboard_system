from src.ka.base import KaBase
import copy
import time
from numpy import random

class KaS(KaBase):
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
        self.learning_factor = 0.5
        self.debug_wait = False
        self.debug_wait_time = 0.5
        self.problem = None
        
        self.execute_once = False
        
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
        if self.execute_once:
            self.log_info('Agent {} shutting down'.format(self.name))
            self.shutdown()    
            
    def calc_objectives(self):
        """
        Calculate the objective functions based on the core design variables.
        This process is performed via an interpolator or a surrogate model.
        Sets the variables for the _entry and _entry_name
        """
        if self.debug_wait:
            time.sleep(self.debug_wait_time)
            
        self.log_debug('Determining core parameters based on SM')
        self._entry_name = self.get_design_name(self.current_design_variables)

        self.current_objectives, self.current_constraints = self.problem.evaluate(self.current_design_variables)
              
        self._entry = {'design variables': self.current_design_variables, 
                           'objective functions': self.current_objectives,
                           'constraints': self.current_constraints}
    
    def clear_entry(self):
        self._entry = {}
        self._entry_name = None

    def design_check(self):
        """
        Determine if all design variables are within the limits of the design.
        Check if the design has been examined before.
        """
        core_name = self.get_design_name(self.current_design_variables)
        if core_name in self._lvl_data.keys():
            self.log_debug('Core {} not examined; found same core in Level {}'.format(core_name, self.bb_lvl_data))
            return False
        
        for dv, dv_dict in self._design_variables.items():
            dv_val = self.current_design_variables[dv]       
            violated = False
            if 'options' in dv_dict.keys():
                violated = True if dv_val not in dv_dict['options'] else False  
            elif dv_dict['variable type'] == float:
                violated = True if dv_val < dv_dict['ll'] or dv_val > dv_dict['ul'] else False
            else:
                # If we are going to keep the dict option we need to add something here to check it
                ...

            if violated:
                self.log_debug('Core {} not examined, design variable {} with value {} outside of limits.'.format(core_name, dv, dv_val))
                return False    
        return True
       
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
        name = name.replace(" ", "")
        return name

    def get_float_val(self, multiplier, ll, ul,  accuracy):
        return round(multiplier * (ul - ll) + ll, accuracy)
                  
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB.
        
        Parameter
        ---------
        message : str
            Push-pull message from blackboard, contains the current state of all abstract levels on BB
        """
        if self.debug_wait:
            time.sleep(self.debug_wait_time)
        
        self.clear_entry()
        t = time.time()
        self._trigger_event = message[0]
        lvl_data = message[1]['level {}'.format(self.bb_lvl_data)]        
        self._lvl_data = {**lvl_data['new'], **lvl_data['old']}
            
        self.log_debug('Executing agent {}'.format(self.name))
        self.search_method()
        self.calc_objectives()
        # Check to ensure that all components calculated are present before we write to the BB
        if self._entry_name and len(self.current_objectives) == len(self._objectives) and len(self.current_constraints) == len(self._constraints):
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
        
        
class KaLocal(KaS):
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
        self.lvl_read = None
        self.analyzed_design = {}
        self.new_designs = []
        self._class = 'local search'
        self.reanalyze_designs = False
        
    def check_new_designs(self):
        """
        Check to ensure all designs in `new_designs` are still in `lvl_read`.
        """
        new_design_list = copy.copy(self.new_designs)
        for core in new_design_list:
            if core not in self.lvl_read.keys():
                self.new_designs.remove(core)        
                
    def determine_model_applicability(self, dv):
        """
        Determine if a design variable is valid, and if the design has already been examined.
        If the design isn't valid or has already been examined, skip this.
        If the design is new, calculate the objectives and wrtie this to the blackbaord.
        """
        self.clear_entry()
        dv_dict = self._design_variables[dv]
        dv_cur_val = self.current_design_variables[dv]
        core_name = self.get_design_name(self.current_design_variables)
        if not self.design_check():
            return False
        
        self.calc_objectives()
        if self._entry_name and len(self.current_objectives) == len(self._objectives) and len(self.current_constraints) == len(self._constraints):        
            self.write_to_bb(self.bb_lvl_data, self._entry_name, self._entry, panel='new')
            self.log_debug('Perturbed variable {} with value {}'.format(dv, dv_cur_val))    
        else:
            self.log_warning('Failed to log current design due to a failure in objective calculations.')
            return False
        return True
        
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        
        KA will perturb the core via the perturbations method and write all results the BB
        """
        t = time.time()
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))
        _lvl_read = message[1]['level {}'.format(self.bb_lvl_read)]
        self.lvl_read = _lvl_read if self.bb_lvl_read == 1 else {**_lvl_read['new'],**_lvl_read['old']}
        _lvl_data = message[1]['level {}'.format(self.bb_lvl_data)]        
        self._lvl_data = {**_lvl_data['new'],**_lvl_data['old']}
            
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
        _lvl_read = blackboard['level {}'.format(self.bb_lvl_read)]
        _lvl_read = _lvl_read if self.bb_lvl_read == 1 else {**_lvl_read['new'],**_lvl_read['old']}

        self._trigger_val = self._base_trigger_val if self.read_bb_lvl(_lvl_read) else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def search_method(self):
        """
        Perturb a core design
        
        This first selects a core at random from abstract level 1 (from the 'new' panel).
        It then perturbs each design variable independent by the values in perturbations, this produces n*m new cores (n = # of design variables, m = # of perturbations)
        
        These results are written to the BB level 3, so there are design_vars * pert added to level 3.
        """
        raise NotImplementedError('KaLocal is a base class, and should be inherited from')

    def select_core(self):
        """
        We select a core from the Pareto front by either selecting tha design with the maximum fitness.
        Or we can select a random choice in self.new_design.
        This is based on the `learning_factor`, which is a simple probability.
        
        We should look at making this a probability denstiy function rather than just the max PF choice.
        We could also try and have it select the design that has the highest hvi or something to do with dci?
        
        """
        self.check_new_designs()
        if len(self.new_designs) < 1:
            return False
        if random.random() > self.learning_factor and self.bb_lvl_read == 1:
            fitness = {core : self.lvl_read[core]['fitness function'] for core in self.new_designs}
            core = max(fitness,key=fitness.get)
        else:
            core = random.choice(self.new_designs)
        return core
          
    def read_bb_lvl(self, lvl):
        """
        Determine if there are any 'new' entries on level 1.
        
        Returns
        -------
            True -  if level has entries
            False -  if level is empty
        """
        self.new_designs = list(lvl.keys()) if self.reanalyze_designs else [key for key in lvl if key not in self.analyzed_design.keys()]
            
        return True if len(self.new_designs) > 0 else False   