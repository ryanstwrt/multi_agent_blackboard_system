from mabs.ka.ka_s.base import KaLocal
import copy
import time
from numpy import random

class GeneticAlgorithm(KaLocal):
    """
    Pseudo-basic gentic algorithm for helping global and local searches
    """
     
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.previous_populations = {}
        self.crossover_rate = 0.8
        self.offspring_per_generation = 20
        self.mutation_rate = 0.1
        self.perturbation_size = 0.05
        self.crossover_type = 'single point'
        self.num_cross_over_points = 1
        self.mutation_type = 'random'
        self.pf_size = 40
        self.b = 2
        self.k = 5
        self.T = 100
        self._class = 'local search genetic algorithm'
        
    def handler_trigger_publish(self, message):
        """
        Read the BB level and determine if an entry is available.
        GA is currently triggered if we find that the PF level has solutions that it has not analyzed greater than some aribratry amount pf_size.
        
        Paremeters
        ----------
        message : str
            Required message from BB
        
        Returns
        -------
        send : message
            _trigger_response_alias : int
                Alias for the trigger response 
            name : str
                Alias for the agent, such that the trigger value get assigned to the right agent on the BB
            _trigger_val : int
                Trigger value for knowledge agent
        """
        lvl = message['level {}'.format(self.bb_lvl_read)]
        lvl = lvl if self.bb_lvl_read == 1 else {**lvl['new'], **lvl['old']}

        #self._trigger_val = self._base_trigger_val if len(new) - len(old) >= self.pf_size else 0
        if self.reanalyze_designs:
            self._trigger_val = self._base_trigger_val if len(lvl)  >= self.pf_size else 0
        else:
            new = set(list(lvl.keys()))
            old = set(list(self.analyzed_design.keys()))
            self._trigger_val = self._base_trigger_val if len(new) - len(old) >= self.pf_size else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        
    def search_method(self):
        """
        Search method for the GA is to perform crossover and mutation to generate new designs.
        
        Currently two crossover types are allowed: single-point and linear.
        Currently two mutation types are allowed: random and non-uniform.
        """
        population = list(self.lvl_read) if self.bb_lvl_read == 1 else list({**self.lvl_read['new'], **self.lvl_read['old']})
            
        children = []
        num_children = 0
        while num_children < self.offspring_per_generation:
            if len(population) < 2:
                break
            design1 = population.pop(random.choice(range(len(population))))
            design2 = population.pop(random.choice(range(len(population))))
            parent1 = self._lvl_data[design1]
            parent2 = self._lvl_data[design2]
            self.analyzed_design[design1] = {'Analyzed': True}
            self.analyzed_design[design2] = {'Analyzed': True}
            # Crosover to determine new children
            if self.crossover_type == 'single point':
                children = self.single_point_crossover(parent1, parent2, self.num_cross_over_points)
            elif self.crossover_type == 'linear crossover':
                children = self.linear_crossover(parent1, parent2)
            elif self.crossover_type == 'batch crossover':
                children = self.batch_crossover(parent1, parent2)
            else:
                self.log_warning('Warning: cross-over type {} is not implemented, reverting to `single-point` cross-over.'.format(self.crossover_rate))
                children = self.single_point_crossover(parent1, parent2, self.num_cross_over_points)

            # Determine if we mutate a child
            for child in children:
                if random.random() < self.mutation_rate:
                    if self.mutation_type == 'random':
                        child = self.random_mutation(child)
                    elif self.mutation_type == 'non-uniform':
                        child = self.non_uniform_mutation(child)
                    else:
                        self.log_warning('Warning: mutation type {} is not implemented, reverting to `random` mutation.'.format(self.mutation_type))
                        child = self.random_mutation(child)
                self.current_design_variables = child
                if self.determine_model_applicability(next(iter(child))):
                    if self.parallel:
                        self.parallel_executor()
                    else:
                        self.calc_objectives()
                        self.determine_write_to_bb()
                num_children += len(children)
                if self.kill_switch:
                    break
                
            if self.kill_switch:
                break
        if self.parallel:
            self.determine_parallel_complete()
                                      
            
    def single_point_crossover(self, genotype1, genotype2, num_crossover_points):
        """
        Single point crossover where we simply select a design variables and cross the two parents at that variable
        Paremeters:
        -----------
        genotype1 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        genotype2 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        Returns:
        --------
        c1 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c2 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        """
        # Prevent a null crossover
        crossover = 0
        while crossover == 0:
            crossover = random.choice(range(len(self._design_variables)))
        p1_dv = list(genotype1['design variables'].values())
        p2_dv = list(genotype2['design variables'].values())

        c1_dv = p1_dv[:crossover] + p2_dv[crossover:]
        c2_dv = p2_dv[:crossover] + p1_dv[crossover:]
        c1 = {dv:c1_dv[num] for num, dv in enumerate(self._design_variables.keys())}
        c2 = {dv:c2_dv[num] for num, dv in enumerate(self._design_variables.keys())}

        return [c1, c2]
    
    def linear_crossover(self, genotype1, genotype2):
        """
        Linear crossover for GA, where we take fractions of each design variable and sum them up to generate a new design variable
        
        Paremeters:
        -----------
        genotype1 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        genotype2 : dict
            dictionary of design to be mated, keys are design variable names, values are design variable values
        Returns:
        --------
        c1 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c2 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        c3 : dict
            dictionary of new design , keys are design variable names, values are design variable values
        """
        c1 = {}
        c2 = {}
        c3 = {}
        for dv, value in genotype1['design variables'].items():
            c1[dv] = round(0.5 * value + 0.5 * genotype2['design variables'][dv], self._design_accuracy)
            c2[dv] = round(1.5 * value - 0.5 * genotype2['design variables'][dv], self._design_accuracy)
            if c2[dv] > self._design_variables[dv]['ul']:
                c2[dv] = self._design_variables[dv]['ul']
            elif c2[dv] < self._design_variables[dv]['ll']:
                c2[dv] = self._design_variables[dv]['ll']
            c3[dv] = round(-0.5 * value + 1.5 * genotype2['design variables'][dv], self._design_accuracy)
            if c3[dv] > self._design_variables[dv]['ul']:
                c3[dv] = self._design_variables[dv]['ul']
            elif c3[dv] < self._design_variables[dv]['ll']:
                c3[dv] = self._design_variables[dv]['ll']
        return [c1, c2, c3]
    
    def batch_crossover(self, genotype1, genotype2):
        """
        Performa batch cross-over. Only used for Permutation type design variables.
        Implementation based on "Core loading pattern optimization of a typical two-loop 300 MWe PWR using Simulated Annealing (SA), novel crossover Genetic Algorithms (GA) and hybrid GA(SA) schemes" by A. Zameer et al.
        """

        c1 = copy.copy(genotype2['design variables'])
        for dv, dv_dict in self._design_variables.items(): 
            idx = range(len(dv_dict['permutation']))
            i1, i2 = random.choice(idx, size=2, replace=False)
            val1, val2 = genotype1['design variables'][dv][i1], genotype1['design variables'][dv][i2]
            if val1 != genotype2['design variables'][dv][i1] and val2 != genotype2['design variables'][dv][i2]:
                i3 = c1[dv].index(val1)
                i4 = c1[dv].index(val2)
                c1[dv][i1], c1[dv][i3] = c1[dv][i3], c1[dv][i1]
                c1[dv][i2], c1[dv][i4] = c1[dv][i4], c1[dv][i2]
        return [c1] 
    
    def random_mutation(self, genotype):
        """
        Perform a random mutation, take a DV and allow it to vary it within a small perturbation
        Paremeters:
        -----------
        genotype : dict
            dictionary of design to be mutated, keys are design variable names, values are design variable values
        Returns:
        --------
        genotype : dict
            dictionary of mutated design with one of the design variables changed within the perturbation size
        """
        dv_mutate = random.choice(list(self._design_variables.keys()))
        if 'options' in self._design_variables[dv_mutate]:
            options = copy.copy(self._design_variables[dv_mutate]['options'])
            options.remove(genotype[dv_mutate])
            genotype[dv_mutate] = str(random.choice(options))
        elif 'permutation' in self._design_variables[dv_mutate]:
            idx = range(len(self._design_variables[dv_mutate]['permutation']))
            i1, i2 = random.choice(idx, size=2, replace=False)
            genotype[dv_mutate][i1], genotype[dv_mutate][i2] = genotype[dv_mutate][i2], genotype[dv_mutate][i1]
        else:
            ll = genotype[dv_mutate]*(1-self.perturbation_size)
            ul = genotype[dv_mutate]*(1+self.perturbation_size)
            genotype[dv_mutate] = round(random.random() * (ul - ll) + ll, self._design_accuracy)
            # Check to make sure we don't violate upper/lower limits, if we do, set it to the limit.
            genotype[dv_mutate] = min(self._design_variables[dv_mutate]['ul'], genotype[dv_mutate])
            genotype[dv_mutate] = max(self._design_variables[dv_mutate]['ll'], genotype[dv_mutate])   
            
        return genotype
    
    def non_uniform_mutation(self, genotype):
        """
        Utilize Michalewicz's non-uniform mutation,
        
        For the following, assume a constant alpha as well
        Notes: For a constant k/T, smaller values of b lead to a larger distribution
               For a constant b, a smaller k/T ratio leads to a larger distribution
               
        Paremeters:
        -----------
        genotype : dict
            dictionary of design to be mutated, keys are design variable names, values are design variable values
        Returns:
        --------
        genotype : dict
            dictionary of mutated design with one of the dezign variables changed according to a non-uniform mutation
        """
        
        # can we update the k/T parameter as a function of hypervolume convergence?
        dv_mutate = random.choice([x for x in self._design_variables.keys()])
        mutation_direction = random.choice(['up', 'down'])
        
        alpha = random.random()
        exponent = (1 - self.k / self.T)**self.b
        delta_k = genotype[dv_mutate] * (1 - alpha**exponent)
        
        if mutation_direction == 'up':
            new_gene = genotype[dv_mutate] + delta_k
            genotype[dv_mutate] = round(min(new_gene, self._design_variables[dv_mutate]['ul']), self._design_accuracy)
        else:
            new_gene = genotype[dv_mutate] - delta_k
            genotype[dv_mutate] = round(max(new_gene, self._design_variables[dv_mutate]['ll']), self._design_accuracy)
        return genotype