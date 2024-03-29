import src.ka as ka
import src.performance_measure as pm
import time

class KaBr(ka.KaBase):
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
        self._num_allowed_entries = 25
        self._trigger_val_base = 0
        self._objectives = None
        self._constraints = None
        self.lvl_read = {}
        self.lvl_write = {}
        self._lvl_data = {}
        self._update_hv = False
        self._class = 'reader'
        self.level_clear_number = 20
    
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
    def determine_validity(self, core_name):
        """Determine if the core is pareto optimal"""
        if 'lvl2' in self._class:
            self._fitness = self.determine_fitness_function(core_name, self._lvl_data[core_name]['objective functions'])
        
        if self.lvl_write == {}:
            self.log_debug('Design {} is initial optimal design.'.format(core_name))
            return (True, 'pareto')

        pareto_opt = None
        for opt_core in self.lvl_write.keys():
            if opt_core != core_name:
                pareto_opt = self.determine_optimal_type(self._lvl_data[core_name]['objective functions'], 
                                                         self._lvl_data[opt_core]['objective functions'])
                if pareto_opt == None:
                    return (False, pareto_opt)
        return (True, pareto_opt)
    
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name))
        self.update_abstract_levels()
        self.clear_bb_lvl()
        self.lvl_read = self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
        for entry_name in self.lvl_read.keys():
            self.clear_entry()
            self.add_entry((entry_name, True))
            self.write_to_bb(self.bb_lvl_write, self._entry_name, self._entry, panel=self.new_panel)
            entry = self.lvl_read[self._entry_name]
            self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel) 
        self._trigger_val = 0
        self.action_complete()
            
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.update_abstract_levels()
        self._num_entries = len(self.lvl_read)

        new_entry = self.read_bb_lvl()
        trig_prob = self._num_entries / self._num_allowed_entries if new_entry else 0
        self._trigger_val = self._trigger_val_base + int(trig_prob) if trig_prob > 0 else 0
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
    
    def clear_bb_lvl(self):
        move = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel)
#        self.update_abstract_levels()
                
    def remove_dominated_entries(self):
        pass

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
    
    def scale_objective(self, val, ll, ul):
        """Scale an objective based on the upper/lower value"""
        if val < ll or val > ul:
            return None
        else:
            return (val - ll) / (ul - ll)
        
    def scale_list_objective(self, val_list, ll, ul, goal_type):
        """Scale an objective based on the upper/lower value"""
        scaled_list = []
        for num, val in enumerate(val_list):
            lower = ll[num] if type(ll) == list else ll
            upper = ul[num] if type(ul) == list else ul
            scaled_list.append(self.scale_objective(val, lower, upper))

        scaled_val = self.list_objective_value(scaled_list, goal_type)

        return scaled_val
    
    def list_objective_value(self, obj_list, goal_type):
        """
        Returns a single value to use as either a fitness function or Pareto indicator if our objective is a list
        """
        
        if goal_type == 'max':
            obj_val = max(obj_list)
        elif goal_type == 'min':
            obj_val = min(obj_list)
        else:
            obj_val = sum(obj_list)/len(obj_list)   
            
        return obj_val
    
    def get_objective_value(self, core, obj):
        objective_value = self._lvl_data[core]['objective functions'][obj]
        if (type(objective_value) == float) or (type(objective_value) == int):
            return objective_value
        elif type(objective_value) == list:
            return self.list_objective_value(objective_value, self._objectives[obj]['goal type'])        

    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        pass
    
    def update_abstract_level(self, level_num, panels=[]):
        """
        Update a single abstract level for the KA
        """
        level_obj = {}
        if panels:
            for panel in panels:
                level_obj.update(self.bb.get_attr('abstract_lvls')['level {}'.format(level_num)][panel])
        else:
            level_obj = self.bb.get_attr('abstract_lvls')['level {}'.format(level_num)]
        return level_obj
            
            
