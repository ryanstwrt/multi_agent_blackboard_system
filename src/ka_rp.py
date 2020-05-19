import osbrain
from osbrain import Agent
import numpy as np
import random
import scipy.interpolate
import ka
import train_surrogate_models as tm
import copy
import database_generator as dg


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
        self.design_variables = []
        self.design_variable_ranges = {}
        self.current_design_variables = {}
        self._design_accuracy = 2
        self.objectives = []
        self.objective_functions = {}
        self._objective_accuracy = 2

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
    design_variable_ranges : dict
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

    def calc_objectives(self):
        """
        Calculate the objective functions based on the core design variables.
        This process is performed via an interpolator or a surrogate model.
        Sets the variables for the _entry and _entry_name
        """
        self.log_debug('Determining core parameters based on SM')
        design = [x for x in self.current_design_variables.values()]
        if self.sm_type == 'interpolate':
            for obj_name, interpolator in self._sm.items():
                self.objective_functions[obj_name] = float(interpolator(tuple(design)))
        else:
            obj_list = self._sm.predict(self.sm_type, [design])
            for num, obj in enumerate(self.objectives):
                self.objective_functions[obj] = float(obj_list[0][num])
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
        self.mc_design_variables()
        self.calc_objectives()
        self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel='new')
        self._trigger_val = 0
        self.log_debug('Executing agent {}'.format(self.name))
        
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
        
    def mc_design_variables(self):
        """
        Determine the core design variables using a monte carlo method.
        """
        for param, ranges in self.design_variable_ranges.items():
            self.current_design_variables[param] = round(random.random() * (ranges[1] - ranges[0]) + ranges[0], self._design_accuracy)
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))


class KaRpExploit(KaRpExplore):
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
        self.perturbations = [0.99, 1.01]
        self._design_accuracy = 4
        self.new_panel = 'new'
        self.old_panel = 'old'
    
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        
        KA will perturb the core via the perturbations method and write all results the BB
        """
        self.log_debug('Executing agent {}'.format(self.name))
        self.perturb_design()

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
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
            
    def perturb_design(self):
        """
        Perturb a core design
        
        This first selects a core at random from abstract level 1 (from the 'new' panel).
        It then perturbs each design variable independent by the values in perturbations, this produces n*m new cores (n = # of design variables, m = # of perturbations)
        These results are written to the BB level 3, so there should be design_vars * pert added to level 3.
        """
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        lvl3 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]['old']
            
        core, entry = random.choice(list(lvl.items())) if random.random() > 0.7 else min(list(lvl.items()))

        base_design_variables = {k: lvl3[core]['reactor parameters'][k] for k in self.design_variable_ranges.keys()}
        for var_name, var_value in base_design_variables.items():
            # TODOL Add an if statement here to ensure we don't perform a perturbation that has already been done.
            for pert in self.perturbations:
                self.current_design_variables = copy.copy(base_design_variables)
                self.current_design_variables[var_name] = round(var_value * pert, self._design_accuracy)
                self.calc_objectives()
                self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel='new', complete=False)
                self.log_debug('Perturbed variable {} with value {}'.format(var_name, self.current_design_variables[var_name]))
        self.move_entry(self.bb_lvl_read, core, entry, self.old_panel, self.new_panel, write_complete=True)
                        
    def read_bb_lvl(self):
        """
        Determine if there are any 'new' entries on level 1.
        
        Returns
        -------
            True -  if level has content
            False -  if level is empty
        """
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]

        return True if lvl != {} else False