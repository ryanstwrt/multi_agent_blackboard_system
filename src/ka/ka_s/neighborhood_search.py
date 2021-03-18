from src.ka.ka_s.base import KaLocal
import copy
from numpy import random

class NeighborhoodSearch(KaLocal):
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
        self.perturbation_size = 0.05
        self.neighboorhod_search = 'fixed'
        self._class = 'local search neighborhood search'
        
    def search_method(self):
        """
        Perturb a core design
        
        This first selects a core at random from abstract level 1 (from the 'new' panel).
        It then perturbs each design variable independent by the values in perturbations, this produces n*m new cores (n = # of design variables, m = # of perturbations)
        
        These results are written to the BB level 3, so there are design_vars * pert added to level 3.
        """
        core = self.select_core()
        if core == False:
            return
        design_ = self._lvl_data[core]['design variables']
        dv_keys = [x for x in design_.keys()]
        pert = self.perturbation_size if self.neighboorhod_search == 'fixed' else random.uniform(0,self.perturbation_size)
        perts = [1.0 - pert, 1.0 + pert]
        pert_designs = []
            
        for dv in dv_keys:
            dv_value = design_[dv]
            design = copy.copy(design_)
            if 'options' in self._design_variables[dv]:
                options = copy.copy(self._design_variables[dv]['options'])
                dv_type = type(dv_value)
                options.remove(design[dv])
                design[dv] = dv_type(random.choice(options))
                pert_designs.append((dv,design))                
            else:
                for pert in perts:
                    design[dv] = round(dv_value * pert, self._design_accuracy)
                    pert_designs.append((dv,design))
                    design = copy.copy(design_)
        for dv, design in pert_designs:
            self.current_design_variables = design
            self._entry_name = self.get_design_name(self.current_design_variables)
            self.determine_model_applicability(dv)
        
        self.analyzed_design[core] = {'Analyzed': True}