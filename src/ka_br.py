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
        self.lvl_read = None
        self.lvl_write = None
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_validity(self):
        pass
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.clear_bb_lvl()
        if self._entry:
            self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel=self.new_panel, complete=False)
            entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
            self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel, write_complete=True)
        self.clear_entry()
        self._trigger_val = 0
                
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
        lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
        lvl_data = self.bb.get_attr('abstract_lvls')['level 3']
                
        lvl_1 = {}
        for panel in lvl.values():
            lvl_1.update(panel)
        lvl_3 = {}
        for panel in lvl_data.values():
            lvl_3.update(panel)

        self.lvl_write = lvl_1
        self.lvl_read  = lvl_read
        self.lvl_data  = lvl_3
        self._num_entries = len(self.lvl_read)

        new_entry = self.read_bb_lvl()
        trig_prob = self._num_entries / self._num_allowed_entries if new_entry else 0
        self._trigger_val = self._trigger_val_base + int(trig_prob) if trig_prob > random.random() else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def read_bb_lvl(self):
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if valid_core:
                self.add_entry((core_name,opt_type))
                return True
        return False
    
    def clear_bb_lvl(self):
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel, write_complete=False)
                
    def move_dominated_entries(self):
        pass
    
    def remove_dominated_entries(self):
        pass

        
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
        self._dominated_designs = {}
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1], 'fitness function': self._fitness}

    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 

        self.clear_bb_lvl()
        self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel=self.new_panel, complete=False)
        
        self.determine_dominated_cores()
        self.remove_dominated_entries()

        entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
        self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel, write_complete=True)
        
        self.clear_entry()
        self._trigger_val = 0
        
    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        self._fitness = self.determine_fitness_function(core_name, self.lvl_data[core_name]['reactor parameters'])
            
        if self.lvl_write == {}:
            self.log_debug('Core {} is initial core for level 1.'.format(core_name))
            return (True, 'pareto')

        for opt_core in self.lvl_write.keys():
            pareto_opt = self.determine_optimal_type(self.lvl_data[core_name]['reactor parameters'], 
                                                     self.lvl_data[opt_core]['reactor parameters'])
            if pareto_opt == None:
                return (False, pareto_opt)
        return (True, pareto_opt)

    def determine_dominated_cores(self):
        """
        Determing if any cores in level 1 are dominated by any others, if so mark them for removal
        """
        #Update level 1, as we have just added to it likely
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
                    
        lvl_1 = {}
        for panel in lvl.values():
            lvl_1.update(panel)    
        self.lvl_write = lvl_1

        optimal = False
        self._dominated_designs = {}
        for core_1 in self.lvl_write.keys():
            for core_2 in self.lvl_write.keys():
                if core_1 != core_2:
                    pareto_opt = self.determine_optimal_type(self.lvl_data[core_1]['reactor parameters'], 
                                                             self.lvl_data[core_2]['reactor parameters'])
                    if pareto_opt == None:
                        self._dominated_designs[core_1] = self.lvl_write[core_1]
    
    def determine_fitness_function(self, core_name, core_parmeters):
        """
        Calculate the total fitness function based on upper and lower limits.
        """
        fitness = 0
        for param, obj_dict in self._objective_ranges.items():
            scaled_fit = self.objective_scaler(obj_dict['ll'], obj_dict['ul'], core_parmeters[param])
            fitness += scaled_fit if obj_dict['goal'] == 'gt' else (1-scaled_fit)
        return round(fitness, 5)
    
    def determine_optimal_type(self, new_rx, opt_rx):
        """Determine if the solution is Pareto, weak, or not optimal"""
        optimal = 0
        pareto_optimal = 0
        for param, obj_dict in self._objective_ranges.items():
            new_val = -new_rx[param] if obj_dict['goal'] == 'gt' else new_rx[param]
            opt_val = -opt_rx[param] if obj_dict['goal'] == 'gt' else opt_rx[param]            
            optimal += 1 if new_val <= opt_val else 0
            pareto_optimal += 1 if new_val < opt_val else 0
            
        if optimal == len(self._objective_ranges.keys()) and pareto_optimal > 0:
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
                    self.write_to_bb(self.bb_lvl, name, entry, panel=panel_name, complete=False, remove=True)
                    return

    def remove_dominated_entries(self):
        lvl = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
        #Remove any dominated entires on level 1
        for core_name, entry in self._dominated_designs.items():
            self.remove_entry(core_name, entry, lvl)

    def clear_bb_lvl(self):
        """
        Remove any core designs which hvae been dominated
        """
        #Move all dominated entries on level 2
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel, write_complete=False)

                
class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.bb_lvl_read = 3
        self._objective_ranges = None
        self.read_results = []
        self._trigger_val_base = 3
        
    def determine_validity(self, core_name):
        """Determine if the core falls in the desired results range"""
        for param_name, obj_dict in self._objective_ranges.items():     
            param = self.lvl_data[core_name]['reactor parameters'][param_name]
            if param < obj_dict['ll'] or param > obj_dict['ul']:
                return (False, None)
        return (True, None)
    
    def add_entry(self, core_name):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
