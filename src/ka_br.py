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
        self.new_panel = 'new'
        self.old_panel = 'old'
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_validity(self):
        pass

    def move_current_entry(self, bb_lvl, entry_name, entry):
        self.write_to_bb(bb_lvl, panel=self.old_panel)
        self.write_to_bb(bb_lvl, panel=self.new_panel, remove=True)
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.write_to_bb(self.bb_lvl, panel=self.new_panel)
        self.clear_entry()
                
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        new_entry = self.read_bb_lvl()
        self._trigger_val = 10 if new_entry else 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))

    def read_bb_lvl(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        lvl = lvl[self.new_panel] if self.bb_lvl_read != 3 else lvl

        for core_name, core_entry in lvl.items():
            valid = self.determine_validity(core_name)
            if self.bb_lvl_read !=3:
                self.move_current_entry(self.bb_lvl_read, core_name, core_entry)
            if valid[0]:
                self.add_entry((core_name,valid[1]))
                return True
        
class KaBr_lvl2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 2
        self.desired_results = None
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1]}
        
    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
        lvl_3 = self.bb.get_attr('abstract_lvls')['level 3']

        #make a dictionary of all the cores present in the level
        all_cores = {}
        for panel in lvl.values():
            all_cores.update(panel)
            
        if all_cores == {}:
            return (True, 'pareto')
            
        for opt_core in all_cores.keys():
            pareto_opt = self.determine_optimal_type(lvl_3[core_name]['reactor parameters'], 
                                                     lvl_3[opt_core]['reactor parameters'])
            if pareto_opt:
                self.log_info('Core {} is {} optimal.'.format(core_name,pareto_opt))
                return (True, pareto_opt)
        return (False, pareto_opt)

    def determine_optimal_type(self, new_rx, opt_rx):
        """Determine if the solution is Pareto, weak, or not optimal"""
        optimal = 0
        pareto_optimal = 0
        for param, symbol in self.desired_results.items():
            new_val = -new_rx[param] if symbol == 'gt' else new_rx[param]
            opt_val = -opt_rx[param] if symbol == 'gt' else opt_rx[param]
            if new_val <= opt_val:
                optimal += 1
            if new_val < opt_val:
                pareto_optimal += 1
                
        if optimal == len(opt_rx.keys()) and pareto_optimal > 0:
            return 'pareto'
        elif pareto_optimal > 0:
            return 'weak'
        else:
            return None
    
    def remove_entry(self):
        """Remove an entry that has been dominated."""
        pass
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.write_to_bb(self.bb_lvl, panel=self.new_panel)
        self.remove_entry()
        self.clear_entry()
                

class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.bb_lvl_read = 3
        self.desired_results = None
        
    def determine_validity(self, core_name):
        """Determine if the core falls in the desired results range"""
        lvl_3 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        rx_params = lvl_3[core_name]['reactor parameters']

        for param_name, param_range in self.desired_results.items():            
            param = rx_params[param_name]
            if param < param_range[0] or param > param_range[1]:
                return (False, None)
        return (True, None)
    
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
        
            
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
        self.write_to_bb(self.bb_lvl)

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
