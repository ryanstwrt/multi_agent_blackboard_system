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
        
    def read_bb_lvl(self):
        pass

    def handler_trigger_publish(self, message):
        """Read the BB level that it is qualified to read and determine if an entry is available."""
        new_entry = self.read_bb_lvl()
        self._trigger_val = 10 if new_entry else 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val)) 

        
class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is optimal.
    
    Option 1: Panels - new and old data have their own panels to prevent reread
    Option 2: KA pushes data from level 3 to level 4 if it is not optimal
    Showcase if a constraint is to constrictive, we loose up our desired results by 5%?
    
    """
    def on_init(self):
        super().init()
        self.bb_level = 2
        self.bb_read_level = 3
        self.desired_results = None
        self.valid_results = []
        
    def determine_valid_core(self, rx_params):
        """Determine if the core falls in the desired results range"""
        for param_name, param_range in self.desired_results.items():
            param = rx_params[param_name]
            if param < param_range[0] or param > param_range[1]:
                return False
        return True
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.write_to_bb()
        

    def read_bb_lvl(self):
        """Read the information from the blackboard and determine if a new solution is better thatn the previous"""
        lvl_2 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        for core_name, entry in lvl_2.items():
            valid = self.determine_valid_core(entry['reactor parameters'])
            if valid and core_name not in self.valid_results:
                self.valid_results.append(core_name)
                self._entry_name = core_name
                self._entry = {'valid': True, 'reactor parameters': entry['reactor parameters']}
                return True
        return False
                
   
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
