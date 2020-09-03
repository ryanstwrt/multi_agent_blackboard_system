import ka
import performance_measure as pm
import time

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
     #   write_read = []
      #  write_move = []
#        t1 = time.time()
        self.clear_bb_lvl()
 #       clear_bb_lvl = round(time.time() - t1,5)
        while self._entry_name:
            self.clear_entry()
  #          t2 = time.time()
            self.lvl_write = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl)]
            self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)][self.new_panel]
   #         write_read.append(round(time.time() - t2,5))
            
            if self.read_bb_lvl():
    #            t3 = time.time()
                self.write_to_bb(self.bb_lvl, self._entry_name, self._entry, panel=self.new_panel)
                entry = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]['new'][self._entry_name]
                self.move_entry(self.bb_lvl_read, self._entry_name, entry, self.old_panel, self.new_panel)      
       #         write_move.append(round(time.time() - t3,5))
        self._trigger_val = 0
        self.action_complete()
        #total = round(time.time() - t1,5)
       # print('Time to clear BB: {}'.format(clear_bb_lvl))
       # print('Time to make read/write: {} \n  total: {}'.format(write_read,sum(write_read)))
       # print('Time to read/move: {}'.format(sum(write_read)))
        #print('Time to make read/write: {} \n  total: {}'.format(write_read,sum(write_read)))
       # print('Time to write/move: {}'.format(sum(write_move)))
       # print('Time for total: {}'.format(total))
            
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
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel)
                    
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
        self.total_pf_size = 100
        self._previous_pf = None
        self.dci = False
        self.dci_div = None
        self._nadir_point = None
        self._ideal_point = None
        
    def handler_trigger_publish(self, message):
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        new_pf_size = len(self.lvl_read)
        
        self._trigger_val = self._trigger_val_base if new_pf_size > self._pf_size * self.pf_increase else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))

    def handler_executor(self, message):
        """
        The executor handler for KA-BR-lvl1 maintains the Pareto front.
        There are currently two methods for maintaining the blackboard; hyper volume indicator (HVI) and diversity comarison indicator (DCI) accelerate HVI
        
        HVI calculates the HVI contribution for each solution on the Pareto front and removes solutions which contribute little to the total hypervolume of the size of the Pareto fron ti greater than self.total_pf_size
        
        DCI accelerated HVI uses the DCI to remove solutions which are closeby to help increase the diversity of the Pareto front.
        """
        self.log_debug('Executing agent {}'.format(self.name)) 
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
        self._pf_size = len(self.lvl_read)
        self._hvi_dict = {}

        # Make sure this is okay for larger numbers of entries otherwise revert to old method
        for panel in self.bb.get_attr('abstract_lvls')['level 3'].values():
            self._lvl_data.update(panel)
        if self.dci:
            if self._previous_pf:
                self.calculate_dci()
                #self.calculate_hvi_contribution()
                if self._pf_size > self.total_pf_size:
                    self.calculate_hvi_contribution()
                    self.prune_pareto_front()
                self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
                self._previous_pf = [x for x in self.lvl_read.keys()]
            else:
                self._previous_pf = [x for x in self.lvl_read.keys()]
        else:
            self.calculate_hvi_contribution()
            if self._pf_size > self.total_pf_size:
                self.prune_pareto_front()
        self.clear_entry()
       # self.clear_data_levels()
        self.action_complete()
        
    def clear_data_levels(self):
        pf = [x for x in self.lvl_read.keys()]
        lvl2 = self.bb.get_attr('abstract_lvls')['level 2']['old']
        lvl3 = self.bb.get_attr('abstract_lvls')['level 3']['old']
        for core_name, entry in lvl2.items():
            if core_name in pf:
                pass
            else:
                self.write_to_bb(2, core_name, entry, remove=True)
        for core_name, entry in lvl3.items():
            if core_name in pf:
                pass
            else:
                self.write_to_bb(3, core_name, entry, remove=True)   
                

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
            for obj in self._objectives.keys():
                scaled_obj = self.scale_objective(self._lvl_data[x]['objective functions'][obj], self._objectives[obj]['ll'], self._objectives[obj]['ul'])
                design_objectives.append(scaled_obj if self._objectives[obj]['goal'] == 'lt' else (1.0-scaled_obj))
            scaled_pf.append(design_objectives)
        return scaled_pf

    def calculate_hvi_contribution(self):
        pf = [x for x in self.lvl_read.keys()]
        scaled_pf = self.scale_pareto_front(pf)
        self._previous_pf = pf
        # Get the HVI from the blackboard rather than calculating it
        hvi = self.calculate_hvi(scaled_pf) #self.bb.gt_attr('hv_list[-1]')
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
        designs_to_remove = []
                
        pf = {name: self._lvl_data[name]['objective functions'] for name in self.lvl_read.keys()}
        pf_old = {name: self._lvl_data[name]['objective functions'] for name in self._previous_pf}

        scaled_pf = self.scale_pareto_front([x for x in self.lvl_read.keys()])
        hvi = self.calculate_hvi(scaled_pf) #self.bb.gt_attr('hv_list[-1]')
        
        # Calculate DCI for new/old pareto front
        dci = pm.diversity_comparison_indicator(self._nadir_point, self._ideal_point, [pf,pf_old], div=self.dci_div)
        dci._grid_generator()
        dci.compute_dci(pf)
        dc_new = dci.dc

        dci.compute_dci(pf_old)
        dc_old = dci.dc
        designs_to_compare = []

        # Determine if old Pareto front is missing any grid positions
        # Determine if any point on the new Pareto front is dominated and remove it
        
        for new_pf_design_name, new_dci in dc_new.items():
            # Determine if we have two designs in the same hyperbox
            for old_pf_design_name, old_dci in dc_old.items():
                if ((new_pf_design_name != old_pf_design_name) and (new_dci == old_dci)) and ((old_pf_design_name, new_pf_design_name) not in designs_to_compare):
                    designs_to_compare.append((new_pf_design_name, old_pf_design_name))
            
            # Determine if any solutions are dominated and add them to the designs_to_remove list
            for new_pf_design_name_2 in dc_new.keys():
                if (new_pf_design_name != new_pf_design_name_2):
                    optimal =  self.determine_optimal_type(self._lvl_data[new_pf_design_name]['objective functions'], 
                                                           self._lvl_data[new_pf_design_name_2]['objective functions'])
                    designs_to_remove += [new_pf_design_name] if not optimal else []
        
        designs_to_compare = list(set(designs_to_compare))        
        
        scaled_pareto_fronts = {x: (self.scale_pareto_front([x[0]])[0], self.scale_pareto_front([x[1]])[0]) for x in designs_to_compare}
        # Examine the two solutions in hyperbox and determine which one to remove
        # Calcualte DCI for previous PF, and compare with current PF
        # If two solutions are in the same hyperbox, calculate the HVI contribution for each and remove lower one.
        for design_name, design in scaled_pareto_fronts.items():
            if (design_name[0] not in designs_to_remove) and (design_name[1] not in designs_to_remove):
                hvi_1 = hvi - self.calculate_hvi([dv for dv in scaled_pf if dv != design[0]])
                hvi_2 = hvi - self.calculate_hvi([dv for dv in scaled_pf if dv != design[1]])
                designs_to_remove += [design_name[1]] if hvi_1 > hvi_2 else [design_name[0]]

        designs_to_remove = list(set(designs_to_remove))
        if designs_to_remove != []:
             self.remove_dominated_entries(designs_to_remove)
        # We need to calculate the hyperbox that each solution is in, and then determine if a hyperbox is better than another one.
        self._previous_pf = [x for x in self.lvl_read.keys() if x not in designs_to_remove]
        self.lvl_read = self.bb.get_attr('abstract_lvls')['level {}'.format(self.bb_lvl_read)]
    
    def remove_dominated_entries(self, entries):
        """
        Remove designs that do not contibute to the Pareto front (i.e. designs with HV values of 0)
        """
        for design in entries:
            self.log_info('Removing core {}, no longer optimal'.format(design))
            self._pf_size -= 1
            self.write_to_bb(self.bb_lvl, design, self.lvl_read[design], remove=True)
            
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
        self._fitness = self.determine_fitness_function(core_name, self.lvl_data[core_name]['objective functions'])
        
        if self.lvl_write == {}:
            self.log_debug('Design {} is initial optimal design.'.format(core_name))
            return (True, 'pareto')
        pareto_opt = None
        for opt_core in self.lvl_write.keys():
            if opt_core != core_name:
                pareto_opt = self.determine_optimal_type(self.lvl_data[core_name]['objective functions'], 
                                                         self.lvl_data[opt_core]['objective functions'])
                if pareto_opt == None:
                    return (False, pareto_opt)
        return (True, pareto_opt)
    
    def determine_fitness_function(self, core_name, core_objectives):
        """
        Calculate the total fitness function based on upper and lower limits.
        """
        fitness = 0
        for param, obj_dict in self._objectives.items():
            scaled_fit = self.scale_objective(core_objectives[param], obj_dict['ll'], obj_dict['ul'])
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
            param = self.lvl_data[core_name]['objective functions'][param_name]
            if param < obj_dict['ll'] or param > obj_dict['ul']:
                return (False, None)
        return (True, None)
    
    def add_entry(self, core_name):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name[0]
        self._entry = {'valid': True}
