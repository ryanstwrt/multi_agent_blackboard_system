import src.ka as ka
import src.performance_measure as pm
import src.utilities as utils
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
        self._class = 'reader'
        self.agent_time = 0
        self.agent_time = 0
        self._trigger_event = 0

    def action_complete(self):
        """
        Send a message to the BB indicating it's completed its action
        """
        self.send(self._complete_alias, (self.name, self.agent_time, self._trigger_event))
        
    def clear_entry(self):
        """Clear the KA entry"""
        self._entry = None
        self._entry_name = None
        
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
                if pareto_opt == None:
                    return (False, pareto_opt)
        return (True, pareto_opt)
    
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
    
    def clear_bb_lvl(self):
        move = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                move.append(core_name)
                self.move_entry(self.bb_lvl_read, core_name, core_entry, self.old_panel, self.new_panel)
        for core in move:
            self.lvl_read.pop(core)
                
    def remove_dominated_entries(self):
        pass

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
        elif pareto_optimal > 0:
            return 'weak'
        else:
            #Change this to 'domianted'
            return 
        
                
    def get_objective_value(self, core, obj):
        objective_value = self._lvl_data[core]['objective functions'][obj]
        goal = self._objectives[obj]['goal type'] if 'goal type' in self._objectives[obj] else None
        return utils.get_objective_value(objective_value, goal)

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
                level_obj.update(self.bb.get_blackboard()['level {}'.format(level_num)][panel])
        else:
            level_obj = self.bb.get_blackboard()['level {}'.format(level_num)]
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
        self._trigger_val_base = 6.00000000003
        self._pf_size = 1
        self._lower_objective_reference_point = None
        self._upper_objective_reference_point = None
        self._hvi_dict = {}
        self._lvl_data = {}
        self._designs_to_remove = []
        self._class = 'reader level 1'
        self.pf_increase = 1.25
        self.total_pf_size = 100
        self._previous_pf = None
        self.dci = False
        self.dci_div = None
        self._nadir_point = None
        self._ideal_point = None
        self.pareto_sorter = 'non-dominated'
        
    def handler_trigger_publish(self, message):
        self.lvl_read = message['level {}'.format(self.bb_lvl_read)]
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
        
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))

        self.lvl_read = message[1]['level {}'.format(self.bb_lvl_read)]
        self.lvl_write = self.lvl_read
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)        
        
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
        elif self.pareto_sorter == 'non-dominated':
            pass
        else:
            self.log_debug('Pareto Sorter ({}) not recognized, please select from `non-dominated`, `dci`, `hvi`, or `dci hvi`. Automatically selecting `non-dominated`'.format(self.pareto_sorter)) 
        self.clear_entry()
        self.agent_time = time.time() - t
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

    def calculate_hvi_contribution(self):
        pf = [x for x in self.lvl_read.keys()]
        scaled_pf = utils.scale_pareto_front(pf, self._objectives, self._lvl_data)

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
            
        # Place the PF in the DCI hypergrid
        goal = {}
        for obj_name, obj in self._objectives.items():
            if obj['goal'] == 'et':
                goal.update({obj_name: (obj['goal'], obj['target'])})
            else:
                goal.update({obj_name: obj['goal']})

        dci = pm.diversity_comparison_indicator(self._nadir_point, self._ideal_point, [pf], goal=goal, div=self.dci_div)
        dci.compute_dci(pf)
        dc = dci.dc
        
        designs_to_compare = {}
        for design_name in pf.keys():
            design_pos = dc[design_name]['grid position']
            if design_pos in designs_to_compare:
                designs_to_compare[design_pos].update({design_name: self.lvl_read[design_name]['fitness function']})
            else:
                designs_to_compare[dc[design_name]['grid position']] = {design_name: self.lvl_read[design_name]['fitness function']}
            
        designs_to_remove = []
        for grid_position, designs in designs_to_compare.items():
            if len(designs) > 1:
                design_to_keep = max(designs, key=designs.get)
                designs_to_remove.append([x for x in designs.keys() if x != design_to_keep])
        designs_to_remove = [item for sublist in designs_to_remove for item in sublist]
        if designs_to_remove != []:
             self.remove_dominated_entries(designs_to_remove)


    def remove_dominated_entries(self, entries):
        """
        Remove designs that do not contibute to the Pareto front (i.e. designs with HV values of 0)
        """
        for design in entries:
            self.log_debug('Removing core {}, no longer optimal'.format(design))
            self._pf_size -= 1
            self.write_to_bb(self.bb_lvl_write, design, self.lvl_read[design], remove=True)
            self.lvl_read.pop(design)

    def clear_bb_lvl(self):
        remove = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                remove.append(core_name)
        self.remove_dominated_entries(remove)    

class KaBr_lvl2(KaBr):
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
            return (1.0 - 2*abs(target - obj_val))
    
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
        self._trigger_val_base = 3.00000000001
        self._class = 'reader level 3'


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
        self._lvl_data = self.lvl_read

class KaBr_interBB(KaBr):
    """Reads BB Level and write results to secondary BB."""
    def on_init(self):
        super().on_init()
        self.bb_to_write = None
        self.bb_lvl_write = 3
        self.bb_lvl_read = 1
        self._trigger_val_base = 6.00000000001
        self._class = 'reader inter'
        self._entries_moved = []
        self._design_variables = None
        self._new_entry_format = {}

    def add_entry(self, core_name, entry):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name
        self._entry = entry
        
    def connect_bb_to_write(self, bb):
        """Connect the BB and writer message to the BB we want to write to"""
        bb_agent_addr = bb.get_attr('agent_addrs')
        bb_agent_addr[self.name] = {'trigger response': None, 'executor': None, 'shutdown':None, 'performing action': False, 'class': KaBr_interBB}
        bb.set_attr(agent_addrs=bb_agent_addr)
        self._new_entry_format = {'design variables': bb.get_attr('design_variables'),
                                  'objective functions': bb.get_attr('objectives'),
                                  'constraints': bb.get_attr('constraints')}
        
        self._writer_alias, self._writer_addr = bb.connect_writer(self.name)
        self.connect(self._writer_addr, alias=self._writer_alias)
        self.log_info('Agent {} connected writer to {}'.format(self.name, bb.get_attr('name')))
        
    def handler_executor(self, message):
        
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))

        self.lvl_read =  message[1]['level {}'.format(self.bb_lvl_read)]
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)        
        
        for entry_name in self.lvl_read.keys():
            self.clear_entry()
            if entry_name not in self._entries_moved:
                entry = self.format_entry(entry_name)
                self.add_entry(entry_name, entry)
                self.write_to_bb(self.bb_lvl_write, self._entry_name, self._entry, panel=self.new_panel)
                self._entries_moved.append(entry_name)

        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.action_complete()
        
    def format_entry(self, entry_name):
        """
        Transform the variables from the sub BB to allow them to be written to the master BB
        """
        design = self._lvl_data[entry_name]['design variables']
        design.update({k:v for k,v in self._lvl_data[entry_name]['objective functions'].items()})
        design.update({k:v for k,v in self._lvl_data[entry_name]['constraints'].items()})
        new_design = {}
        
        for k,v in self._new_entry_format.items():
            new_design[k] = {param: design[param] for param, val in v.items()}
            
        return new_design
        
            
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.lvl_read =  message['level {}'.format(self.bb_lvl_read)] 
        
        designs = [x for x in self.lvl_read.keys()]
        new_entry = set(designs).issubset(self._entries_moved)
        self._trigger_val = self._trigger_val_base if not new_entry else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))     
    