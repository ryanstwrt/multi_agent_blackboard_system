from src.ka.ka_brs.base import KaBr
import src.utils.utilities as utils
import time

class KaBrLevel2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl_write= 1
        self.bb_lvl_read = 2
        self._num_allowed_entries = 10
        self._trigger_val_base = 4.00000000002
        self._fitness = 0.0
        self._class = 'reader level 2'
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1], 'fitness function': self._fitness}

    def convert_fitness_to_minimzation(self, obj, obj_val):
        """
        Convert the fitness function value to a minimization problem
        """
        
        goal = self._objectives[obj]['goal']
        if goal == 'gt':
            return obj_val
        elif goal =='lt':
            return 1.0 - obj_val
        elif goal =='et':
            target = utils.scale_value(self._objectives[obj]['target'], self._objectives[obj])
            return (1.0 - 2 * abs(target - obj_val))
    
    def determine_fitness_function(self, core_name, core_objectives):
        """
        Calculate the total fitness function based on upper and lower limits.
        """
        fitness = 0
        for obj, obj_dict in self._objectives.items():
            scaled_fit = utils.scale_value(core_objectives[obj], obj_dict)
            goal = self._objectives[obj]['goal type'] if 'goal type' in self._objectives[obj] else None
            scaled_fit = utils.get_objective_value(scaled_fit, goal)
            try:
                fitness += self.convert_fitness_to_minimzation(obj, scaled_fit)
            except TypeError:
                fitness += 0

        return fitness        
        
    def handler_executor(self, message):
        
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name)) 

        self.lvl_read =  message[1]['level {}'.format(self.bb_lvl_read)][self.new_panel] 
        self.lvl_write = message[1]['level {}'.format(self.bb_lvl_write)] 
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)
        
        self.clear_bb_lvl()
        for core_name in self.lvl_read.keys():
            self.clear_entry()
            valid_core, opt_type = self.determine_validity(core_name)
            if valid_core:
                self.add_entry((core_name, opt_type))
                # Add this entry to the  write level
                self.write_to_bb(self.bb_lvl_write, self._entry_name, self._entry)
                # Move this entry from the new panel to the old panel on the read level
                self.move_entry(self.bb_lvl_read, self._entry_name, self.lvl_read[self._entry_name], self.old_panel, self.new_panel)
        
        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.action_complete()      

    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.lvl_read =  message['level {}'.format(self.bb_lvl_read)][self.new_panel] 
        self.lvl_write = message['level {}'.format(self.bb_lvl_write)]
        lvl = {}
        for panel in message['level {}'.format(self.bb_lvl_data)].values():
            lvl.update(panel)
        self._lvl_data = lvl        
        self._num_entries = len(self.lvl_read)

        self._trigger_val = 0
        if self.read_bb_lvl():
            self._trigger_val = self._num_entries / self._num_allowed_entries * self._trigger_val_base if self._num_entries > self._num_allowed_entries else self._trigger_val_base
            
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))        
        
    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        
        We add a try, except for the multi-agent case where the blackboard dictionary can change size due to another agent interacting with it.
        """
        try:
            self.lvl_read =  self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
            self.lvl_write = self.update_abstract_level(self.bb_lvl_write)
            self._lvl_data = self.update_abstract_level(self.bb_lvl_data, panels=[self.new_panel, self.old_panel])
        except RuntimeError:
            self.update_abstract_levels()