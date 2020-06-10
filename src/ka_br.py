import osbrain
from osbrain import Agent
import ka
import random

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
        self._num_entries = 0
        self._num_allowed_entries = 25
        self._trigger_val_base = 0
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_validity(self):
        pass
    
    def handler_executor(self, message):
        self.clear_bb_lvl()
        new_entry = self.read_bb_lvl()
        self.log_debug('Executing agent {}'.format(self.name)) 
        if new_entry:
            self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel=self.new_panel, complete=False)
            entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
            self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel, write_complete=True)
        self.clear_entry()
        self._trigger_val = 0
                
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        new_entry = self.read_bb_lvl()
        trig_prob = self._num_entries / self._num_allowed_entries if new_entry else 0
        self._trigger_val = self._trigger_val_base + int(trig_prob) if trig_prob > random.random() else 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        
    def read_bb_lvl(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        self._num_entries = len(lvl)

        for core_name, core_entry in lvl.items():
            valid = self.determine_validity(core_name)
            if valid[0]:
                self.add_entry((core_name,valid[1]))
                return True
        return False
    
    def clear_bb_lvl(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]

        for core_name, core_entry in lvl.items():
            valid = self.determine_validity(core_name)
            if not valid[0]:
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel, write_complete=False)

        
class KaBr_lvl2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 2
        self.desired_results = None
        self._objective_ranges = None
        self._num_allowed_entries = 10
        self._trigger_val_base = 4
        self._fitness = 0.0
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1], 'fitness function': self._fitness}
        
    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
        lvl_read = self.bb.get_attr('abstract_lvls')['level 3']
        
        #makes a dictionary of all the cores present in the level
        lvl_3 = {}
        for panel in lvl_read.values():
            lvl_3.update(panel)
            
        self._fitness = self.determine_fitness_function(core_name, lvl_3[core_name]['reactor parameters'])
                    
        lvl_1 = {}
        for panel in lvl.values():
            lvl_1.update(panel)
            
        if lvl_1 == {}:
            self.log_debug('Core {} is initial core for level 1.'.format(core_name))
            return (True, 'pareto')
        
        optimal = False
        dominated_designs = {}
        for opt_core in lvl_1.keys():
            pareto_opt = self.determine_optimal_type(lvl_3[core_name]['reactor parameters'], 
                                                     lvl_3[opt_core]['reactor parameters'])          
            if pareto_opt:
                self.log_debug('Core {} is {} optimal.'.format(core_name,pareto_opt))
                optimal = True
                if pareto_opt == 'pareto':
                    dominated_designs[opt_core] = lvl_1[opt_core]
        for core_name, entry in dominated_designs.items():
            self.remove_entry(core_name, entry, lvl)
        return (optimal, pareto_opt)

    def determine_fitness_function(self, core_name, core_parmeters):
        fitness =0
        for param, symbol in self.desired_results.items():
            scaled_fit = self.objective_scaler(self._objective_ranges[param][0], self._objective_ranges[param][1], core_parmeters[param])
            fitness += scaled_fit if symbol == 'gt' else (1-scaled_fit)
        return round(fitness, 5)
    
    def determine_optimal_type(self, new_rx, opt_rx):
        """Determine if the solution is Pareto, weak, or not optimal"""
        optimal = 0
        pareto_optimal = 0
        for param, symbol in self.desired_results.items():
            new_val = -new_rx[param] if symbol == 'gt' else new_rx[param]
            opt_val = -opt_rx[param] if symbol == 'gt' else opt_rx[param]            
            optimal += 1 if new_val <= opt_val else 0
            pareto_optimal += 1 if new_val < opt_val else 0

        if optimal == len(self.desired_results.keys()) and pareto_optimal > 0:
            return 'pareto'
        elif pareto_optimal > 0:
            return 'weak'
        else:
            return None
        
    def objective_scaler(self, minimum, maximum, value):
        """Scale the objective function between the minimum and maximum allowable values"""
        return (maximum - value) / (maximum-minimum)
    
    def remove_entry(self, name, entry, level):
        """Remove an entry that has been dominated."""
        for panel_name, panel_entries in level.items():
            for core in panel_entries.keys():
                if core == name:
                    self.log_info('Removing core {}, no longer optimal'.format(name))
                    self.write_to_bb(self.bb_lvl, name, entry, panel=panel_name,remove=True)
                    return
    
class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.bb_lvl_read = 3
        self.desired_results = None
        self.read_results = []
        self._trigger_val_base = 3
        
    def determine_validity(self, core_name):
        """Determine if the core falls in the desired results range"""
        lvl_3 = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new']
        rx_params = lvl_3[core_name]['reactor parameters']

        for param_name, param_range in self.desired_results.items():     
            param = rx_params[param_name]
            if param < param_range[0] or param > param_range[1]:
                return (False, None)
        return (True, None)
    
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
