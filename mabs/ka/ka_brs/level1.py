from mabs.ka.ka_brs.base import KaBr
import mabs.utils.performance_measure as pm
import mabs.utils.utilities as utils
import time
import copy

class KaBrLevel1(KaBr):
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
        self._previous_pf = {}
        self.dci = False
        self.dci_div = None
        self._nadir_point = None
        self._ideal_point = None
        self.pareto_sorter = 'non-dominated'
        
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
        hvi = pm.hypervolume_indicator(pf, self._upper_objective_reference_point)
        return hvi    
    
    def calculate_dci(self):
        """
        Calculate the DCI for the new pareto front
        """
        pf = {name: {obj: self.get_objective_value(name, obj) for obj in self._objectives.keys()} for name in self.lvl_read.keys()}
            
        goal = {}
        #Convert our objectives to a minimization system
        for obj_name, obj in self._objectives.items():
            if obj['goal'] == 'et':
                goal.update({obj_name: (obj['goal'], obj['target'])})
            else:
                goal.update({obj_name: obj['goal']})

        # Place the PF in the DCI hypergrid
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

    def clear_bb_lvl(self):
        remove = []
        for core_name, core_entry in self.lvl_read.items():
            valid_core, opt_type = self.determine_validity(core_name)
            if not valid_core:
                remove.append(core_name)
        self.remove_dominated_entries(remove)  
        
    def handler_trigger_publish(self, message):
        self.lvl_read = message['level {}'.format(self.bb_lvl_read)]
        self.lvl_write = self.lvl_read
        new_pf_size = len(self.lvl_read)
        old_pf_size = len(self._previous_pf)
        
        self._trigger_val = self._trigger_val_base if new_pf_size > old_pf_size * self.pf_increase else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
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
        self._lvl_data = {**message[1]['level {}'.format(self.bb_lvl_data)]['new'], **message[1]['level {}'.format(self.bb_lvl_data)]['old']}     
        
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
        self._previous_pf = copy.copy(self.lvl_read)
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
        
    def remove_dominated_entries(self, entries):
        """
        Remove designs that do not contibute to the Pareto front (i.e. designs with HV values of 0)
        """
        for design in entries:
            self.log_debug('Removing core {}, no longer optimal'.format(design))
            self._pf_size -= 1
            self.write_to_bb(self.bb_lvl_write, design, self.lvl_read[design], remove=True)
            self.lvl_read.pop(design)

    def update_abstract_levels(self):
        """
        Update the KA's current understanding of the BB
        """
        self.lvl_read = self.update_abstract_level(self.bb_lvl_read)
        self.lvl_write = self.lvl_read
        self._lvl_data = self.update_abstract_level(self.bb_lvl_data, panels=[self.new_panel, self.old_panel])