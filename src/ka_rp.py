import osbrain
from osbrain import Agent
import numpy as np
import random
import scipy.interpolate
import db_reshape as dbr
from collections import OrderedDict
import ka
import time
from itertools import permutations

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

    def on_init(self):
        super().on_init()
        self.design_variables = {}
        self.objective_functions = {}
        self.interpolator_dict = {}
        self.interp_path = None
        self.bb_lvl = 3
        self.objectives = ['keff', 'void_coeff', 'doppler_coeff']
        self.independent_variable_ranges = OrderedDict({'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})

    def handler_executor(self, message):
        """Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB."""
        self.log_debug('Executing agent {}'.format(self.name))
        self.mc_design_variables()
        self.calc_objectives()
        self.write_to_bb()
    
    def mc_design_variables(self):
        """Determine the core design variables using a monte carlo method."""
        for param, ranges in self.independent_variable_ranges.items():
            self.design_variables[param] = round(random.random() * (ranges[1] - ranges[0]) + ranges[0],2)
        self.log_info('Core design variables determined: {}'.format(self.design_variables))

    def calc_objectives(self):
        """Calculate the objective functions based on the core design variables."""
        self.log_debug('Determining core parameters based on SM')
        for obj_name, interpolator in self.interpolator_dict.items():
            self.objective_functions[obj_name] = float(interpolator(tuple([x for x in self.design_variables.values()])))
        a = self.design_variables.copy()
        a.update(self.objective_functions)
        self._entry_name = 'core_{}'.format([x for x in self.design_variables.values()])
        self._entry = {'reactor parameters': a}
    
    def create_sm(self):
        """Build the linear interpolator for estimating between known datapoints.
        This uses scipy's LinearNDInterpolator, where we create a unique interpolator for each objective function"""
        design_var, objective_func = dbr.reshape_database(r'{}/sfr_db_new.h5'.format(self.interp_path), [x for x in self.independent_variable_ranges.keys()], self.objectives)
        design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
        for num, objective in enumerate(self.objectives):
            self.interpolator_dict[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])        

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
        self.perturbed_cores = {}
        self.lvl1 = {}
        self.perturbations = [0.99, 1.01]
    
    def handler_executor(self, message):
        """Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB."""
        self.log_debug('Executing agent {}'.format(self.name))
        self.lvl1 = self.bb.get_attr('abstract_lvls')['level 1']
        if self.lvl1 == {}:
            self.mc_design_variables()
            self.calc_objectives()
            self.write_to_bb()
        else:
            self.perturb_design()

    def perturb_design(self):
        """
        Perturb a core design
        
        This first finds a core in BB level 1 that it has not examined yet.
        It then perturbs each design variable independent by the values in self.perturbations
        These results are written to the BB level 3, so there should be design_vars * pert added to level 3.
        """
        lvl3 = self.bb.get_attr('abstract_lvls')['level 3']
        for core in self.lvl1.keys():
            if core in self.perturbed_cores:
                pass
            else:
                base_design_variables = {k: lvl3[core][k] for k in self.independent_variable_ranges.keys()}
                i = 0
                total_perts = len(base_design_variables.keys()) * len(self.permutations)
                for var_name, var_value in base_design_variables.items():
                    for pert in self.perturbations:
                        i += 1
                        self.design_variables = base_design_variables
                        self.design_variables[var_name] = var_value * pert
                        self.calc_objectives()
                        self.perturbed_cores.append(self._entry_name)
                        completed = True if i == total_perts else False
                        self.write_to_bb(completed)

    def write_to_bb(self, completed):
        """Write the KA's entry to the BB on the specified level."""
        self.log_debug('Sending writer trigger to BB.')
        write = False
        while not write:
            time.sleep(1)
            self.send(self._writer_alias, [self.name, completed])
            write = self.recv(self._writer_alias)
        else:
            self.log_debug('Writing to BB Level {}'.format(self.bb_lvl))
            self.bb.update_abstract_lvl(self.bb_lvl, self._entry_name, self._entry)
            
class KaRp_verify(KaRpExplore):
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.objectives = ['keff', 'void_coeff', 'doppler_coeff']
        self.independent_variable_ranges = OrderedDict({'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})

    def calc_objectives(self):
        """Calculate the objective functions based on the core design variables."""
        self.log_debug('Determining core parameters based on SM')
        for obj_name, interpolator in self.interpolator_dict.items():
            self.objective_functions[obj_name] = float(interpolator(tuple([x for x in self.design_variables.values()])))
        a = self.design_variables.copy()
        a.update(self.objective_functions)
        self._entry = {'reactor parameters': a}
