import osbrain
from osbrain import Agent
import ka
import random
import performance_measure as pm

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
        self._objectives = None
        self.lvl_read = None
        self.lvl_write = None
        self._update_hv = False
        self._class = 'reader'
        self.level_clear_number = 20
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_validity(self):
        pass
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.clear_bb_lvl()
        while self._entry_name:
            self.clear_entry()
            self.lvl_write = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
            self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
            
            if self.read_bb_lvl():
                self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel=self.new_panel)
                entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
                self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel)         
        self._trigger_val = 0
        self.action_complete()
            
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.lvl_write = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]

        for panel in self.bb.get_attr('abstract_lvls')['level 3'].values():
            self.lvl_data.update(panel)

        self._num_entries = len(self.lvl_read)

        new_entry = self.read_bb_lvl()
        trig_prob = self._num_entries / self._num_allowed_entries if new_entry else 0
        self._trigger_val = self._trigger_val_base + int(trig_prob) if trig_prob > 0 else 0
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
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel)
                
    def move_dominated_entries(self):
        pass
    
    def remove_dominated_entries(self):
        pass

    def scale_objective(self, val, ll, ul):
        """Scale an objective based on the upper/lower value"""
        if val < ll or val > ul:
            return None
        else:
            return (val - ll) / (ul - ll)
    
class KaBr_lvl1(KaBr):
    """
    Reads `level 1` on the blackboard.
    - Determines pareto optimal solutions
    - Calculates the hypervolume contribution for each entry
    """
    
    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 1
        self._update_hv = False
        self._trigger_val_base = 6
        self._pf_size = 1
        self._lower_objective_reference_point = None
        self._upper_objective_reference_point = None
        self._hvi_dict = {}
        self._lvl_data = {}
        self._designs_to_remove = []
        self._class = 'reader_lvl1'
        self.pf_increase = 1.25
        
    def handler_trigger_publish(self, message):
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        new_pf_size = len(self.lvl_read)
        
        self._trigger_val = self._trigger_val_base if new_pf_size > self._pf_size * self.pf_increase else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))

    def handler_executor(self, message):
        """
        BR_lvl1 calculates the hypervolume contribution for each entry and removed dominated entries
        """
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        self._pf_size = len(self.lvl_read)

        # Make sure this is okay for larger numbers of entries otherwise revert to old method
        for panel in self.bb.get_attr('abstract_lvls')['level 3'].values():
            self._lvl_data.update(panel)
        self.calculate_hvi_contribution()
        if len(self._designs_to_remove) > 0:
            self.remove_dominated_entries()
        self.clear_entry()
        self.action_complete()
            
    def scale_pareto_front(self, pf):
        """
        Scale the objective functions for the pareto front and return a scaled pareto front for the hypervolume.
        """
        # TODO If scale_objective returns a None, we need to figure out how to deal with it.
        # Perhaps cancel the current iteration and tell the BB we are done
        # Should we keep a log of what happened?
        scaled_pf = []
        for x in pf:
            design_objectives = []
            for obj in self._objectives.keys():
                scaled_obj = self.scale_objective(self._lvl_data[x]['reactor parameters'][obj], self._objectives[obj]['ll'], self._objectives[obj]['ul'])
                design_objectives.append(scaled_obj if self._objectives[obj]['goal'] == 'lt' else (1.0-scaled_obj))
            scaled_pf.append(design_objectives)
        return scaled_pf

    def calculate_hvi_contribution(self):
        pf = [x for x in self.lvl_read.keys()]
        scaled_pf = self.scale_pareto_front(pf)
        hvi = self.calculate_hvi(scaled_pf)
        self._designs_to_remove = []
        for design_name, design in zip(pf, scaled_pf):
            design_hvi_contribution = hvi - self.calculate_hvi([x for x in scaled_pf if x != design])
            self._hvi_dict[design_name] = design_hvi_contribution
            if design_hvi_contribution <= 0:
                self._designs_to_remove.append(design_name)
        
    def calculate_hvi(self, pf):
        """
        Calculate the hypervolume indicator for the given pareto front.
        """
        hvi = pm.hypervolume_indicator(pf, self._lower_objective_reference_point, self._upper_objective_reference_point)
        return hvi
    
    def remove_dominated_entries(self):
        """
        Remove designs that do not contibute to the Pareto front (i.e. designs with HV values of 0)
        """
        for design in self._designs_to_remove:
            self.log_info('Removing core {}, no longer optimal'.format(design))
            self._pf_size -= 1
            self.write_to_bb(self.bb_lvl, design, self.lvl_read[design], remove=True)
            
        
class KaBr_lvl2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 1
        self.bb_lvl_read = 2
        self._num_allowed_entries = 10
        self._trigger_val_base = 4
        self._fitness = 0.0
        self._update_hv = True
        self.lvl_data = {}
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1], 'fitness function': self._fitness}
        
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 

        self.clear_bb_lvl()

        while self._entry_name:
            self.clear_entry()
            self.lvl_write = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
            self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
            if self.read_bb_lvl():
                self.write_to_bb(self.bb_lvl, self._entry_name, self._entry)
                entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
                self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel)
        
        self._trigger_val = 0
        self.action_complete()
        
    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        self._fitness = self.determine_fitness_function(core_name, self.lvl_data[core_name]['reactor parameters'])
        
        if self.lvl_write == {}:
            self.log_debug('Design {} is initial optimal design.'.format(core_name))
            return (True, 'pareto')
        pareto_opt = None
        for opt_core in self.lvl_write.keys():
            if opt_core != core_name:
                pareto_opt = self.determine_optimal_type(self.lvl_data[core_name]['reactor parameters'], 
                                                         self.lvl_data[opt_core]['reactor parameters'])
                if pareto_opt == None:
                    return (False, pareto_opt)
        return (True, pareto_opt)
    
    def determine_fitness_function(self, core_name, core_parmeters):
        """
        Calculate the total fitness function based on upper and lower limits.
        """
        fitness = 0
        for param, obj_dict in self._objectives.items():
            scaled_fit = self.scale_objective(core_parmeters[param], obj_dict['ll'], obj_dict['ul'])
            fitness += scaled_fit if obj_dict['goal'] == 'gt' else (1-scaled_fit)
        return round(fitness, 5)
    
    def determine_optimal_type(self, new_rx, opt_rx):
        """Determine if the solution is Pareto, weak, or not optimal"""
        optimal = 0
        pareto_optimal = 0
        for param, obj_dict in self._objectives.items():
            new_val = -new_rx[param] if obj_dict['goal'] == 'gt' else new_rx[param]
            opt_val = -opt_rx[param] if obj_dict['goal'] == 'gt' else opt_rx[param]           
            optimal += 1 if new_val <= opt_val else 0
            pareto_optimal += 1 if new_val < opt_val else 0
            
        if optimal == len(self._objectives.keys()) and pareto_optimal > 0:
            return 'pareto'
        elif pareto_optimal > 0:
            return 'weak'
        else:
            return None

                
class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl = 2
        self.bb_lvl_read = 3
        self._trigger_val_base = 3
        self.lvl_data = {}

        
    def determine_validity(self, core_name):
        """Determine if the core falls in the desired results range"""
        for param_name, obj_dict in self._objectives.items():     
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
