from mabs.ka.base import KaBase
import time
import mabs.utils.utilities as utils

class KaBr(KaBase):
    """
    Base function for reading a BB level and performing some type of action.
    
    Inherits from KaBase
    
    """
    
    def on_init(self):
        super().on_init()
        self.bb_lvl_read = 0
        self.bb_lvl_write = 0
        self.bb_lvl_data = 3
        self.new_panel = 'new'
        self.old_panel = 'old'
        self._num_entries = 0
        self._num_allowed_entries = 125
        self._trigger_val_base = 0
        self._objectives = None
        self._constraints = None
        self.lvl_read = {}
        self.lvl_write = {}
        self._lvl_data = {}
        self._class = 'reader'
        self.agent_time = 0
        self.agent_time = 0
        self._trigger_event = 0
        
    def add_entry(self, core_name):
        ...

    def action_complete(self):
        """
        Send a message to the BB indicating it's completed its action
        """
        self.send(self._complete_alias, (self.name, self.agent_time, self._trigger_event))

    def clear_bb_lvl(self):
        move = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                move.append(core_name)
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel)
        for core in move:
            self.lvl_read.pop(core)        
        
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_optimal_type(self, new_rx, opt_rx):
        """Determine if the solution is Pareto, weak, or not optimal"""
        optimal = 0
        pareto_optimal = 0
        for obj, obj_dict in self._objectives.items():
            new_val = utils.convert_objective_to_minimize(obj_dict, new_rx[obj])
            opt_val = utils.convert_objective_to_minimize(obj_dict, opt_rx[obj])       
            optimal += 1 if new_val <= opt_val else 0
            pareto_optimal += 1 if new_val < opt_val else 0
            
        if optimal == len(self._objectives.keys()) and pareto_optimal > 0:
            return 'pareto'
        elif optimal == len(self._objectives.keys()):
            return 'weak'
        elif pareto_optimal > 0:
            return 'weak'
        else:
            return 'dominated'
             

    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        if 'level 2' in self._class:
            self._fitness = self.determine_fitness_function(core_name, self._lvl_data[core_name]['objective functions'])
        
        if self.lvl_write == {}:
            self.log_debug('Design {} is initial optimal design.'.format(core_name))
            return (True, 'pareto')

        pareto_opt = None
        for opt_core in self.lvl_write.keys():
            if opt_core != core_name:
                pareto_opt = self.determine_optimal_type(self._lvl_data[core_name]['objective functions'], 
                                                         self._lvl_data[opt_core]['objective functions'])
                if pareto_opt == 'dominated':
                    return (False, pareto_opt)
        return (True, pareto_opt)        
        
    def get_objective_value(self, core, obj):
        objective_value = self._lvl_data[core]['objective functions'][obj]
        goal = self._objectives[obj]['goal type'] if 'goal type' in self._objectives[obj] else None
        return utils.get_objective_value(objective_value, goal)    
    
    def handler_executor(self, message):
        t = time.time()
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))
        
        self.lvl_read =  message[1]['level {}'.format(self.bb_lvl_read)][self.new_panel] 
        self.lvl_write = message[1]['level {}'.format(self.bb_lvl_write)][self.new_panel]
        self._lvl_data = self.lvl_read

        self.clear_bb_lvl()
        for entry_name in self.lvl_read.keys():
            self.clear_entry()
            self.add_entry((entry_name, True))
            self.write_to_bb(self.bb_lvl_write, self._entry_name, self._entry, panel=self.new_panel)
            entry = self.lvl_read[self._entry_name]
            self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel) 
        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.log_info(f'Time Required: {self.agent_time}')
        self.action_complete()
            
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.lvl_read =  message['level {}'.format(self.bb_lvl_read)][self.new_panel] 
        self.lvl_write = message['level {}'.format(self.bb_lvl_write)][self.new_panel]
        self._lvl_data = self.lvl_read
        
        self._num_entries = len(self.lvl_read)
        
        self._trigger_val = 0
        if self.read_bb_lvl():
            self._trigger_val = self._num_entries / self._num_allowed_entries + self._trigger_val_base if self._num_entries > self._num_allowed_entries else self._trigger_val_base
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def read_bb_lvl(self):
        """
        Read the BB level corresponding to the KA lvl_read and return if a valid core is present
        
        Returns
        --------
        Bool : 
            True if a valid core is found, false if not valid core is found in the lvl_read
        """
        for core_name in self.lvl_read.keys():
            valid_core, opt_type = self.determine_validity(core_name)
            if valid_core:
                self.add_entry((core_name,opt_type))
                return True
        return False
                   
    def remove_dominated_entries(self):
        ...

    def update_abstract_levels(self):
        ...
    
    def update_abstract_level(self, level_num, panels=[]):
        """
        Update a single abstract level for the KA
        """
        level_obj = {}
        if panels:
            for panel in panels:
                level_obj.update(self.bb.get_blackboard()['level {}'.format(level_num)][panel])
        else:
            level_obj = self.bb.get_blackboard()['level {}'.format(level_num)]
        return level_obj