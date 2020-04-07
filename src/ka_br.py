import osbrain
from osbrain import Agent
import time
import random
import os
import ka

class KaBr(ka.KaBase):
    """
    Base function for reading a BB level and performing some type of action.
    
    Inherits from KaBase
    
    """
    
    def on_init(self):
        super().on_init()
        self.bb_lvl_read = 0
    
    def determine_validity(self):
        pass
    
    def read_bb_lvl(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        lvl3 = self.bb.get_attr('abstract_lvls')['level 3']
        for core_name in lvl.keys():
            valid = self.determine_validity(lvl3[core_name]['reactor parameters'])
            if valid:
                self.add_entry(core_name)
                return True

    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.write_to_bb()
        self.clear_entry()
                
    def handler_trigger_publish(self, message):
        """Read the BB level that it is qualified to read and determine if an entry is available."""
        new_entry = self.read_bb_lvl()
        self._trigger_val = 10 if new_entry else 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        

class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.bb_lvl_read = 3
        self.desired_results = None
        
    def determine_validity(self, rx_params):
        """Determine if the core falls in the desired results range"""
        self.log_info(rx_params)
        for param_name, param_range in self.desired_results.items():            
            param = rx_params[param_name]
            if param < param_range[0] or param > param_range[1]:
                return False
        return True
    
    def add_entry(self, core_name):
        self._entry_name = core_name
        self._entry = {'valid': True}
        
class KaBr_lvl2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 2
        self.desired_results = None
        self.valid_results = []
        
    def determine_validity(self, rx_params):
        """Determine if the core is pareto optimal"""
        lvl_2 = self.bb.get_attr('abstract_lvls')['level 2']
        
        for opt_core, entry in lvl_2.items():
            opt_params = entry['reactor parameters']
            pareto_opt = self.determine_pareto_optimal()
            if pareto_opt != None:
                self._entry_name = opt_core
                self._entry = {'pareto': pareto_opt}

    def determine_optimal_type(self):
        """Determine if the solution is Pareto, weak, or not optimal"""
        pass
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.write_to_bb()
                
   
class KaBr_verify(KaBr):
    """Reads `level 2` to verify the components of the MABS are working correctly.
    
    Inherets from KaBr
    """

    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 2
        self.desired_results = None

    def determine_valid_core(self, rx_params):
        """Determine if the core falls in the desired results range"""
        for param_name, param_range in self.desired_results.items():
            param = rx_params[param_name]
            if param < param_range[0] or param > param_range[1]:
                return False
        return True
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name))
        self.read_bb_lvl()
        self.write_to_bb()

    def read_bb_lvl(self):
        """Read the information from the blackboard and determine if a new solution is better thatn the previous"""
        lvl_2 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        for core_name, entry in lvl_2.items():
            valid = self.determine_valid_core(entry['reactor parameters'])
            if valid:
                self._entry_name = core_name
                self._entry = {'valid': True}
                return True
        return False
