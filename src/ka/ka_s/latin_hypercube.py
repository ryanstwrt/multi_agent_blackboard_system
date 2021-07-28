from src.ka.ka_s.base import KaS
import src.utils.utilities as utils
from numpy import random
import copy
import numpy as np
import time

class LatinHypercube(KaS):
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
        self.execute_once = True

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
        for v in self._design_variables.values():
            length += len(v['permutation']) if 'permutation' in v.keys() else 1
        lhd = self.lhs(length, samples=self.samples, criterion=self.lhc_criterion)
        self.lhd = lhd.tolist()
        
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
        self._lvl_data = {}
        self._trigger_event = message[0]
        self._lvl_data = {**message[1]['level {}'.format(self.bb_lvl_data)]['new'], **message[1]['level {}'.format(self.bb_lvl_data)]['old']}          
        self.log_debug('Executing agent {}'.format(self.name))
        self.search_method()

        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.action_complete()
        if not self.execute_once:
            self.generate_lhc()    
        
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
        if criterion == 'simple' or n==1:
            return self._lhsclassic(n, self.samples)
        else:
            return self._lhscorrelate(n, self.samples, iterations)

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
        if len(self.lhd) == 0:
            return
        
        cur_design = self.lhd.pop(0)
        num = 0
        for dv, dv_dict in self._design_variables.items():
            if 'permutation' in self._design_variables[dv]:
                ...
            elif 'options' in dv_dict.keys():
                dv_val = dv_dict['options'][int(len(dv_dict['options']) * cur_design[num])]
                self.current_design_variables[dv] = dv_dict['variable type'](dv_val)            
            else:
                self.current_design_variables[dv] = utils.get_float_val(cur_design[num], dv_dict['ll'], dv_dict['ul'], self._design_accuracy)
            num += 1 if dv_dict['variable type'] != dict else 0
        
        self._entry_name = self.get_design_name(self.current_design_variables)
        if self._entry_name not in self._lvl_data.keys():
            self.calc_objectives()
            self.write_to_bb(self.bb_lvl_data, self._entry_name, self._entry, panel='new')
            self.clear_entry()
                  
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))
        if self.kill_switch:
            self.log_info('Returning agent to allow for shutdown.')            
            return
        else:
            self.search_method()