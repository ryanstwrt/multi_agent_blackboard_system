from src.ka.ka_s.base import KaS
from numpy import random

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
            if dv_dict['variable type'] == dict:
                design = {}
                for pos in dv_dict['dict']:
                    if dv_dict['dict'][pos]['variable type'] == str:
                        design[pos] = random.choice(dv_dict['dict'][pos]['options'])
                    else:
                        design[pos] = self.get_float_val(random.random(), dv_dict['dict'][pos]['ll'], dv_dict['dict'][pos]['ul'], self._design_accuracy)
                self.current_design_variables[dv] = design
            elif dv_dict['variable type'] == str:
                self.current_design_variables[dv] = str(random.choice(dv_dict['options'])) if random.random() > self.learning_factor else dv_dict['default']              
            else:
                self.current_design_variables[dv] = self.get_float_val(random.random(), dv_dict['ll'], dv_dict['ul'], self._design_accuracy)
        
        self._entry_name = self.get_design_name(self.current_design_variables)
        if not self.design_check():
            self.search_method()
            
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))