from mabs.ka.ka_s.base import KaLocal
import copy
from numpy import random
import time

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
        self.additional_perturbations = 0
        self.neighborhood_search = 'fixed'
        self._class = 'local search neighborhood search'
        
    def get_perturbed_design(self,dv,design_,pert):
        dv_value = design_[dv]
        dv_type = type(dv_value)
        design = copy.copy(design_)
        if 'permutation' in self._design_variables[dv]:
            idx = range(len(self._design_variables[dv]['permutation']))
            i1, i2 = random.choice(idx, size=2, replace=False)
            design[dv][i1], design[dv][i2] = design[dv][i2], design[dv][i1]
        elif 'options' in self._design_variables[dv]:
            options = copy.copy(self._design_variables[dv]['options'])
            options.remove(self._design_variables[dv]['variable type'](design[dv]))
            design[dv] = dv_type(random.choice(options))
        else:
            dv_value = dv_type(round(dv_value * pert, self._design_accuracy))
            dv_value = self._design_variables[dv]['ll'] if dv_value < self._design_variables[dv]['ll'] else dv_value
            dv_value = self._design_variables[dv]['ul'] if dv_value > self._design_variables[dv]['ul'] else dv_value
            design[dv] = dv_value
            #design[dv] = dv_type(round(dv_value * pert, self._design_accuracy)) #if 
        return design
        
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
        design = {}
        dv_keys = [x for x in design_.keys()]
        pert = self.perturbation_size if self.neighborhood_search == 'fixed' else random.uniform(0,self.perturbation_size)
        perts = [1.0 - pert, 1.0 + pert]
        pert_designs = []
            
        
        if self.additional_perturbations > len(dv_keys) - 1:
            self.log_warning(f'Additional perturbations set to {self.additional_perturbations}, which is greater than number of design variabels {len(dv_keys)} minus 1. Seting additional_perturbations to {len(dv_keys) - 1}.')
            self.additional_perturbations = len(dv_keys) - 1
            
        for dv in dv_keys:
            for pert in perts:
                dvs_left = copy.copy(dv_keys)
                design = self.get_perturbed_design(dv,design_, pert)
                multi_perts = self.additional_perturbations
                while multi_perts > 0:
                    dvs_left.remove(dv)
                    dv = random.choice(dvs_left)
                    design = self.get_perturbed_design(dv,design,random.choice(perts))
                    multi_perts -= 1
                pert_designs.append((dv,copy.deepcopy(design)))

        for dv, design in pert_designs:
            self.current_design_variables = design
            self._entry_name = self.get_design_name(self.current_design_variables)
            if self.determine_model_applicability(dv):
                if self.parallel:
                    self.parallel_executor()
                else:
                    self.calc_objectives()
                    self.determine_write_to_bb() 
            if self.kill_switch:
                self.log_info('Returning agent to allow for shutdown.')
                return
        if self.parallel:
            self.determine_parallel_complete()
        self.analyzed_design[core] = {'Analyzed': True}