class KaBr_lvl1(KaBr):
    """
    Reads `level 1` on the blackboard.
    - Determines pareto optimal solutions
    - Calculates the hypervolume contribution for each entry
    """
    
    def on_init(self):
        super().on_init()
        self.bb_lvl_write= 1
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
        self.total_pf_size = 100
        self._previous_pf = None
        self.dci = False
        self.dci_div = None
        self._nadir_point = None
        self._ideal_point = None
        self.pareto_sorter = 'non-dominated'
        
    def handler_trigger_publish(self, message):
        self.lvl_read = self.update_abstract_level(self.bb_lvl_read)
        self.lvl_write = self.lvl_read
        new_pf_size = len(self.lvl_read)
        
        self._trigger_val = self._trigger_val_base if new_pf_size > self._pf_size * self.pf_increase else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))

    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        self.lvl_read =  self.update_abstract_level(self.bb_lvl_read)
        self.lvl_write = self.lvl_read
        self._lvl_data = self.update_abstract_level(self.bb_lvl_data, panels=[self.new_panel, self.old_panel])
        
    def handler_executor(self, message):
        """
        The executor handler for KA-BR-lvl1 maintains the Pareto front.
        There are currently two methods for maintaining the blackboard; hyper volume indicator (HVI) and diversity comarison indicator (DCI) accelerate HVI
        
        HVI calculates the HVI contribution for each solution on the Pareto front and removes solutions which contribute little to the total hypervolume of the size of the Pareto fron ti greater than self.total_pf_size
        
        DCI accelerated HVI uses the DCI to remove solutions which are closeby to help increase the diversity of the Pareto front.
        """
        self.log_debug('Executing agent {}'.format(self.name))
        #Update this to figure out an appropriate naming scheme for levels
        self.update_abstract_levels()
        self.clear_bb_lvl()
        self._pf_size = len(self.lvl_read)
        self._hvi_dict = {}

        if self.pareto_sorter == 'dci':
            self.calculate_dci()
        elif self.pareto_sorter == 'hvi':
            self.calculate_hvi_contribution()
            if self._pf_size > self.total_pf_size:
                self.prune_pareto_front()            
        elif self.pareto_sorter == 'dci hvi':
            self.calculate_dci()
            if self._pf_size > self.total_pf_size:
                self.calculate_hvi_contribution()
                self.prune_pareto_front()
        else:
            self.log_debug('Pareto Sorter ({}) not recognized, please select from `non-dominated`, `dci`, `hvi`, or `dci hvi`. Automatically selecting `non-dominated`'.format(self.pareto_sorter)) 
        self.clear_entry()
        self.action_complete()
    
    def prune_pareto_front(self):
        """
        Remove locations of the Pareto front to reduce the overall size.
        """
        # TODO Add a function to prevent removing the highest/lowest values?
        removal = []
        hvi_contributions = sorted([x for x in self._hvi_dict.values()])
        hvi_contribution_limit = hvi_contributions[self._pf_size - self.total_pf_size]
        for design, contribution in self._hvi_dict.items():
            if contribution < hvi_contribution_limit:
                removal.append(design)
        self.remove_dominated_entries(removal)
            
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
            # This part of the loop is identical to the determine fitness function... perhaps create a function in KA_RP and merge
            for obj in self._objectives.keys():
                if (self._objectives[obj]['variable type'] == float) or (self._objectives[obj]['variable type'] ==  int):
                    scaled_obj = self.scale_objective(self._lvl_data[x]['objective functions'][obj], self._objectives[obj]['ll'], self._objectives[obj]['ul'])
                elif self._objectives[obj]['variable type'] == list:
                    scaled_obj = self.scale_list_objective(self._lvl_data[x]['objective functions'][obj], self._objectives[obj]['ll'], self._objectives[obj]['ul'], self._objectives[obj]['goal type'])
                design_objectives.append(scaled_obj if self._objectives[obj]['goal'] == 'lt' else (1.0-scaled_obj))
            scaled_pf.append(design_objectives)
        return scaled_pf

    def calculate_hvi_contribution(self):
        pf = [x for x in self.lvl_read.keys()]
        scaled_pf = self.scale_pareto_front(pf)
        # Get the HVI from the blackboard rather than calculating it
        hvi = self.calculate_hvi(scaled_pf)
        designs_to_remove = []
        
        for design_name, design in zip(pf, scaled_pf):
            design_hvi_contribution = hvi - self.calculate_hvi([x for x in scaled_pf if x != design])
            if design_hvi_contribution <= 0:
                designs_to_remove.append(design_name)
            else:
                self._hvi_dict[design_name] = design_hvi_contribution
        if designs_to_remove != []:
            self.remove_dominated_entries(designs_to_remove)
            
    def calculate_hvi(self, pf):
        """
        Calculate the hypervolume indicator for the given pareto front.
        """
        hvi = pm.hypervolume_indicator(pf, self._lower_objective_reference_point, self._upper_objective_reference_point)
        return hvi    
    
    def calculate_dci(self):
        """
        Calculate the DCI for the new pareto front
        """
        pf = {name: {obj: self.get_objective_value(name, obj) for obj in self._objectives.keys()} for name in self.lvl_read.keys()}
            
        try:
            pf_old = {name: {obj: self.get_objective_value(name, obj) for obj in self._objectives.keys()} for name in self._previous_pf}
            total_pf = [pf,pf_old]
        except TypeError:
            pf_old = []
            total_pf = [pf]
         
        # Calculate DCI for new/old pareto front
        dci = pm.diversity_comparison_indicator(self._nadir_point, self._ideal_point, total_pf, goal={obj_name: obj['goal'] for obj_name, obj in self._objectives.items()}, div=self.dci_div)
        dci._grid_generator()
        dci.compute_dci(pf)
        dci_new = dci.dci
        dc = dci.dc
        if pf_old != []:
            dci.compute_dci(pf_old)
            dci_diff = abs(dci_new - dci.dci)
        
        designs_to_compare = {}
        for design_name in pf.keys():
            if design_name in dc:
                design_pos = dc[design_name]['grid position']
                try:
                    if design_pos in designs_to_compare:
                        designs_to_compare[design_pos].update({design_name: self.lvl_read[design_name]['fitness function']})
                    else:
                        designs_to_compare[dc[design_name]['grid position']] = {design_name: self.lvl_read[design_name]['fitness function']}
                except KeyError:
                    pass
            
            
        designs_to_remove = []
        for grid_position, designs in designs_to_compare.items():
            if len(designs) > 1:
                design_to_keep = max(designs, key=designs.get)
                designs_to_remove.append([x for x in designs.keys() if x != design_to_keep])
        designs_to_remove = [item for sublist in designs_to_remove for item in sublist]
        if designs_to_remove != []:
             self.remove_dominated_entries(designs_to_remove)
        self.lvl_read = self.update_abstract_level(self.bb_lvl_read)
        self._previous_pf = [x for x in self.lvl_read.keys()]

    def remove_dominated_entries(self, entries):
        """
        Remove designs that do not contibute to the Pareto front (i.e. designs with HV values of 0)
        """
        for design in entries:
            self.log_debug('Removing core {}, no longer optimal'.format(design))
            self._pf_size -= 1
            self.write_to_bb(self.bb_lvl_write, design, self.lvl_read[design], remove=True)

    def clear_bb_lvl(self):
        remove = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                remove.append(core_name)
        self.remove_dominated_entries(remove)
        self.update_abstract_levels()
    

