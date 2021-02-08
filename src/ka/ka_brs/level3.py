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
                if constraint_value < constraint_dict['ll'] or constraint_value > constraint_dict['ul']:
                    return (False, None)
        
        for obj_name, obj_dict in self._objectives.items():     
            obj_value = self._lvl_data[core_name]['objective functions'][obj_name]
            if type(obj_value) == (float or int):
                if obj_value < obj_dict['ll'] or obj_value > obj_dict['ul']:
                    return (False, None)
            elif type(obj_value) == list:
                for num, val in enumerate(obj_value):
                    ll = obj_dict['ll'][num] if type(obj_dict['ll']) == list else obj_dict['ll']
                    ul = obj_dict['ul'][num] if type(obj_dict['ul']) == list else obj_dict['ul']
                    if val < ll or val > ul:
                        return (False, None)                   
        return (True, None)
        
    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        self.lvl_read =  self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
        self.lvl_write = self.update_abstract_level(self.bb_lvl_write, panels=[self.new_panel])
        self._lvl_data = self.lvl_read
