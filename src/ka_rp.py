import osbrain
from osbrain import Agent
import numpy as np
import random
import scipy.interpolate
import db_reshape as dbr
from collections import OrderedDict
import ka


class KaRp(ka.KaBase):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    """
    def on_init(self):
        super().on_init()
        self._trigger_val = 1.0

class KaRp_verify(KaRp):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
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
        self.bb_lvl = 2
        self.objectives = ['keff', 'void_coeff', 'doppler_coeff']
        self.independent_variable_ranges = OrderedDict({'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})

    def handler_executor(self, message):
        """Execution handler for KA-RP.
        KA-RP determines a core design and runs a physics simulation using a surrogate model.
        Upon completion, KA-RP sends the BB a writer message to write to the BB."""
        self.log_debug('Executing agent {}'.format(self.name))
        self.determine_design_variables()
        self.calc_core_params()
        self.write_to_bb()
    
    def determine_design_variables(self):
        """Determine the core design variables using either a surrogate model, or random assignment."""
        for param, ranges in self.independent_variable_ranges.items():
            self.design_variables[param] = round(random.random() * (ranges[1] - ranges[0]) + ranges[0],2)
        self._entry_name = 'core_{}'.format([x for x in self.design_variables.values()])
        self.log_info('Core design variables determined: {}'.format(self.design_variables))

    def calc_core_params(self):
        """Calculate the objective functions based on the core design variables."""
        self.log_debug('Determining core parameters based on SM')
        for obj_name, interpolator in self.interpolator_dict.items():
            self.objective_functions[obj_name] = float(interpolator(tuple([x for x in self.design_variables.values()])))
        a = self.design_variables.copy()
        a.update(self.objective_functions)
        self._entry = {'reactor parameters': a}
    
    def create_interpolator(self):
        """Build the linear interpolator for estimating between known datapoints.
        This uses scipy's LinearNDInterpolator, where we create a unique interpolator for each objective function"""
        design_var, objective_func = dbr.reshape_database(r'{}/sfr_db_new.h5'.format(self.interp_path), [x for x in self.independent_variable_ranges.keys()], self.objectives)
        design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
        for num, objective in enumerate(self.objectives):
            self.interpolator_dict[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])
    
            