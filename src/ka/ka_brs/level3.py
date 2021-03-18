from src.ka.ka_brs.base import KaBr


class KaBrLevel3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl_write = 2
        self.bb_lvl_read = 3
        self._trigger_val_base = 3.00000000001
        self._class = 'reader level 3'
  
    def add_entry(self, core_name):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
        
    def determine_validity(self, core_name):
        """Determine if the core falls within objective ranges and constrain ranges"""
        if self._constraints:
            for constraint, constraint_dict in self._constraints.items():
                constraint_value = self._lvl_data[core_name]['constraints'][constraint]
                violated = self.test_float_int(constraint_value, constraint_dict) if type(constraint_value) == (float or int) else self.test_list(constraint_value, constraint_dict)
                if violated:
                    return (False, None)  
        
        for obj_name, obj_dict in self._objectives.items():     
            obj_value = self._lvl_data[core_name]['objective functions'][obj_name]
            violated = self.test_float_int(obj_value, obj_dict) if type(obj_value) == (float or int) else self.test_list(obj_value, obj_dict)
            if violated:
                return (False, None)               
        return (True, None)
   
    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        self.lvl_read =  self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
        self.lvl_write = self.update_abstract_level(self.bb_lvl_write, panels=[self.new_panel])
        self._lvl_data = self.lvl_read