class KaBr_lvl2(KaBr):
    """Reads 'level 2' to determine if a core design is Pareto optimal for `level 1`."""
    def on_init(self):
        super().on_init()
        self.bb_lvl_write= 1
        self.bb_lvl_read = 2
        self._num_allowed_entries = 10
        self._trigger_val_base = 4
        self._fitness = 0.0
        self._class = 'reader_lvl2'
        self._update_hv = True
        
    def add_entry(self, core_name):
        self._entry_name = core_name[0]
        self._entry = {'pareto type': core_name[1], 'fitness function': self._fitness}
        
    def handler_executor(self, message):
        self.log_debug('Executing agent {}'.format(self.name)) 
        
        self.update_abstract_levels()
        self.clear_bb_lvl()
        #self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
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
        self.action_complete()
    
    def determine_fitness_function(self, core_name, core_objectives):
        """
        Calculate the total fitness function based on upper and lower limits.
        """
        fitness = 0
        for param, obj_dict in self._objectives.items():
            if (type(core_objectives[param]) == float) or (type(core_objectives[param]) == int):
                scaled_fit = self.scale_objective(core_objectives[param], obj_dict['ll'], obj_dict['ul'])
            elif type(core_objectives[param]) == list:
                scaled_fit = self.scale_list_objective(core_objectives[param], obj_dict['ll'], obj_dict['ul'], obj_dict['goal type'])
            try:
                fitness += scaled_fit if obj_dict['goal'] == 'gt' else (1-scaled_fit)
            except TypeError:
                fitness += 0

        return round(fitness, 5)

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
                
class KaBr_lvl3(KaBr):
    """Reads 'level 3' to determine if a core design is valid."""
    def on_init(self):
        super().on_init()
        self.bb_lvl_write = 2
        self.bb_lvl_read = 3
        self._trigger_val_base = 3
        self._class = 'reader_lvl3'


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
    
    def add_entry(self, core_name):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
        
    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        self.lvl_read =  self.update_abstract_level(self.bb_lvl_read, panels=[self.new_panel])
        self.lvl_write = self.update_abstract_level(self.bb_lvl_write, panels=[self.new_panel])
        self._lvl_data = self.lvl_read#self.update_abstract_level(self.bb_lvl_data, panels=[self.new_panel])#, self.old_panel])
