import osbrain
from osbrain import Agent
import numpy as np
import random
import scipy.interpolate
import database_generator as dg
from collections import OrderedDict
import ka
import time
from itertools import permutations
import train_surrogate_models as tm
import copy

class KaRp(ka.KaBase):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    """
    def on_init(self):
        super().on_init()
        self._trigger_val = 1.0

class KaRpExplore(KaRp):
    """
    Knowledge agent to solve portions reactor physics problems using a SM.
    
    Inherets from KaBase.
    
    Attibutes:
    
      core_name        (str)             - Name of the core
      rx_parameters    (dataframe)       - Pandas dataframe containing reactor core parameters from Mammoth
      surrogate_models (SurrogateModels) - SurrogateModels class from surrogate_modeling, containes a set of trained surogate mdoels
      objectives       (list)            - List of the desired objective functions to be examined
      design_variables (list)            - List of the design variables to be used
    """
    
    
    # Create a unique trigger handler to determine the number of entries on level 3 new and decrease the trigger value to 0 if there are too many.

    def on_init(self):
        super().on_init()
        self.design_variables = {}
        self.objective_functions = {}
        self.interpolator_dict = {}
        self.interp_path = None
        self.bb_lvl = 3
        self.objectives = []
        self.independent_variable_ranges = OrderedDict({'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})
        self._sm = None
        self.sm_type = 'interpolate'

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
    
    def mc_design_variables(self):
        """Determine the core design variables using a monte carlo method."""
        for param, ranges in self.independent_variable_ranges.items():
            self.design_variables[param] = round(random.random() * (ranges[1] - ranges[0]) + ranges[0],2)
        self.log_debug('Core design variables determined: {}'.format(self.design_variables))

    def calc_objectives(self):
        """
        Calculate the objective functions based on the core design variables.
        This process is performed via an interpolator or a surrogate model.
        """
        self.log_debug('Determining core parameters based on SM')
        design = [x for x in self.design_variables.values()]
        if self.sm_type == 'interpolate':
            for obj_name, interpolator in self._sm.items():
                self.objective_functions[obj_name] = float(interpolator(tuple(design)))
        else:
            obj_list = self._sm.predict(self.sm_type, [design])
            for num, obj in enumerate(self.objectives):
                self.objective_functions[obj] = float(obj_list[0][num])
        a = self.design_variables.copy()
        a.update(self.objective_functions)
        self.log_debug('Core Design & Objectives: {}'.format([(x,round(y,2)) for x,y in a.items()]))
        self._entry_name = 'core_{}'.format([x for x in self.design_variables.values()])
        self._entry = {'reactor parameters': a}


class KaRpExploit(KaRpExplore):
    """
    Knowledge agent to solve portions reactor physics problems using a SM.
    
    Inherets from KaBase.
    
    Attibutes:
    
      core_name        (str)             - Name of the core
      rx_parameters    (dataframe)       - Pandas dataframe containing reactor core parameters from Mammoth
      surrogate_models (SurrogateModels) - SurrogateModels class from surrogate_modeling, containes a set of trained surogate mdoels
      objectives       (list)            - List of the desired objective functions to be examined
      design_variables (list)            - List of the design variables to be used
    """

    def on_init(self):
        super().on_init()
        self.perturbed_cores = []
        self._trigger_val = 0.0
        self.bb_lvl_read = 1
        self.perturbations = [0.99, 1.01]
        self.new_panel = 'new'
        self.old_panel = 'old'
    
    def handler_executor(self, message):
        """
        Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB.
        """
        self.log_debug('Executing agent {}'.format(self.name))
        self.perturb_design()

    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        new_entry = self.read_bb_lvl()
        self._trigger_val = 2.0 if new_entry else 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
            
    def move_entry(self, bb_lvl, entry_name, entry):
        self.write_to_bb(bb_lvl, entry_name, entry, panel=self.old_panel)
        self.write_to_bb(bb_lvl, entry_name, entry, panel=self.new_panel, remove=True)
            
    def perturb_design(self):
        """
        Perturb a core design
        
        This first finds a core in BB level 1 that it has not examined yet.
        It then perturbs each design variable independent by the values in self.perturbations
        These results are written to the BB level 3, so there should be design_vars * pert added to level 3.
        """
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        lvl3 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]['old']
        
        for core, entry in lvl.items():
            self.log_debug("Perturbing core design for {}".format(core))
            base_design_variables = {k: lvl3[core]['reactor parameters'][k] for k in self.independent_variable_ranges.keys()}
            i = 0
            total_perts = len(base_design_variables.keys()) * len(self.perturbations)
            for var_name, var_value in base_design_variables.items():
                for pert in self.perturbations:
                    i += 1
                    self.design_variables = copy.copy(base_design_variables)
                    self.design_variables[var_name] = var_value * pert
                    self.log_debug('Perturbing variable {} with value {}'.format(var_name, self.design_variables[var_name]))
                    self.calc_objectives()
                    completed = True if i == total_perts else False
                    self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, complete=completed, panel='new')
            self.move_entry(self.bb_lvl_read, core, entry)
            return
                        
    def read_bb_lvl(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]

        if lvl != {}:
            return True
            
class KaRp_verify(KaRpExplore):
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.objectives = ['keff', 'void', 'doppler']
        self.independent_variable_ranges = OrderedDict({'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})

    def calc_objectives(self):
        """Calculate the objective functions based on the core design variables."""
        self.log_debug('Determining core parameters based on SM')
        for obj_name, interpolator in self.interpolator_dict.items():
            self.objective_functions[obj_name] = float(interpolator(tuple([x for x in self.design_variables.values()])))
        a = self.design_variables.copy()
        a.update(self.objective_functions)
        self._entry = {'reactor parameters': a}

    def create_sm(self):
        """
        Build a surrogate model based on the SFR_DB.h5 dataset.
        The data is generated using the `get_data` function and returns the design and objective variables.
        This can be done using scipy's scipy's LinearNDInterpolator, or we use a regression model.
        The regression model is based on scikit-learn's and accessed through the `train_surrogate_model` module
        """

        design_var, objective_func = dg.get_data([x for x in self.independent_variable_ranges.keys()], self.objectives)
        if self.sm_type == 'interpolate':
            self._sm = {}
            design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
            for num, objective in enumerate(self.objectives):
                self._sm[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])
        else:
            self._sm = tm.Surrogate_Models()
            self._sm.random = 0
            self._sm.update_database(design_var, objective_func)
            self._sm.optimize_model(self.sm_type)