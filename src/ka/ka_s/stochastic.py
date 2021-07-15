from src.ka.ka_s.base import KaS
from numpy import random
import src.utils.utilities as utils

class Stochastic(KaS):
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
        self._class = 'global search stochastic'
        
    def search_method(self):
        """
        Determine the core design variables using a monte carlo (stochastic) method.
        """        
        for dv, dv_dict in self._design_variables.items():
            if 'permutation' in dv_dict.keys():
                perm = dv_dict['permutation']
                random.shuffle(perm)
                self.current_design_variables[dv] = perm
            elif 'options' in dv_dict.keys():
                if 'default' in dv_dict.keys():
                    dv_val = random.choice(dv_dict['options']) if random.random() > self.learning_factor else dv_dict['default']   
                    self.current_design_variables[dv] = dv_dict['variable type'](dv_val)
                else:
                    self.current_design_variables[dv] = dv_dict['variable type'](random.choice(dv_dict['options']))
            else:
                self.current_design_variables[dv] = utils.get_float_val(random.random(), dv_dict['ll'], dv_dict['ul'], self._design_accuracy)
        
        self.log_info(self.current_design_variables)
        self._entry_name = self.get_design_name(self.current_design_variables)
        if not self.design_check():
            self.search_method()
            
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))